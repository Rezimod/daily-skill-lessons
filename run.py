#!/usr/bin/env python3
"""Learning Hub — Georgian skill micro-lessons + financial lessons."""

from __future__ import annotations

import os
import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main() -> None:
    job = os.getenv("JOB", "").strip()
    if job == "skill_lesson":
        runpy.run_path(str(ROOT / "jobs" / "skill_lesson.py"), run_name="__main__")
    elif job == "financial_lesson":
        runpy.run_path(str(ROOT / "jobs" / "financial" / "lesson.py"), run_name="__main__")
    else:
        raise SystemExit("Set JOB to: skill_lesson, financial_lesson")


if __name__ == "__main__":
    main()
