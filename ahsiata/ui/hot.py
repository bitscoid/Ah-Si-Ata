"""HOT packages menu (preset JSON of favourite deals)."""
from __future__ import annotations

import json

from ahsiata.api.packages import get_family, get_package_details
from ahsiata.api.purchase.balance import settlement_balance
from ahsiata.api.purchase.ewallet import show_multipayment
from ahsiata.api.purchase.qris import show_qris_payment
from ahsiata.core.session import SESSION
from ahsiata.type_dict import PaymentItem
from ahsiata.ui.package.details import show_package_details
from ahsiata.ui.utils import clear_screen, format_quota_byte, pause

WIDTH = 55


def _show_hot_list():
    clear_screen()
    print("=" * WIDTH)
    print("🔥 Paket  Hot 🔥".center(WIDTH))
    print("=" * WIDTH)

    with open("hot_data/hot.json", "r", encoding="utf-8") as f:
        hot_packages = json.load(f)

    for idx, p in enumerate(hot_packages):
        print(f"{idx + 1}. {p['family_name']} - {p['variant_name']} - {p['option_name']}")
        print("-" * WIDTH)

    print("00. Kembali ke menu utama")
    print("-" * WIDTH)
    return hot_packages


def show_hot_menu() -> None:
    api_key = SESSION.api_key
    tokens = SESSION.get_active_tokens()

    while True:
        hot_packages = _show_hot_list()
        choice = input("Pilih paket (nomor): ")
        if choice == "00":
            return
        if not choice.isdigit() or not (1 <= int(choice) <= len(hot_packages)):
            print("Input tidak valid.")
            pause()
            continue

        selected = hot_packages[int(choice) - 1]
        family_data = get_family(api_key, tokens, selected["family_code"], selected["is_enterprise"])
        if not family_data:
            print("Gagal mengambil data family.")
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


def show_hot_menu2() -> None:
    api_key = SESSION.api_key
    tokens = SESSION.get_active_tokens()

    while True:
        clear_screen()
        print("=" * WIDTH)
        print("🔥 Paket  Hot 2 🔥".center(WIDTH))
        print("=" * WIDTH)

        with open("hot_data/hot2.json", "r", encoding="utf-8") as f:
            hot_packages = json.load(f)

        for idx, p in enumerate(hot_packages):
            print(f"{idx + 1}. {p['name']}\n   Harga: {p['price']}")
            print("-" * WIDTH)

        print("00. Kembali ke menu utama")
        print("-" * WIDTH)
        choice = input("Pilih paket (nomor): ")
        if choice == "00":
            return
        if not choice.isdigit() or not (1 <= int(choice) <= len(hot_packages)):
            print("Input tidak valid.")
            pause()
            continue

        selected = hot_packages[int(choice) - 1]
        packages = selected.get("packages", [])
        if not packages:
            print("Paket tidak tersedia.")
            pause()
            continue

        payment_items: list[PaymentItem] = []
        main_detail = None
        for package in packages:
            detail = get_package_details(
                api_key, tokens,
                package["family_code"], package["variant_code"], package["order"],
                package["is_enterprise"], package["migration_type"],
            )
            if not detail:
                print(f"Gagal mengambil detail paket untuk {package['family_code']}.")
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

        print("=" * WIDTH)
        print(f"Name: {selected['name']}")
        print(f"Price: {selected['price']}")
        print(f"Detail: {selected['detail']}")
        print("=" * WIDTH)
        print(f"Nama: {title}")
        print(f"Harga: Rp {price}")
        print(f"Payment For: {payment_for}")
        print(f"Masa Aktif: {validity}")
        print(f"Point: {main_detail['package_option']['point']}")
        print(f"Plan Type: {main_detail['package_family']['plan_type']}")
        print("-" * WIDTH)
        print(f"Family Code: {family_code}")
        print(f"Parent Code (for addon/dummy): {parent_code}")
        print("-" * WIDTH)

        for benefit in main_detail["package_option"]["benefits"]:
            print(f" Name: {benefit['name']}")
            data_type = benefit["data_type"]
            total = benefit["total"]
            if data_type == "VOICE" and total > 0:
                print(f"  Total: {total / 60} menit")
            elif data_type == "TEXT" and total > 0:
                print(f"  Total: {total} SMS")
            elif data_type == "DATA" and total > 0:
                print(f"  Total: {format_quota_byte(int(total))} ({data_type})")
            elif data_type not in ("DATA", "VOICE", "TEXT"):
                print(f"  Total: {total} ({data_type})")
            if benefit["is_unlimited"]:
                print("  Unlimited: Yes")

        payment_for = selected.get("payment_for", "BUY_PACKAGE")
        ask_overwrite = selected.get("ask_overwrite", False)
        overwrite_amount = selected.get("overwrite_amount", -1)
        token_confirmation_idx = selected.get("token_confirmation_idx", 0)
        amount_idx = selected.get("amount_idx", -1)

        while True:
            print("Pilih Metode Pembelian:")
            print("1. Balance")
            print("2. E-Wallet")
            print("3. QRIS")
            print("00. Kembali ke menu sebelumnya")
            method = input("Pilih metode (nomor): ")
            if method == "00":
                break
            if method == "1":
                if overwrite_amount == -1:
                    print(f"Pastikan sisa balance KURANG DARI Rp{payment_items[-1]['item_price']}!!!")
                    if input("Apakah anda yakin ingin melanjutkan pembelian? (y/n): ").lower() != "y":
                        continue
                settlement_balance(
                    api_key, tokens, payment_items, payment_for, ask_overwrite,
                    overwrite_amount=overwrite_amount,
                    token_confirmation_idx=token_confirmation_idx,
                    amount_idx=amount_idx,
                )
                input("Tekan enter untuk kembali...")
                return
            if method == "2":
                show_multipayment(
                    api_key, tokens, payment_items, payment_for, ask_overwrite,
                    overwrite_amount, token_confirmation_idx, amount_idx,
                )
                input("Tekan enter untuk kembali...")
                return
            if method == "3":
                show_qris_payment(
                    api_key, tokens, payment_items, payment_for, ask_overwrite,
                    overwrite_amount, token_confirmation_idx, amount_idx,
                )
                input("Tekan enter untuk kembali...")
                return
            print("Metode tidak valid.")
            pause()
