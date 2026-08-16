"""Store segments menu: browse categories, pick package."""
from __future__ import annotations

from ahsiata.api.catalog import get_segments
from ahsiata.core.session import SESSION
from ahsiata.ui.style import C, p, title, rule, info, fail
from ahsiata.ui.utils import clear_screen, pause, format_price

WIDTH = 55


def show_store_segments_menu(is_enterprise: bool) -> None:
    api_key = SESSION.api_key
    tokens = SESSION.get_active_tokens()
    if tokens is None:
        return

    while True:
        clear_screen()
        print(rule(char="=", color=C.CYAN))
        print(title("🏬 Promo", color=C.CYAN))
        print(rule(char="=", color=C.CYAN))
        segments_data = get_segments(api_key, tokens, is_enterprise)
        if not segments_data:
            print(fail("Tidak ada segmen ditemukan."))
            pause()
            return

        segments = segments_data.get("data", {}).get("store_segments", [])
        if not segments:
            print(fail("Tidak ada segmen ditemukan."))
            pause()
            return

        for seg_idx, seg in enumerate(segments):
            letter = chr(ord("A") + seg_idx)
            print(f"{letter}. {p(seg.get('title', ''), C.BOLD, C.WHITE)}")
            for j, banner in enumerate(seg.get("banners", []), start=1):
                price = banner.get("discounted_price")
                price_text = format_price(price) if isinstance(price, (int, float)) else ""
                line = f"   {letter.lower()}{j}. {p(banner.get('title', ''), C.CYAN)}"
                if price_text:
                    line += p(f" ({price_text})", C.YELLOW)
                print(line)
            print(rule(color=C.CYAN))

        print(rule(char="-", color=C.CYAN))
        print(p(f"{'':>3}  {'B':>2} Kembali", C.YELLOW))
        print(rule(char="-", color=C.CYAN))
        print()
        choice = input(p("🧭 Pilih : ", C.YELLOW)).strip()
        if choice.lower() == "b":
            return
        # Parse "<letter><number>"
        if len(choice) < 2 or not choice[0].isalpha() or not choice[1:].isdigit():
            print(fail("Pilihan tidak valid."))
            pause()
            continue
        seg_idx = ord(choice[0].upper()) - ord("A")
        banner_idx = int(choice[1:]) - 1
        if not (0 <= seg_idx < len(segments)):
            print(fail("Pilihan tidak valid."))
            pause()
            continue
        banners = segments[seg_idx].get("banners", [])
        if not (0 <= banner_idx < len(banners)):
            print(fail("Pilihan tidak valid."))
            pause()
            continue
        # Banner action → show package PDP detail via its option code.
        from ahsiata.ui.package.details import show_package_details
        option_code = banners[banner_idx].get("action_param", "")
        if option_code:
            show_package_details(api_key, tokens, option_code, False)
