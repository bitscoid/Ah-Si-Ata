"""Store segments menu: browse categories, pick package."""
from __future__ import annotations

from ahsiata.api.catalog import get_segments
from ahsiata.core.session import SESSION
from ahsiata.ui.utils import clear_screen, pause

WIDTH = 55


def show_store_segments_menu(is_enterprise: bool) -> None:
    api_key = SESSION.api_key
    tokens = SESSION.get_active_tokens()
    if tokens is None:
        return

    while True:
        clear_screen()
        print("=" * WIDTH)
        print("Store Segments".center(WIDTH))
        print("=" * WIDTH)
        print("Mengambil segments toko...")
        segments_data = get_segments(api_key, tokens, is_enterprise)
        if not segments_data:
            print("Tidak ada segments ditemukan.")
            pause()
            return

        banner_packages = segments_data.get("data", {}).get("packages", [])
        if not banner_packages:
            print("Tidak ada segments ditemukan.")
            pause()
            return

        for letter_idx, banner in enumerate(banner_packages):
            letter = chr(ord("A") + letter_idx)
            print(f"{letter}. Banner: {banner.get('name', 'N/A')}")
            for j, pkg in enumerate(banner.get("packages", []), start=1):
                print(f"   {letter.lower()}{j}. {pkg.get('name', 'N/A')}")
            print("-" * WIDTH)

        print("00. Kembali ke menu utama")
        choice = input("Masukkan pilihan Anda untuk melihat detail paket (mis. A1, B2): ").strip()
        if choice == "00":
            return
        # Parse "<letter><number>"
        if len(choice) < 2 or not choice[0].isalpha() or not choice[1:].isdigit():
            print("Pilihan tidak valid.")
            pause()
            continue
        letter_idx = ord(choice[0].upper()) - ord("A")
        pkg_idx = int(choice[1:]) - 1
        if not (0 <= letter_idx < len(banner_packages)):
            print("Pilihan tidak valid.")
            pause()
            continue
        banner = banner_packages[letter_idx]
        packages = banner.get("packages", [])
        if not (0 <= pkg_idx < len(packages)):
            print("Pilihan tidak valid.")
            pause()
            continue
        # PLP action would fetch packages; PDP would show detail; both are no-op stubs here.
        # The original menu called `get_package_details` directly on the option code.
        from ahsiata.ui.package.details import show_package_details
        option_code = packages[pkg_idx].get("package_option_code", "")
        if option_code:
            show_package_details(api_key, tokens, option_code, False)
