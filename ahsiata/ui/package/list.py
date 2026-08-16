"""Package list: list variants/options of a family + dispatch to detail."""
from __future__ import annotations

from ahsiata.api.packages import get_family
from ahsiata.core.session import SESSION
from ahsiata.ui.package.details import show_package_details
from ahsiata.ui.style import C, p as sp, rule, title, fail

from ahsiata.ui.utils import clear_screen, pause, format_price


def get_packages_by_family(
    family_code: str,
    is_enterprise: bool | None = None,
    migration_type: str | None = None,
) -> list[dict] | None:
    api_key = SESSION.api_key
    tokens = SESSION.get_active_tokens()
    if tokens is None:
        print(fail("Tidak ada token user aktif"))
        pause()
        return None

    data = get_family(api_key, tokens, family_code, is_enterprise, migration_type)
    if not data:
        print(fail("Gagal muat data family"))
        pause()
        return None

    price_currency = "Poin" if data["package_family"].get("rc_bonus_type") == "MYREWARDS" else "Rp"
    packages: list[dict] = []

    while True:
        clear_screen()
        print(rule(char="=", color=C.CYAN))
        print(title(f"📦 {data['package_family']['name']}", color=C.CYAN))
        print(rule(char="=", color=C.CYAN))
        print(f"🔢 Family Code: {family_code}")
        print(f"🏷 Tipe: {data['package_family']['package_family_type']}")
        print(f"📦 Varian: {len(data['package_variants'])}")
        print(rule(color=C.CYAN))
        print(sp("📋 Paket Tersedia:", C.BOLD, C.WHITE))
        print(rule(color=C.CYAN))

        option_number = 1
        for variant_idx, variant in enumerate(data["package_variants"], start=1):
            variant_name = variant["name"]
            variant_code = variant["package_variant_code"]
            print(sp(f"🔖 {variant_name}", C.BOLD, C.BLUE))
            print(f"   🔢 Kode: {variant_code}")
            for option in variant["package_options"]:
                packages.append({
                    "number": option_number,
                    "variant_name": variant_name,
                    "option_name": option["name"],
                    "price": option["price"],
                    "code": option["package_option_code"],
                    "option_order": option["order"],
                })
                print(f"   {option_number}. {sp(option['name'], C.WHITE)} - {sp(format_price(option['price']), C.BOLD, C.YELLOW)}")
                option_number += 1
            if variant_idx < len(data["package_variants"]):
                print(rule(color=C.CYAN))
        print(rule(char="-", color=C.CYAN))
        print(sp(f"{'':>3}  {'B':>2} Kembali", C.DIM))
        print()
        pkg_choice = input(sp("🧭 Pilih : ", C.YELLOW)).strip()

        if pkg_choice.lower() == "b":
            return packages
        if not pkg_choice.isdigit():
            print(fail("Input salah"))
            continue

        selected = next((p for p in packages if p["number"] == int(pkg_choice)), None)
        if not selected:
            print(fail("Paket tidak ada"))
            continue

        show_package_details(
            api_key, tokens, selected["code"], is_enterprise,
            option_order=selected["option_order"],
        )
