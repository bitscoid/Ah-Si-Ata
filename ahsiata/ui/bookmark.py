"""Bookmark menu: list, open, delete favourite packages."""
from __future__ import annotations

from ahsiata.api.packages import get_family, get_package_details
from ahsiata.core.bookmark import BOOKMARK
from ahsiata.core.session import SESSION
from ahsiata.ui.package.details import show_package_details
from ahsiata.ui.utils import clear_screen, pause


def show_bookmark_menu() -> None:
    user = SESSION.get_active_user()
    if user is None:
        return
    api_key = SESSION.api_key
    tokens = user["tokens"]

    in_menu = True
    while in_menu:
        clear_screen()
        bookmarks = BOOKMARK.get_bookmarks()
        print("=" * 55)
        print("Bookmark Paket".center(55))
        print("=" * 55)
        if not bookmarks:
            print("Belum ada bookmark.")
        else:
            for idx, bm in enumerate(bookmarks):
                print(f"{idx + 1}. {bm['family_name']} - {bm['variant_name']} - {bm['option_name']}")
                print("-" * 55)
        print("000. Hapus bookmark")
        print("00. Kembali")
        choice = input("Pilih paket (nomor): ")

        if choice == "00":
            in_menu = False
            return

        if choice == "000":
            if not bookmarks:
                pause()
                continue
            del_idx = input("Hapus nomor urut: ")
            if not del_idx.isdigit() or not (1 <= int(del_idx) <= len(bookmarks)):
                print("Nomor tidak valid.")
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
            print("Pilihan tidak valid.")
            pause()
            continue

        bm = bookmarks[int(choice) - 1]
        family_data = get_family(api_key, tokens, bm["family_code"], bm["is_enterprise"])
        if not family_data:
            print("Gagal mengambil data family.")
            pause()
            continue

        detail = get_package_details(
            api_key, tokens, bm["family_code"], bm["variant_name"], bm["order"], bm["is_enterprise"]
        )
        if detail:
            option_code = detail.get("package_option", {}).get("package_option_code", "")
            if option_code:
                show_package_details(api_key, tokens, option_code, bm["is_enterprise"])
