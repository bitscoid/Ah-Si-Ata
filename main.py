"""Ah-Si-Ata CLI entry point.

Thin wrapper for the historical launch path (`python main.py`).
The real entry lives in `ahsiata.cli` (also `python -m ahsiata` and the
`ahsiata` console script from pyproject.toml).
"""
from ahsiata.cli import main

if __name__ == "__main__":
    main()