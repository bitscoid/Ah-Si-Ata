"""Store search menu: family list and packages."""
from __future__ import annotations

from ahsiata.api.catalog import get_family_list, get_store_packages
from ahsiata.core.session import SESSION
from ahsiata.ui.package.details import show_package_details
from ahsiata.ui.package.list import get_packages_by_family
from ahsiata.ui.style import C, p, title, rule, fail
from ahsiata.ui.utils import clear_screen, pause


def show_family_list_menu(subs_type: str, is_enterprise: bool) -> None:
    api_key = SESSION.api_key
    tokens = SESSION.get_active_tokens()
    if tokens is None:
        return

    while True:
        clear_screen()
        print(rule(char="=", color=C.CYAN))
        print(title("🏬 Family List", color=C.CYAN))
        print(rule(char="=", color=C.CYAN))
        res = get_family_list(api_key, tokens, subs_type, is_enterprise)
        if not res:
            print(fail("Gagal mengambil daftar family."))
            pause()
            return

        families = res.get("data", {}).get("family_list", [])
        for idx, fam in enumerate(families, start=1):
            print(f"{idx}. 👨‍👩‍👧 {p(fam.get('family_name', 'N/A'), C.BOLD)}")
        print(rule(char="-", color=C.CYAN))
        print(p(f"{'':>3}  {'B':>2} Kembali", C.DIM))
        print()
        choice = input(p("🧭 Pilih : ", C.YELLOW)).strip()
        if choice.lower() == "b":
            return
        if not choice.isdigit() or not (1 <= int(choice) <= len(families)):
            print(fail("Pilihan tidak valid."))
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
        print(rule(char="=", color=C.CYAN))
        print(title("🛒 Store Packages", color=C.CYAN))
        print(rule(char="=", color=C.CYAN))
        res = get_store_packages(api_key, tokens, subs_type, is_enterprise)
        if not res:
            print(fail("Gagal mengambil paket."))
            pause()
            return

        packages = res.get("data", {}).get("results_price_only", [])
        for idx, pkg in enumerate(packages, start=1):
            price = pkg.get("discounted_price", pkg.get("price", "N/A"))
            name = pkg.get("package_name", pkg.get("name", "N/A"))
            print(f"{idx}. 📦 {p(name, C.BOLD)} - {p(str(price), C.BOLD, C.YELLOW)}")
        print(rule(char="-", color=C.CYAN))
        print(p(f"{'':>3}  {'B':>2} Kembali", C.DIM))
        print()
        choice = input(p("🧭 Pilih : ", C.YELLOW)).strip()
        if choice.lower() == "b":
            return
        if not choice.isdigit() or not (1 <= int(choice) <= len(packages)):
            print(fail("Pilihan tidak valid."))
            pause()
            continue
        selected = packages[int(choice) - 1]
        option_code = selected.get("package_option_code", "")
        if option_code:
            show_package_details(api_key, tokens, option_code, is_enterprise)
