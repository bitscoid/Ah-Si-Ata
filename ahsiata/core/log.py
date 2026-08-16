"""Diagnostic logging to `ahsiata.log` (CWD) for tracking raw responses."""
from __future__ import annotations

from datetime import datetime

_LOG_PATH = "ahsiata.log"


def log(entry: str) -> None:
    """Append a timestamped line to the log file; never raise."""
    try:
        with open(_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().isoformat(timespec='seconds')}] {entry}\n")
    except OSError:
        pass