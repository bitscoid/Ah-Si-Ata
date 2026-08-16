"""Package detail screen: show info, choose payment method, redeem options."""
from __future__ import annotations


from ahsiata.api.client import send_api_request
from ahsiata.api.packages import get_addons, get_package, unsubscribe
from ahsiata.api.purchase.balance import append_decoy_item, settle_with_decoy, settlement_balance
from ahsiata.api.purchase.ewallet import show_multipayment
from ahsiata.api.purchase.qris import show_qris_payment
from ahsiata.api.purchase.redeem import (
    bounty_allotment,
    settlement_bounty,
    settlement_loyalty,
)
from ahsiata.constants import Endpoint, LANG_EN, PaymentFor
from ahsiata.core.bookmark import BOOKMARK
from ahsiata.core.decoy import DECOY
from ahsiata.core.session import SESSION
from ahsiata.type_dict import PaymentItem
from ahsiata.ui.purchase.single import purchase_n_times_by_option_code
from ahsiata.ui.style import C, p, title, rule, ok, fail, warn, info
from ahsiata.ui.utils import clear_screen, display_html, format_quota_byte, pause


def _print_benefits(benefits: list[dict]) -> None:
    if not benefits or not isinstance(benefits, list):
        return
    print(p("🎁 Benefit:", C.BOLD, C.WHITE))
    for benefit in benefits:
        print(rule(color=C.CYAN))
        print(f" 📦 {benefit['name']}")
        print(f"  🔢 ID: {benefit['item_id']}")
        data_type = benefit["data_type"]
        total = benefit["total"]
        if data_type == "VOICE" and total > 0:
            print(p(f"  ⏳ Total: {total / 60} menit", C.YELLOW))
        elif data_type == "TEXT" and total > 0:
            print(p(f"  ⏳ Total: {total} SMS", C.YELLOW))
        elif data_type == "DATA" and total > 0:
            print(p(f"  ⏳ Kuota: {format_quota_byte(int(total))}", C.YELLOW))
        elif data_type not in ("DATA", "VOICE", "TEXT"):
            print(p(f"  ⏳ Total: {total} ({data_type})", C.YELLOW))
        if benefit.get("is_unlimited"):
            print(p("  ♾️ Unlimited", C.GREEN))


def _print_summary(package: dict) -> tuple[str, int, str, str, str]:
    price = package["package_option"]["price"]
    validity = package["package_option"]["validity"]
    payment_for = package["package_family"]["payment_for"]
    option_name = package.get("package_option", {}).get("name", "")
    family_name = package.get("package_family", {}).get("name", "")
    variant_name = package.get("package_detail_variant", {}).get("name", "") if isinstance(package.get("package_detail_variant"), dict) else ""
    title = f"{family_name} - {variant_name} - {option_name}".strip()
    family_code = package.get("package_family", {}).get("package_family_code", "")
    parent_code = package.get("package_addon", {}).get("parent_code", "") or "N/A"

    print(rule(color=C.CYAN))
    print(f"📦 Nama: {p(title, C.BOLD, C.WHITE)}")
    print(f"💰 Harga: {p(f'Rp {price}', C.BOLD, C.GREEN)}")
    print(f"💳 Pembayaran: {payment_for}")
    print(f"⏳ Masa Aktif: {validity}")
    print(f"⭐ Point: {package['package_option']['point']}")
    print(f"🏷 Plan: {package['package_family']['plan_type']}")
    print(rule(color=C.CYAN))
    print(f"🔢 Family Code: {family_code}")
    print(f"🧩 Parent Code: {parent_code}")
    print(rule(color=C.CYAN))
    _print_benefits(package["package_option"]["benefits"])
    return title, price, payment_for, family_code, parent_code


def show_package_details(api_key, tokens, package_option_code, is_enterprise, option_order: int = -1):
    clear_screen()
    print(rule(color=C.CYAN))
    print(title("📦 Detail Paket", color=C.CYAN))
    print(rule(color=C.CYAN))
    package = get_package(api_key, tokens, package_option_code)
    if not package:
        print(fail("Gagal muat detail paket"))
        pause()
        return False

    variant_name = (package.get("package_detail_variant") or {}).get("name", "") if isinstance(package.get("package_detail_variant"), dict) else ""
    option_name = package.get("package_option", {}).get("name", "")
    price = package["package_option"]["price"]
    token_confirmation = package["token_confirmation"]
    ts_to_sign = package["timestamp"]
    payment_for = package["package_family"]["payment_for"] or PaymentFor.BUY_PACKAGE

    payment_items = [PaymentItem(
        item_code=package_option_code,
        product_type="",
        item_price=price,
        item_name=f"{variant_name} {option_name}".strip(),
        tax=0,
        token_confirmation=token_confirmation,
    )]

    _print_summary(package)
    detail_html = display_html(package["package_option"]["tnc"])
    addons = get_addons(api_key, tokens, package_option_code) or {}

    print(p("➕ Addon:", C.BOLD, C.WHITE))
    if isinstance(addons, dict) and addons:
        for code, val in addons.items():
            name = val.get("name", "") if isinstance(val, dict) else ""
            print(f"  🔢 {code}" + (f" - {name}" if name else ""))
    else:
        print(p("💡 Tidak ada addon", C.DIM))
    print(rule(color=C.CYAN))
    print(p("📜 Syarat & Ketentuan:", C.BOLD, C.WHITE))
    print(detail_html if detail_html.strip() else p("💡 Tidak ada Syarat & Ketentuan untuk paket ini", C.DIM))
    print(rule(color=C.CYAN))

    while True:
        print(p("⚙️ Opsi:", C.BOLD, C.WHITE))
        print("1. 💳 Beli Pulsa")
        print("2. 💵 E-Wallet")
        print("3. 🧾 QRIS")
        print("4. 🎭 Pulsa+Decoy")
        print("5. 🎭 Pulsa+Decoy V2")
        print("6. 🎭 QRIS+Decoy")
        print("7. 🎭 QRIS+Decoy V2")
        print("8. 🔄 Pulsa N-kali")
        if payment_for == PaymentFor.REDEEM_VOUCHER:
            print("B. 🎁 Ambil bonus")
            print("BA. 📤 Kirim bonus")
            print("L. ⭐ Beli Poin")
        if option_order != -1:
            print("0. ⭐ Bookmark")
        print("00. ↩️ Kembali")

        choice = input("👉 Pilihan: ").strip()

        if choice == "00":
            return False

        if choice == "0" and option_order != -1:
            success = BOOKMARK.add_bookmark(
                family_code=package.get("package_family", {}).get("package_family_code", ""),
                family_name=package.get("package_family", {}).get("name", ""),
                is_enterprise=is_enterprise,
                variant_name=variant_name,
                option_name=option_name,
                order=option_order,
            )
            print(ok("Paket ditambahkan ke bookmark") if success else warn("Paket sudah ada di bookmark"))
            pause()
            continue

        if choice == "1":
            settlement_balance(api_key, tokens, payment_items, payment_for, True)
            input(p("⏎ Lanjut…", C.DIM))
            return True

        if choice == "2":
            show_multipayment(api_key, tokens, payment_items, payment_for, True)
            input(p("⏎ Lanjut…", C.DIM))
            return True

        if choice == "3":
            show_qris_payment(api_key, tokens, payment_items, payment_for, True)
            input(p("⏎ Lanjut…", C.DIM))
            return True

        if choice in ("4", "5"):
            decoy = DECOY.get_decoy("balance")
            decoy_detail = get_package(api_key, tokens, decoy["option_code"]) if decoy else None
            if not decoy_detail:
                print(fail("Gagal muat detail decoy"))
                pause()
                return False
            tcidx = 1 if choice == "5" else 0
            payment_for_arg = "🤫" if choice == "5" else payment_for
            res = settle_with_decoy(
                api_key, tokens, payment_items, payment_for_arg, decoy_detail,
                token_confirmation_idx=tcidx,
            )
            if isinstance(res, dict) and res.get("status") == "SUCCESS":
                print(ok("Pembelian berhasil!"))
            pause()
            return True

        if choice in ("6", "7"):
            decoy = DECOY.get_decoy("qris" if choice == "6" else "qris0")
            decoy_detail = get_package(api_key, tokens, decoy["option_code"])
            if not decoy_detail:
                print(fail("Gagal muat detail decoy"))
                pause()
                return False
            append_decoy_item(payment_items, decoy_detail)
            print(rule(color=C.YELLOW))
            print(warn(f"💰 Harga Utama: Rp {price}"))
            print(warn(f"🎭 Harga Decoy: Rp {decoy_detail['package_option']['price']}"))
            print(warn("Silahkan sesuaikan amount (trial & error, 0 = malformed)"))
            print(rule(color=C.YELLOW))
            show_qris_payment(
                api_key, tokens, payment_items, PaymentFor.SHARE_PACKAGE, True,
                token_confirmation_idx=1,
            )
            input(p("⏎ Lanjut…", C.DIM))
            return True

        if choice == "8":
            use_decoy = input(p("👉 Pakai decoy? (y/n): ", C.YELLOW)).strip().lower() == "y"
            n_times_str = input(p("👉 Jumlah pembelian (contoh: 3): ", C.YELLOW)).strip()
            delay_str = input(p("👉 Jeda antar pembelian (dtk): ", C.YELLOW)).strip() or "0"
            try:
                n_times = int(n_times_str)
                if n_times < 1:
                    raise ValueError
            except ValueError:
                print(fail("Angka tidak valid"))
                pause()
                continue
            purchase_n_times_by_option_code(
                n_times,
                option_code=package_option_code,
                use_decoy=use_decoy,
                delay_seconds=int(delay_str),
                pause_on_success=False,
                token_confirmation_idx=1,
            )

        if choice.lower() == "b":
            settlement_bounty(
                api_key=api_key, tokens=tokens,
                token_confirmation=token_confirmation, ts_to_sign=ts_to_sign,
                payment_target=package_option_code, price=price, item_name=variant_name,
            )
            input(p("⏎ Lanjut…", C.DIM))
            return True

        if choice.lower() == "ba":
            destination_msisdn = input(p("👉 Nomor tujuan (62…): ", C.YELLOW)).strip()
            bounty_allotment(
                api_key=api_key, tokens=tokens,
                ts_to_sign=ts_to_sign, destination_msisdn=destination_msisdn,
                item_name=option_name, item_code=package_option_code,
                token_confirmation=token_confirmation,
            )
            pause()
            return True

        if choice.lower() == "l":
            settlement_loyalty(
                api_key=api_key, tokens=tokens,
                token_confirmation=token_confirmation, ts_to_sign=ts_to_sign,
                payment_target=package_option_code, price=price,
            )
            input(p("⏎ Lanjut…", C.DIM))
            return True

        print(info("Pembelian dibatalkan"))
        return False


def fetch_my_packages() -> None:
    user = SESSION.get_active_user()
    if user is None:
        return
    api_key = SESSION.api_key
    tokens = user["tokens"]

    payload = {"is_enterprise": False, "lang": LANG_EN, "family_member_id": ""}
    res = send_api_request(api_key, Endpoint.QUOTA_DETAILS, payload, tokens["id_token"], "POST")
    if not isinstance(res, dict) or res.get("status") != "SUCCESS":
        print(fail("Gagal mengambil paket"))
        pause()
        return

    quotas = res["data"]["quotas"]
    clear_screen()
    print(rule(char="=", color=C.BLUE))
    print(title("📦 Paket Saya", color=C.CYAN))
    print(rule(char="=", color=C.BLUE))

    my_packages = []
    for idx, quota in enumerate(quotas, start=1):
        quota_code = quota["quota_code"]
        group_code = quota["group_code"]
        group_name = quota["group_name"]
        quota_name = quota["name"]
        family_code = "N/A"

        product_subscription_type = quota.get("product_subscription_type", "")
        product_domain = quota.get("product_domain", "")

        benefit_infos = []
        for benefit in quota.get("benefits", []):
            bid = benefit.get("id", "")
            name = benefit.get("name", "")
            data_type = benefit.get("data_type", "N/A")
            remaining = benefit.get("remaining", 0)
            total = benefit.get("total", 0)
            info = (
                "  -----------------------------------------------------\n"
                f"  ID    : {bid}\n"
                f"  Name  : {name}\n"
                f"  Type  : {data_type}\n"
            )
            if data_type == "DATA":
                info += f"  Kuota : {format_quota_byte(remaining)} / {format_quota_byte(total)}"
            elif data_type == "VOICE":
                info += f"  Kuota : {remaining / 60:.2f} / {total / 60:.2f} menit"
            elif data_type == "TEXT":
                info += f"  Kuota : {remaining} / {total} SMS"
            else:
                info += f"  Kuota : {remaining} / {total}"
            benefit_infos.append(info)

        package_details = get_package(api_key, tokens, quota_code)
        if package_details:
            family_code = package_details["package_family"]["package_family_code"]

        print(rule(char="=", color=C.BLUE))
        print(p(f"📦 Paket {idx}", C.BOLD, C.WHITE))
        print(f"📛 Nama: {quota_name}")
        if benefit_infos:
            print(p("🎁 Benefit:", C.BOLD, C.WHITE))
            for bi in benefit_infos:
                print(p(bi, C.YELLOW))
            print(rule(color=C.BLUE))
        print(f"👥 Grup: {group_name}")
        print(f"🔢 Kode Kuota: {quota_code}")
        print(f"🔢 Family: {family_code}")
        print(f"🔢 Kode Grup: {group_code}")
        print(rule(char="=", color=C.BLUE))

        my_packages.append({
            "number": idx,
            "name": quota_name,
            "quota_code": quota_code,
            "product_subscription_type": product_subscription_type,
            "product_domain": product_domain,
        })

    print(rule(char="-", color=C.BLUE))
    print(p(f"{'':>3}  {'D':>2} Berhenti    {'B':>2} Kembali", C.DIM))
    print()
    choice = input(p("🧭 Pilihan: ", C.YELLOW)).strip()

    if choice.lower() == "b":
        return

    if choice.isdigit() and 1 <= int(choice) <= len(my_packages):
        selected = next((pkg for pkg in my_packages if pkg["number"] == int(choice)), None)
        if selected:
            show_package_details(api_key, tokens, selected["quota_code"], False)
        return

    if choice.lower().startswith("d"):
        tail = choice[1:]
        if tail == "":
            tail = input(p("🧭 Nomor urut berhenti: ", C.BOLD))
        if not tail.isdigit() or not (1 <= int(tail) <= len(my_packages)):
            print(fail("Nomor urut tidak valid (contoh: D2)"))
            pause()
            return
        target = my_packages[int(tail) - 1]
        if input(p(f"🧭 Berhenti berlangganan dari {target['name']}? (y/n): ", C.BOLD)).lower() != "y":
            print(p("💡 Dibatalkan", C.CYAN))
            pause()
            return
        if unsubscribe(api_key, tokens, target["quota_code"], target["product_domain"], target["product_subscription_type"]):
            print(ok("Berhenti berlangganan"))
        else:
            print(fail("Gagal berhenti berlangganan"))
        pause()
