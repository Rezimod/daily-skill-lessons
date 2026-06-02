#!/usr/bin/env python3
"""Learning Hub — Georgian skill micro-lessons + financial lessons."""

from __future__ import annotations

import os
import runpy
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def _run_script(relative: str) -> None:
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    os.chdir(ROOT)
    runpy.run_path(str(ROOT / relative), run_name="__main__")


def main() -> None:
    job = os.getenv("JOB", "").strip()
    try:
        if job == "skill_lesson":
            _run_script("jobs/skill_lesson.py")
        elif job == "financial_lesson":
            _run_script("jobs/financial/lesson.py")
        else:
            raise SystemExit("Set JOB to: skill_lesson, financial_lesson")
    except SystemExit:
        raise
    except Exception:
        traceback.print_exc()
        raise SystemExit(1)


if __name__ == "__main__":
    main()
