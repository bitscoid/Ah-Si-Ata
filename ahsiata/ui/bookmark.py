"""Bookmark menu: list, open, delete favourite packages."""
from __future__ import annotations

from ahsiata.api.packages import get_family, get_package_details
from ahsiata.core.bookmark import BOOKMARK
from ahsiata.core.session import SESSION
from ahsiata.ui.package.details import show_package_details
from ahsiata.ui.style import C, p, title, rule, info, fail
from ahsiata.ui.utils import clear_screen, pause


def show_bookmark_menu() -> None:
    user = SESSION.get_active_user()
    if user is None:
        return
    api_key = SESSION.api_key
    tokens = user["tokens"]

    while True:
        clear_screen()
        bookmarks = BOOKMARK.get_bookmarks()
        print(rule(char="=", color=C.MAGENTA))
        print(title("⭐ Bookmark Paket", color=C.MAGENTA))
        print(rule(char="=", color=C.MAGENTA))
        if not bookmarks:
            print(info("Belum ada bookmark"))
        else:
            for idx, bm in enumerate(bookmarks, 1):
                print(f"{idx}. {p(bm['family_name'], C.BOLD)} - {bm['variant_name']} - {bm['option_name']}")
                print(rule(color=C.BLUE))
        print(rule(char="-", color=C.MAGENTA))
        print(p(f"{'':>3}  {'D':>2} Hapus    {'B':>2} Kembali", C.YELLOW))
        print(rule(char="-", color=C.MAGENTA))
        print()
        choice = input(p("🧭 Pilih : ", C.YELLOW)).strip()

        if choice.lower() == "b":
            return

        if choice.lower() == "d":
            if not bookmarks:
                pause()
                continue
            del_idx = input(p("🧭 Nomor urut hapus: ", C.BOLD))
            if not del_idx.isdigit() or not (1 <= int(del_idx) <= len(bookmarks)):
                print(fail("Nomor tidak valid"))
                pause()
                continue
            bm = bookmarks[int(del_idx) - 1]
            BOOKMARK.remove_bookmark(
                family_code=bm["family_code"],
                is_enterprise=bm["is_enterprise"],
                variant_name=bm["variant_name"],
                order=bm["order"],
            )
            pause()
            continue

        if not choice.isdigit() or not (1 <= int(choice) <= len(bookmarks)):
            print(fail("Pilihan salah"))
            pause()
            continue

        bm = bookmarks[int(choice) - 1]
        family_data = get_family(api_key, tokens, bm["family_code"], bm["is_enterprise"])
        if not family_data:
            print(fail("Gagal ambil data family"))
            pause()
            continue

        detail = get_package_details(
            api_key, tokens, bm["family_code"], bm["variant_name"], bm["order"], bm["is_enterprise"]
        )
        if detail:
            option_code = detail.get("package_option", {}).get("package_option_code", "")
            if option_code:
                show_package_details(api_key, tokens, option_code, bm["is_enterprise"])
