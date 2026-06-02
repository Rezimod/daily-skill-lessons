from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional

import httpx
from openai import OpenAI

from .config import SKILL_CATEGORIES, SkillCategory
from .prompt import build_prompt_ka
from .rotation import pick_daily_category
from .utils import get_tbilisi_now


@dataclass(frozen=True)
class GenerationInputs:
    """მომავალში მარტივად იფართოება (multi-message/day, A/B prompts, და ა.შ.)."""

    on_date: date
    slot: int = 0
    categories: Optional[list[SkillCategory]] = None


def generate_lesson_text(
    *,
    openai_api_key: str,
    model: str = "gpt-4o",
    inputs: Optional[GenerationInputs] = None,
    now: Optional[datetime] = None,
) -> str:
    """
    ძირითადი გენერატორი.
    - იღებს კატეგორიას როტაციით (date-based)
    - აწყობს prompt-ს category + seed + angle-ით
    - აბრუნებს ერთ დასრულებულ ტექსტს (ქართულად, <600 სიტყვა)
    """
    if not openai_api_key:
        raise ValueError("openai_api_key is required")

    t_now = get_tbilisi_now(now)
    on_date = (inputs.on_date if inputs is not None else t_now.date())
    slot = (inputs.slot if inputs is not None else 0)
    categories = (inputs.categories if inputs and inputs.categories is not None else SKILL_CATEGORIES)

    pick = pick_daily_category(categories=categories, on_date=on_date, slot=slot)
    prompt = build_prompt_ka(pick)

    http_client = httpx.Client()
    try:
        client = OpenAI(api_key=openai_api_key, http_client=http_client)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "შენ ხარ პრაქტიკული უნარების ინსტრუქტორი. "
                        "წერ ძალიან კონკრეტულ, ტაქტიკურ გაკვეთილებს ქართულად. "
                        "შენ მიერ დაწერილი ტექსტი პირდაპირ იგზავნება Telegram-ში."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.9,
            max_tokens=900,
        )
        content = (response.choices[0].message.content or "").strip()
        return content
    finally:
        http_client.close()


def generate_daily_lesson_text(
    *,
    openai_api_key: str,
    model: str = "gpt-4o",
    slot: int = 0,
    on_date: Optional[date] = None,
    now: Optional[datetime] = None,
) -> str:
    """
    მარტივი wrapper ყოველდღიური გაგზავნისთვის.
    Telegram სკრიპტიდან ერთ ხაზში გამოსაყენებლად.
    """
    t_now = get_tbilisi_now(now)
    return generate_lesson_text(
        openai_api_key=openai_api_key,
        model=model,
        inputs=GenerationInputs(on_date=on_date or t_now.date(), slot=slot),
        now=now,
    )

