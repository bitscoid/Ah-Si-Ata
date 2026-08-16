"""Package list: list variants/options of a family + dispatch to detail."""
from __future__ import annotations

from ahsiata.api.packages import get_family
from ahsiata.core.session import SESSION
from ahsiata.ui.package.details import show_package_details
from ahsiata.ui.utils import clear_screen, pause


def get_packages_by_family(
    family_code: str,
    is_enterprise: bool | None = None,
    migration_type: str | None = None,
) -> list[dict] | None:
    api_key = SESSION.api_key
    tokens = SESSION.get_active_tokens()
    if tokens is None:
        print("No active user tokens found.")
        pause()
        return None

    data = get_family(api_key, tokens, family_code, is_enterprise, migration_type)
    if not data:
        print("Failed to load family data.")
        pause()
        return None

    price_currency = "Poin" if data["package_family"].get("rc_bonus_type") == "MYREWARDS" else "Rp"
    packages: list[dict] = []

    while True:
        clear_screen()
        print("-------------------------------------------------------")
        print(f"Family Name: {data['package_family']['name']}")
        print(f"Family Code: {family_code}")
        print(f"Family Type: {data['package_family']['package_family_type']}")
        print(f"Variant Count: {len(data['package_variants'])}")
        print("-------------------------------------------------------")
        print("Paket Tersedia")
        print("-------------------------------------------------------")

        option_number = 1
        for variant_idx, variant in enumerate(data["package_variants"], start=1):
            variant_name = variant["name"]
            variant_code = variant["package_variant_code"]
            print(f" Variant {variant_idx}: {variant_name}")
            print(f" Code: {variant_code}")
            for option in variant["package_options"]:
                packages.append({
                    "number": option_number,
                    "variant_name": variant_name,
                    "option_name": option["name"],
                    "price": option["price"],
                    "code": option["package_option_code"],
                    "option_order": option["order"],
                })
                print(f"   {option_number}. {option['name']} - {price_currency} {option['price']}")
                option_number += 1
            if variant_idx < len(data["package_variants"]):
                print("-------------------------------------------------------")
        print("-------------------------------------------------------")
        print("00. Kembali ke menu utama")
        print("-------------------------------------------------------")
        pkg_choice = input("Pilih paket (nomor): ").strip()

        if pkg_choice == "00":
            return packages
        if not pkg_choice.isdigit():
            print("Input tidak valid.")
            continue

        selected = next((p for p in packages if p["number"] == int(pkg_choice)), None)
        if not selected:
            print("Paket tidak ditemukan.")
            continue

        show_package_details(
            api_key, tokens, selected["code"], is_enterprise,
            option_order=selected["option_order"],
        )
