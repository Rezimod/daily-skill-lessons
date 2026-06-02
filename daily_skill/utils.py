from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, date
import hashlib
from typing import Optional

import pytz


TBILISI_TZ = pytz.timezone("Asia/Tbilisi")


def get_tbilisi_now(now: Optional[datetime] = None) -> datetime:
    """
    აბრუნებს მიმდინარე დროს თბილისის დროით.
    - თუ now გადმოგეცა (timezone-aware ან naive), მოვიყვანთ თბილისის TZ-ში.
    """
    if now is None:
        return datetime.now(TBILISI_TZ)
    if now.tzinfo is None:
        return TBILISI_TZ.localize(now)
    return now.astimezone(TBILISI_TZ)


def day_of_year(d: date) -> int:
    """1-დან 366-მდე (leap year ჩათვლით)."""
    return int(d.strftime("%j"))


def date_seed(d: date) -> str:
    """სტაბილური დღიური seed, რომელიც prompt-ში ჩასაჯდომად გამოდგება."""
    return d.isoformat()  # YYYY-MM-DD


def stable_int_hash(text: str) -> int:
    """
    სტაბილური ჰეში (პითონის random hash-ისგან დამოუკიდებელი),
    რომ ყოველდღიური არჩევანი არ ‘იცვალოს’ სხვადასხვა გარემოში.
    """
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return int(digest[:16], 16)


def parse_iso_date(value: str) -> date:
    """მიღებს 'YYYY-MM-DD' და აბრუნებს date-ს; სხვა ფორმატზე აგდებს ValueError-ს."""
    return date.fromisoformat(value)


@dataclass(frozen=True)
class CategoryPick:
    category_id: str
    category_name_ka: str
    angle_ka: str
    index: int
    angle_index: int
    seed: str

