from __future__ import annotations

from datetime import date
from typing import List

from .config import SkillCategory
from .utils import CategoryPick, day_of_year, date_seed, stable_int_hash


def pick_daily_category(
    *,
    categories: List[SkillCategory],
    on_date: date,
    slot: int = 0,
) -> CategoryPick:
    """
    ყოველდღიური კატეგორიის როტაცია:
    - იყენებს day-of-year % len(categories) პრინციპს
    - slot პარამეტრი მომავალში გაძლევს საშუალებას დღეში რამდენიმე მესიჯი გააგზავნო
      (მაგ: slot=0 დილისთვის, slot=1 საღამოსთვის) და კატეგორია/კუთხე წინ წავიდეს.
    """
    if not categories:
        raise ValueError("categories must not be empty")

    doy = day_of_year(on_date)  # 1..366
    base_index = (doy - 1) % len(categories)  # 0..len-1
    index = (base_index + int(slot)) % len(categories)
    category = categories[index]

    seed = date_seed(on_date)
    angle_list = category.get("angles_ka") or []
    if angle_list:
        angle_index = stable_int_hash(f"{seed}|{category['id']}|{slot}") % len(angle_list)
        angle_ka = angle_list[angle_index]
    else:
        angle_index = 0
        angle_ka = ""

    return CategoryPick(
        category_id=category["id"],
        category_name_ka=category["name_ka"],
        angle_ka=angle_ka,
        index=index,
        angle_index=angle_index,
        seed=seed,
    )

