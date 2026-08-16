"""HOT packages menu (preset JSON of favourite deals).

Single merged menu: regular HOT packages (hot.json) + HOT bundles (hot2.json).
"""
from __future__ import annotations

import json

from ahsiata.api.packages import get_family, get_package_details
from ahsiata.api.purchase.balance import settlement_balance
from ahsiata.api.purchase.ewallet import show_multipayment
from ahsiata.api.purchase.qris import show_qris_payment
from ahsiata.core.session import SESSION
from ahsiata.type_dict import PaymentItem
from ahsiata.ui.package.details import show_package_details
from ahsiata.ui.style import C, p as sp, title as tt, rule, fail, warn

from ahsiata.ui.utils import clear_screen, format_quota_byte, pause

WIDTH = 55


def _buy_bundle(api_key: str, tokens: dict, selected: dict) -> None:
    """Resolve bundle packages, show detail, run the payment loop."""
    packages = selected.get("packages", [])
    if not packages:
        print(fail("Paket tidak tersedia"))
        pause()
        return

    payment_items: list[PaymentItem] = []
    main_detail = None
    for package in packages:
        detail = get_package_details(
            api_key, tokens,
            package["family_code"], package["variant_code"], package["order"],
            package["is_enterprise"], package["migration_type"],
        )
        if not detail:
            print(fail(f"Gagal ambil detail {package['family_code']}"))
            return
        if package is packages[0]:
            main_detail = detail
        payment_items.append(PaymentItem(
            item_code=detail["package_option"]["package_option_code"],
            product_type="",
            item_price=detail["package_option"]["price"],
            item_name=detail["package_option"]["name"],
            tax=0,
            token_confirmation=detail["token_confirmation"],
        ))

    if main_detail is None:
        return

    clear_screen()
    price = main_detail["package_option"]["price"]
    validity = main_detail["package_option"]["validity"]
    payment_for = main_detail["package_family"]["payment_for"]
    title = (
        f"{main_detail.get('package_family', {}).get('name', '')}"
        f" - {main_detail.get('package_detail_variant', {}).get('name', '')}"
        f" - {main_detail.get('package_option', {}).get('name', '')}"
    ).strip()
    parent_code = main_detail.get("package_addon", {}).get("parent_code", "") or "N/A"
    family_code = main_detail.get("package_family", {}).get("package_family_code", "")

    print(rule(char="=", color=C.CYAN))
    print(sp(f"📦 {selected['name']}", C.BOLD, C.WHITE))
    print(sp(f"   💰 {selected['price']}", C.YELLOW))
    print(f"   📄 Detail: {selected['detail']}")
    print(rule(char="=", color=C.CYAN))
    print(f"📦 Nama: {sp(title, C.BOLD, C.WHITE)}")
    print(f"💰 Harga: {sp(f'Rp {price}', C.BOLD, C.GREEN)}")
    print(f"💳 Pembayaran: {payment_for}")
    print(f"⏳ Masa Aktif: {validity}")
    print(f"⭐ Point: {main_detail['package_option']['point']}")
    print(f"🏷 Plan: {main_detail['package_family']['plan_type']}")
    print(rule(color=C.CYAN))
    print(f"🔢 Family Code: {family_code}")
    print(f"🧩 Parent Code: {parent_code}")
    print(rule(color=C.CYAN))

    for benefit in main_detail["package_option"]["benefits"]:
        print(f" 📦 {benefit['name']}")
        data_type = benefit["data_type"]
        total = benefit["total"]
        if data_type == "VOICE" and total > 0:
            print(sp(f"  📊 {total / 60} menit", C.YELLOW))
        elif data_type == "TEXT" and total > 0:
            print(sp(f"  📊 {total} SMS", C.YELLOW))
        elif data_type == "DATA" and total > 0:
            print(sp(f"  📊 {format_quota_byte(int(total))} ({data_type})", C.YELLOW))
        elif data_type not in ("DATA", "VOICE", "TEXT"):
            print(sp(f"  📊 {total} ({data_type})", C.YELLOW))
        if benefit["is_unlimited"]:
            print(sp("  ♾️ Unlimited", C.GREEN))

    payment_for = selected.get("payment_for", "BUY_PACKAGE")
    ask_overwrite = selected.get("ask_overwrite", False)
    overwrite_amount = selected.get("overwrite_amount", -1)
    token_confirmation_idx = selected.get("token_confirmation_idx", 0)
    amount_idx = selected.get("amount_idx", -1)

    while True:
        print(sp("💳 Pilih Metode Bayar:", C.BOLD, C.WHITE))
        print(f"{'1':>3}  💰 Balance")
        print(f"{'2':>3}  💵 E-Wallet")
        print(f"{'3':>3}  🧾 QRIS")
        print(f"{'X':>3}  ↩️ Kembali")
        method = input("🧭 Pilih metode: ").strip().lower()
        if method == "x":
            return
        if method == "1":
            if overwrite_amount == -1:
                print(warn(f"💡 Pastikan saldo KURANG DARI Rp{payment_items[-1]['item_price']}!"))
                if input(sp("🧭 Lanjut beli? (y/n): ", C.BOLD)).lower() != "y":
                    continue
            settlement_balance(
                api_key, tokens, payment_items, payment_for, ask_overwrite,
                overwrite_amount=overwrite_amount,
                token_confirmation_idx=token_confirmation_idx,
                amount_idx=amount_idx,
            )
            input(sp("⏎ Lanjut…", C.DIM))
            return
        if method == "2":
            show_multipayment(
                api_key, tokens, payment_items, payment_for, ask_overwrite,
                overwrite_amount, token_confirmation_idx, amount_idx,
            )
            input(sp("⏎ Lanjut…", C.DIM))
            return
        if method == "3":
            show_qris_payment(
                api_key, tokens, payment_items, payment_for, ask_overwrite,
                overwrite_amount, token_confirmation_idx, amount_idx,
            )
            input(sp("⏎ Lanjut…", C.DIM))
            return
        print(fail("Metode salah"))
        pause()


def show_hot_menu() -> None:
    api_key = SESSION.api_key
    tokens = SESSION.get_active_tokens()
    if tokens is None:
        return

    with open("hot_data/hot.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    hot = data["hot"]
    bundles = data["bundles"]
    offset = len(hot)

    while True:
        clear_screen()
        print(rule(char="=", color=C.B_RED))
        print(tt("🔥 PAKET HOT", color=C.B_RED))
        print(rule(char="=", color=C.B_RED))
        for idx, item in enumerate(hot, 1):
            print(f"{idx:>3}  {sp(item['family_name'], C.BOLD, C.WHITE)}"
                  f" - {sp(item['variant_name'], C.CYAN)}"
                  f" - {sp(item['option_name'], C.YELLOW)}")
        print(rule(char="-", color=C.B_RED))
        for j, bundle in enumerate(bundles, offset + 1):
            print(f"{j:>3}  {sp(bundle['name'], C.BOLD, C.WHITE)}  {sp(bundle['price'], C.YELLOW)}")
        print(rule())
        print(f"{'X':>3}  ↩️ Kembali")
        print(rule())
        choice = input("🧭 Pilih paket (nomor): ").strip()
        if choice.lower() == "x":
            return
        if not choice.isdigit():
            print(fail("Input salah"))
            pause()
            continue
        n = int(choice)
        if 1 <= n <= offset:
            selected = hot[n - 1]
            family_data = get_family(api_key, tokens, selected["family_code"], selected["is_enterprise"])
            if not family_data:
                print(fail("Gagal ambil data family"))
                pause()
                continue

            option_code = None
            for variant in family_data["package_variants"]:
                if variant["name"] != selected["variant_name"]:
                    continue
                for option in variant["package_options"]:
                    if option["order"] == selected["order"]:
                        option_code = option["package_option_code"]
                        break
                if option_code:
                    break

            if option_code:
                show_package_details(api_key, tokens, option_code, selected["is_enterprise"])
        elif offset < n <= offset + len(bundles):
            _buy_bundle(api_key, tokens, bundles[n - offset - 1])
        else:
            print(fail("Input salah"))
            pause()