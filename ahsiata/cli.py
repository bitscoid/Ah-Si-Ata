"""Ah-Si-Ata CLI entry point (`python -m ahsiata` or the `ahsiata` script).
"""
from __future__ import annotations

import json
import sys
from datetime import datetime

from ahsiata.api.client import get_balance
from ahsiata.api.profile import get_tiering_info
from ahsiata.api.registration import dukcapil
from ahsiata.api.family_plan import validate_msisdn as api_validate_msisdn
from ahsiata.core.bookmark import BOOKMARK
from ahsiata.core.session import SESSION
from ahsiata.ui.account import show_account_menu
from ahsiata.ui.bookmark import show_bookmark_menu
from ahsiata.ui.circle.info import show_circle_info
from ahsiata.ui.family_plan import show_family_info
from ahsiata.ui.hot import show_hot_menu
from ahsiata.ui.notification import show_notification_menu
from ahsiata.ui.package.details import fetch_my_packages, show_package_details
from ahsiata.ui.package.list import get_packages_by_family
from ahsiata.ui.payment import show_transaction_history
from ahsiata.ui.purchase.loop import purchase_by_family
from ahsiata.ui.store.redeemables import show_redeemables_menu
from ahsiata.ui.store.search import show_family_list_menu, show_store_packages_menu
from ahsiata.ui.store.segments import show_store_segments_menu
from ahsiata.ui.style import C, p, title, rule, center, fail, disp_w
from ahsiata.ui.utils import clear_screen, pause

WIDTH = 55

MENU_ITEMS = [
    ("1", "👤", "Akun"),
    ("2", "📦", "Paket"),
    ("3", "🔥", "Hot"),
    ("4", "🔎", "Option Code"),
    ("5", "👨", "Family Code"),
    ("6", "🔄", "Loop"),
    ("7", "🧾", "Riwayat"),
    ("8", "👨", "Family Plan"),
    ("9", "🫂", "Circle"),
    ("P", "🏬", "Promo"),
    ("F", "🏬", "Family List"),
    ("S", "🛒", "Store"),
    ("G", "🎁", "C"),
    ("R", "📝", "Registrasi"),
    ("N", "🔔", "Notifikasi"),
    ("V", "🎯", "Validasi"),
    ("B", "⭐", "Bookmark"),
    ("X", "🚪", "Keluar"),
]


def show_main_menu(profile: dict) -> None:
    clear_screen()
    number = profile["number"]
    subscription_type = profile["subscription_type"]
    balance_remaining = profile["balance"]
    balance_expired_at = profile["balance_expired_at"]
    balance_text = f"Rp {balance_remaining}" if balance_remaining is not None else "Saldo N/A"
    expired_text = datetime.fromtimestamp(balance_expired_at).strftime("%Y-%m-%d") if balance_expired_at else "N/A"
    point_info = profile["point_info"]
    print(title("🔥 AH-SI-ATA 🔥", color=C.MAGENTA))
    print(p(center(f"📱 {number} | {subscription_type}", WIDTH), C.BOLD, C.WHITE))
    print(p(center(f"💰 {balance_text} | Aktif s/d: {expired_text}", WIDTH), C.BOLD, C.YELLOW))
    if "Points" in point_info:
        point_info = point_info.replace("Points", "⭐ Points")
    print(p(center(point_info, WIDTH), C.CYAN))
    print(rule(char="=", color=C.BLUE))
    items = MENU_ITEMS
    half = (len(items) + 1) // 2
    for i in range(half):
        left = items[i]
        right = items[i + half] if i + half < len(items) else None
        left_str = f"{left[0]:>3}  {left[1]} {left[2]}"
        if right:
            right_str = f"{right[0]:>3}  {right[1]} {right[2]}"
            print(f"{left_str:<27}  {right_str}")
        else:
            print(left_str)
    print(rule(char="-", color=C.BLUE))


def _show_result(label: str, res) -> None:
    """Render API response as labeled lines instead of raw JSON."""
    print(p(f"📋 {label}", C.BOLD, C.WHITE))
    if isinstance(res, dict):
        for k, v in res.items():
            if isinstance(v, (dict, list)):
                v = json.dumps(v, ensure_ascii=False)
            print(f"  {p(str(k).replace('_', ' ').capitalize(), C.CYAN)}: {v}")
    else:
        print(p(str(res), C.YELLOW))


def _run() -> None:
    while True:
        active_user = SESSION.get_active_user()

        if active_user is None:
            selected_number = show_account_menu()
            if selected_number:
                SESSION.set_active_user(selected_number)
            else:
                print(fail("Gagal memuat user"))
            continue

        balance = get_balance(SESSION.api_key, active_user["tokens"]["id_token"])
        balance_remaining = balance.get("remaining") if isinstance(balance, dict) else None
        balance_expired_at = balance.get("expired_at") if isinstance(balance, dict) else None

        point_info = "Points: N/A | Tier: N/A"
        if active_user["subscription_type"] == "PREPAID":
            tiering_data = get_tiering_info(SESSION.api_key, active_user["tokens"])
            tier = tiering_data.get("tier", 0)
            current_point = tiering_data.get("current_point", 0)
            point_info = f"Points: {current_point} | Tier: {tier}"

        profile = {
            "number": active_user["number"],
            "subscriber_id": active_user["subscriber_id"],
            "subscription_type": active_user["subscription_type"],
            "balance": balance_remaining,
            "balance_expired_at": balance_expired_at,
            "point_info": point_info,
        }
        show_main_menu(profile)
        choice = input(p("🧭 Pilih : ", C.BOLD)).strip()

        if choice == "t":
            pause()
        elif choice == "1":
            selected_number = show_account_menu()
            if selected_number:
                SESSION.set_active_user(selected_number)
        elif choice == "2":
            fetch_my_packages()
        elif choice == "3":
            show_hot_menu()
        elif choice == "4":
            option_code = input(p("🧭 Kode opsi (99=batal): ", C.BOLD))
            if option_code != "99":
                show_package_details(SESSION.api_key, active_user["tokens"], option_code, False)
        elif choice == "5":
            family_code = input(p("🧭 Family code (99=batal): ", C.BOLD))
            if family_code != "99":
                get_packages_by_family(family_code)
        elif choice == "6":
            family_code = input(p("🧭 Family code (99=batal): ", C.BOLD))
            if family_code != "99":
                start_from = input(p("🧭 Mulai dari opsi (1): ", C.BOLD)) or "1"
                use_decoy = input(p("🧭 Paket decoy? (y/n): ", C.BOLD)).lower() == "y"
                pause_on_success = input(p("🧭 Jeda tiap sukses? (y/n): ", C.BOLD)).lower() == "y"
                delay = input(p("🧭 Jeda detik (0): ", C.BOLD)) or "0"
                try:
                    start_from_int = int(start_from)
                except ValueError:
                    start_from_int = 1
                try:
                    delay_int = int(delay)
                except ValueError:
                    delay_int = 0
                purchase_by_family(family_code, use_decoy, pause_on_success, delay_int, start_from_int)
        elif choice == "7":
            show_transaction_history(SESSION.api_key, active_user["tokens"])
        elif choice == "8":
            show_family_info(SESSION.api_key, active_user["tokens"])
        elif choice == "9":
            show_circle_info(SESSION.api_key, active_user["tokens"])
        elif choice.lower() == "p":
            is_enterprise = input(p("🧭 Toko enterprise? (y/n): ", C.BOLD)).lower() == "y"
            show_store_segments_menu(is_enterprise)
        elif choice.lower() == "f":
            is_enterprise = input(p("🧭 Toko enterprise? (y/n): ", C.BOLD)).lower() == "y"
            show_family_list_menu(profile["subscription_type"], is_enterprise)
        elif choice.lower() == "s":
            is_enterprise = input(p("🧭 Toko enterprise? (y/n): ", C.BOLD)).lower() == "y"
            show_store_packages_menu(profile["subscription_type"], is_enterprise)
        elif choice.lower() == "g":
            is_enterprise = input(p("🧭 Toko enterprise? (y/n): ", C.BOLD)).lower() == "y"
            show_redeemables_menu(is_enterprise)
        elif choice.lower() == "b":
            show_bookmark_menu()
        elif choice.lower() == "x":
            print(p("👋 Menutup aplikasi.", C.CYAN))
            sys.exit(0)
        elif choice.lower() == "r":
            msisdn = input(p("🧭 MSISDN (628…): ", C.BOLD))
            nik = input(p("🧭 NIK: ", C.BOLD))
            kk = input(p("🧭 KK: ", C.BOLD))
            res = dukcapil(SESSION.api_key, msisdn, kk, nik)
            _show_result("Hasil Registrasi", res)
            pause()
        elif choice.lower() == "v":
            msisdn = input(p("🧭 MSISDN validasi (628…): ", C.BOLD))
            res = api_validate_msisdn(SESSION.api_key, active_user["tokens"], msisdn)
            _show_result("Hasil Validasi MSISDN", res)
            pause()
        elif choice.lower() == "n":
            show_notification_menu()
        else:
            print(fail("Pilihan salah"))
            pause()


def main() -> None:
    """CLI entry point: load on-disk state, then run the menu loop.

    `ponytail:` hard-coded state paths are CWD-relative; move to a data dir
    (XDG) when headless/installed modes matter. Error pauses inside
    `core/session.py` and debug `print`s stay for now; replace with
    exceptions + `logging` when automation is required.
    """
    SESSION.initialize()
    BOOKMARK.initialize()
    try:
        _run()
    except KeyboardInterrupt:
        print(p("\n👋 Menutup aplikasi.", C.CYAN))


if __name__ == "__main__":
    main()