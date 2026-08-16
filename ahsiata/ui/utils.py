"""UI utility helpers: clear screen, pause, HTML→text, quota formatting."""
from __future__ import annotations

import os
import re
import textwrap
from html.parser import HTMLParser

from ahsiata.ui.style import C, p


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def pause() -> None:
    input(p("\n⏎ Lanjut…", C.WHITE))


class _HTMLToText(HTMLParser):
    def __init__(self, width: int = 80):
        super().__init__()
        self.width = width
        self.result: list[str] = []
        self.in_li = False

    def handle_starttag(self, tag, attrs):
        if tag == "li":
            self.in_li = True
        elif tag == "br":
            self.result.append("\n")

    def handle_endtag(self, tag):
        if tag == "li":
            self.in_li = False
            self.result.append("\n")

    def handle_data(self, data):
        text = data.strip()
        if text:
            if self.in_li:
                self.result.append(f"- {text}")
            else:
                self.result.append(text)

    def get_text(self) -> str:
        text = "".join(self.result)
        text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)
        return "\n".join(textwrap.wrap(text, width=self.width, replace_whitespace=False))


def display_html(html_text: str, width: int = 80) -> str:
    parser = _HTMLToText(width=width)
    parser.feed(html_text)
    return parser.get_text()


_GB = 1024 ** 3
_MB = 1024 ** 2
_KB = 1024


def format_quota_byte(quota_byte: int) -> str:
    if quota_byte >= _GB:
        return f"{quota_byte / _GB:.2f} GB"
    if quota_byte >= _MB:
        return f"{quota_byte / _MB:.2f} MB"
    if quota_byte >= _KB:
        return f"{quota_byte / _KB:.2f} KB"
    return f"{quota_byte} B"


def format_price(price: int | float | str) -> str:
    """Format price as 'Rp. 1.000' with dot thousand separator."""
    price_str = str(price)
    import re
    nums = re.sub(r"[^\d]", "", price_str)
    if not nums:
        return price_str
    try:
        return f"Rp. {int(nums):,}".replace(",", ".")
    except ValueError:
        return price_str
