"""Store search menu: family list and packages."""
from __future__ import annotations

from ahsiata.api.catalog import get_family_list, get_store_packages
from ahsiata.core.session import SESSION
from ahsiata.ui.package.details import show_package_details
from ahsiata.ui.package.list import get_packages_by_family
from ahsiata.ui.style import C, p, title, rule, fail, disp_w
from ahsiata.ui.utils import clear_screen, pause, format_price


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

        families = res.get("data", {}).get("results", [])
        cells = [f"{idx}. 👨 {p(fam.get('label', ''), C.BOLD)}" for idx, fam in enumerate(families, start=1)]
        half = (len(cells) + 1) // 2
        col_w = max((disp_w(c) for c in cells[:half]), default=0) + 2
        for i in range(half):
            left = cells[i]
            right = cells[i + half] if i + half < len(cells) else ""
            print(left + " " * max(col_w - disp_w(left), 0) + right)
        print(rule(char="-", color=C.CYAN))
        print(p(f"{'':>3}  {'B':>2} Kembali", C.YELLOW))
        print(rule(char="-", color=C.CYAN))
        print()
        choice = input(p("🧭 Pilih : ", C.YELLOW)).strip()
        if choice.lower() == "b":
            return
        if not choice.isdigit() or not (1 <= int(choice) <= len(families)):
            print(fail("Pilihan tidak valid."))
            pause()
            continue
        selected = families[int(choice) - 1]
        get_packages_by_family(selected.get("id", ""), is_enterprise)


def show_store_packages_menu(subs_type: str, is_enterprise: bool) -> None:
    api_key = SESSION.api_key
    tokens = SESSION.get_active_tokens()
    if tokens is None:
        return

    res = get_store_packages(api_key, tokens, subs_type, is_enterprise)
    if not res:
        print(fail("Gagal mengambil paket."))
        pause()
        return
    packages = res.get("data", {}).get("results_price_only", [])
    if not packages:
        print(fail("Tidak ada paket."))
        pause()
        return

    page_size = 15
    total_pages = (len(packages) + page_size - 1) // page_size
    page = 0
    while True:
        clear_screen()
        print(rule(char="=", color=C.CYAN))
        print(title(f"🛒 Store Packages ({len(packages)})", color=C.CYAN))
        print(rule(char="=", color=C.CYAN))

        items = packages[page * page_size:(page + 1) * page_size]
        for idx, pkg in enumerate(items, start=1):
            price = pkg.get("discounted_price", pkg.get("price", 0))
            name = pkg.get("title", pkg.get("package_name", pkg.get("name", "")))
            print(f"{idx}. 📦 {p(name, C.BOLD)} - {p(format_price(price), C.BOLD, C.YELLOW)}")

        print(rule(char="-", color=C.CYAN))
        nav = f"{'':>3}  {'N':>2} Next  {'P':>2} Prev  {'B':>2} Kembali"
        print(p(nav, C.YELLOW) + p(f"  | Hal {page + 1}/{total_pages}", C.DIM))
        print(rule(char="-", color=C.CYAN))
        print()
        choice = input(p("🧭 Pilih : ", C.YELLOW)).strip().lower()
        if choice == "b":
            return
        if choice == "n":
            page = (page + 1) % total_pages
            continue
        if choice == "p":
            page = (page - 1) % total_pages
            continue
        if not choice.isdigit() or not (1 <= int(choice) <= len(items)):
            print(fail("Pilihan tidak valid."))
            pause()
            continue
        selected = items[int(choice) - 1]
        option_code = selected.get("package_option_code", "")
        if option_code:
            show_package_details(api_key, tokens, option_code, is_enterprise)
