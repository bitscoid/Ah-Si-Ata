"""Store search menu: family list and packages."""
from __future__ import annotations

from ahsiata.api.catalog import get_family_list, get_store_packages
from ahsiata.core.session import SESSION
from ahsiata.ui.package.details import show_package_details
from ahsiata.ui.package.list import get_packages_by_family
from ahsiata.ui.utils import clear_screen, pause


def show_family_list_menu(subs_type: str, is_enterprise: bool) -> None:
    api_key = SESSION.api_key
    tokens = SESSION.get_active_tokens()
    if tokens is None:
        return

    while True:
        clear_screen()
        print("=" * 55)
        print("Store Family List".center(55))
        print("=" * 55)
        res = get_family_list(api_key, tokens, subs_type, is_enterprise)
        if not res:
            print("Gagal mengambil daftar family.")
            pause()
            return

        families = res.get("data", {}).get("family_list", [])
        for idx, fam in enumerate(families, start=1):
            print(f"{idx}. {fam.get('family_name', 'N/A')}")
        print("-" * 55)
        print("00. Kembali ke menu utama")
        choice = input("Pilih family (nomor): ").strip()
        if choice == "00":
            return
        if not choice.isdigit() or not (1 <= int(choice) <= len(families)):
            print("Pilihan tidak valid.")
            pause()
            continue
        selected = families[int(choice) - 1]
        get_packages_by_family(selected.get("family_code", ""), is_enterprise)


def show_store_packages_menu(subs_type: str, is_enterprise: bool) -> None:
    api_key = SESSION.api_key
    tokens = SESSION.get_active_tokens()
    if tokens is None:
        return

    while True:
        clear_screen()
        print("=" * 55)
        print("Store Packages".center(55))
        print("=" * 55)
        res = get_store_packages(api_key, tokens, subs_type, is_enterprise)
        if not res:
            print("Gagal mengambil paket.")
            pause()
            return

        packages = res.get("data", {}).get("results_price_only", [])
        for idx, pkg in enumerate(packages, start=1):
            price = pkg.get("discounted_price", pkg.get("price", "N/A"))
            print(f"{idx}. {pkg.get('package_name', pkg.get('name', 'N/A'))} - {price}")
        print("-" * 55)
        print("00. Kembali ke menu utama")
        choice = input("Pilih paket (nomor): ").strip()
        if choice == "00":
            return
        if not choice.isdigit() or not (1 <= int(choice) <= len(packages)):
            print("Pilihan tidak valid.")
            pause()
            continue
        selected = packages[int(choice) - 1]
        option_code = selected.get("package_option_code", "")
        if option_code:
            show_package_details(api_key, tokens, option_code, is_enterprise)
