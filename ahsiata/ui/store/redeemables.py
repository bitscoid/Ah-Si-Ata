"""Store redeemables menu (typo-free: was `redemables.py` in old layout)."""
from __future__ import annotations

from ahsiata.api.catalog import get_redeemables
from ahsiata.core.session import SESSION
from ahsiata.ui.package.details import show_package_details
from ahsiata.ui.package.list import get_packages_by_family
from ahsiata.ui.style import C, p, title, rule, info, fail
from ahsiata.ui.utils import clear_screen, pause

WIDTH = 55


def show_redeemables_menu(is_enterprise: bool) -> None:
    api_key = SESSION.api_key
    tokens = SESSION.get_active_tokens()
    if tokens is None:
        return

    while True:
        clear_screen()
        print(rule(char="=", color=C.YELLOW))
        print(title("🎁 Redeemables", color=C.YELLOW))
        print(rule(char="=", color=C.YELLOW))
        res = get_redeemables(api_key, tokens, is_enterprise)
        if not res:
            print(fail("Gagal mengambil redeemable."))
            pause()
            return

        categories = res.get("data", {}).get("categories", [])
        if not categories:
            print(info("Tidak ada kategori"))
            pause()
            return

        for letter_idx, cat in enumerate(categories):
            letter = chr(ord("A") + letter_idx)
            print(f"{letter}. 🏷 {p(cat.get('name', 'N/A'), C.BOLD, C.WHITE)}")
            for j, pkg in enumerate(cat.get("packages", []), start=1):
                print(f"   {letter.lower()}{j}. {p(pkg.get('name', 'N/A'), C.CYAN)}")
            print(rule())

        print(rule(char="-", color=C.YELLOW))
        print(p(f"{'':>3}  {'B':>2} Kembali", C.DIM))
        print()
        choice = input(p("🧭 Pilih: ", C.YELLOW)).strip()
        if choice.lower() == "b":
            return
        if len(choice) < 2 or not choice[0].isalpha() or not choice[1:].isdigit():
            print(fail("Pilihan tidak valid."))
            pause()
            continue
        letter_idx = ord(choice[0].upper()) - ord("A")
        pkg_idx = int(choice[1:]) - 1
        if not (0 <= letter_idx < len(categories)):
            print(fail("Pilihan tidak valid."))
            pause()
            continue
        category = categories[letter_idx]
        packages = category.get("packages", [])
        if not (0 <= pkg_idx < len(packages)):
            print(fail("Pilihan tidak valid."))
            pause()
            continue
        selected = packages[pkg_idx]
        action = selected.get("action_type", "")
        param = selected.get("action_param", "")
        if action == "PLP":
            get_packages_by_family(param)
        elif action == "PDP":
            show_package_details(api_key, tokens, param, False)
        else:
            print(fail(f"Tipe aksi yang tidak ditangani: {action}"))
            pause()
