"""Store redeemables menu (typo-free: was `redemables.py` in old layout)."""
from __future__ import annotations

from ahsiata.api.catalog import get_redeemables
from ahsiata.core.session import SESSION
from ahsiata.ui.package.details import show_package_details
from ahsiata.ui.package.list import get_packages_by_family
from ahsiata.ui.utils import clear_screen, pause

WIDTH = 55


def show_redeemables_menu(is_enterprise: bool) -> None:
    api_key = SESSION.api_key
    tokens = SESSION.get_active_tokens()
    if tokens is None:
        return

    while True:
        clear_screen()
        print("=" * WIDTH)
        print("Redeemables".center(WIDTH))
        print("=" * WIDTH)
        res = get_redeemables(api_key, tokens, is_enterprise)
        if not res:
            print("Failed to fetch redeemables.")
            pause()
            return

        categories = res.get("data", {}).get("categories", [])
        if not categories:
            print("No categories.")
            pause()
            return

        for letter_idx, cat in enumerate(categories):
            letter = chr(ord("A") + letter_idx)
            print(f"{letter}. Category: {cat.get('name', 'N/A')}")
            for j, pkg in enumerate(cat.get("packages", []), start=1):
                print(f"   {letter.lower()}{j}. {pkg.get('name', 'N/A')}")
            print("-" * WIDTH)

        print("00. Back to Main Menu")
        choice = input("Enter your choice to view package details (e.g., A1, B2): ").strip()
        if choice == "00":
            return
        if len(choice) < 2 or not choice[0].isalpha() or not choice[1:].isdigit():
            print("Invalid choice.")
            pause()
            continue
        letter_idx = ord(choice[0].upper()) - ord("A")
        pkg_idx = int(choice[1:]) - 1
        if not (0 <= letter_idx < len(categories)):
            print("Invalid choice.")
            pause()
            continue
        category = categories[letter_idx]
        packages = category.get("packages", [])
        if not (0 <= pkg_idx < len(packages)):
            print("Invalid choice.")
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
            print(f"Unhandled action type: {action}")
            pause()
