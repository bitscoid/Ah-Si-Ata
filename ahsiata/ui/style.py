"""ANSI color + emoji helpers for the terminal UI.

Usage:
    from ahsiata.ui.style import C, p, title, rule, center, ok, fail, warn, info
    print(title("📦 Paket Saya"))
    print(p("Saldo: Rp 5.000", C.BOLD, C.GREEN))
"""
from __future__ import annotations

import os
import unicodedata

# Enable ANSI/VT processing on Windows consoles; no-op elsewhere.
if os.name == "nt":
    os.system("")


class C:
    """ANSI escape codes."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    B_RED = "\033[91m"
    B_GREEN = "\033[92m"
    B_YELLOW = "\033[93m"
    B_BLUE = "\033[94m"
    B_MAGENTA = "\033[95m"
    B_CYAN = "\033[96m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_CYAN = "\033[46m"


def p(text, *codes):
    """Wrap text in ANSI codes; plain str when no codes given."""
    return f"{''.join(codes)}{text}{C.RESET}" if codes else str(text)


def disp_w(s: str) -> int:
    """Terminal display width; emoji/CJK count double."""
    return sum(2 if unicodedata.east_asian_width(ch) in "WF" else 1 for ch in s)


def center(text: str, width: int) -> str:
    """Center text accounting for emoji/CJK width."""
    pad = max(width - disp_w(text), 0)
    return " " * (pad // 2) + text + " " * (pad - pad // 2)


def title(text: str, char: str = "=", color: str = C.CYAN, width: int = 55) -> str:
    """Colored centered banner: `===== Text =====`."""
    inner = center(f" {text} ", width)
    return p(inner, color) if color else inner


def rule(char: str = "-", color: str = "", width: int = 55) -> str:
    """Horizontal line."""
    line = char * width
    return p(line, color) if color else line


def ok(msg: str) -> str:
    return p(f"✅ {msg}", C.GREEN)


def fail(msg: str) -> str:
    return p(f"❌ {msg}", C.RED)


def warn(msg: str) -> str:
    return p(f"⚠️ {msg}", C.YELLOW)


def info(msg: str) -> str:
    return p(f"ℹ️ {msg}", C.CYAN)