"""Ah-Si-Ata CLI entry point."""
from __future__ import annotations

import sys
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

from ahsiata.api.client import get_balance
from ahsiata.api.profile import get_tiering_info
from ahsiata.api.registration import dukcapil
from ahsiata.api.family_plan import validate_msisdn as api_validate_msisdn
from ahsiata.core.session import SESSION
from ahsiata.ui.account import show_account_menu
from ahsiata.ui.bookmark import show_bookmark_menu
from ahsiata.ui.circle.info import show_circle_info
from ahsiata.ui.family_plan import show_family_info
from ahsiata.ui.hot import show_hot_menu, show_hot_menu2
from ahsiata.ui.notification import show_notification_menu
from ahsiata.ui.package.details import fetch_my_packages, show_package_details
from ahsiata.ui.package.list import get_packages_by_family
from ahsiata.ui.payment import show_transaction_history
from ahsiata.ui.purchase.loop import purchase_by_family
from ahsiata.ui.store.redeemables import show_redeemables_menu
from ahsiata.ui.store.search import show_family_list_menu, show_store_packages_menu
from ahsiata.ui.store.segments import show_store_segments_menu
from ahsiata.ui.utils import clear_screen, pause

WIDTH = 55


def show_main_menu(profile: dict) -> None:
    clear_screen()
    print("=" * WIDTH)
    expired_at_dt = datetime.fromtimestamp(profile["balance_expired_at"]).strftime("%Y-%m-%d")
    print(f"Nomor: {profile['number']} | Type: {profile['subscription_type']}".center(WIDTH))
    print(f"Pulsa: Rp {profile['balance']} | Aktif sampai: {expired_at_dt}".center(WIDTH))
    print(f"{profile['point_info']}".center(WIDTH))
    print("=" * WIDTH)
    print("Menu:")
    print("1. Login/Ganti akun")
    print("2. Lihat Paket Saya")
    print("3. Beli Paket 🔥 HOT 🔥")
    print("4. Beli Paket 🔥 HOT-2 🔥")
    print("5. Beli Paket Berdasarkan Option Code")
    print("6. Beli Paket Berdasarkan Family Code")
    print("7. Beli Semua Paket di Family Code (loop)")
    print("8. Riwayat Transaksi")
    print("9. Family Plan/Akrab Organizer")
    print("10. Circle")
    print("11. Store Segments")
    print("12. Store Family List")
    print("13. Store Packages")
    print("14. Redemables")
    print("R. Register")
    print("N. Notifikasi")
    print("V. Validate msisdn")
    print("00. Bookmark Paket")
    print("99. Tutup aplikasi")
    print("-------------------------------------------------------")


def main() -> None:
    while True:
        active_user = SESSION.get_active_user()

        if active_user is None:
            selected_number = show_account_menu()
            if selected_number:
                SESSION.set_active_user(selected_number)
            else:
                print("No user selected or failed to load user.")
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
        choice = input("Pilih menu: ").strip()

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
            show_hot_menu2()
        elif choice == "5":
            option_code = input("Enter option code (or '99' to cancel): ")
            if option_code != "99":
                show_package_details(SESSION.api_key, active_user["tokens"], option_code, False)
        elif choice == "6":
            family_code = input("Enter family code (or '99' to cancel): ")
            if family_code != "99":
                get_packages_by_family(family_code)
        elif choice == "7":
            family_code = input("Enter family code (or '99' to cancel): ")
            if family_code != "99":
                start_from = input("Start purchasing from option number (default 1): ") or "1"
                use_decoy = input("Use decoy package? (y/n): ").lower() == "y"
                pause_on_success = input("Pause on each successful purchase? (y/n): ").lower() == "y"
                delay = input("Delay seconds between purchases (0 for no delay): ") or "0"
                try:
                    start_from_int = int(start_from)
                except ValueError:
                    start_from_int = 1
                try:
                    delay_int = int(delay)
                except ValueError:
                    delay_int = 0
                purchase_by_family(family_code, use_decoy, pause_on_success, delay_int, start_from_int)
        elif choice == "8":
            show_transaction_history(SESSION.api_key, active_user["tokens"])
        elif choice == "9":
            show_family_info(SESSION.api_key, active_user["tokens"])
        elif choice == "10":
            show_circle_info(SESSION.api_key, active_user["tokens"])
        elif choice == "11":
            is_enterprise = input("Is enterprise store? (y/n): ").lower() == "y"
            show_store_segments_menu(is_enterprise)
        elif choice == "12":
            is_enterprise = input("Is enterprise? (y/n): ").lower() == "y"
            show_family_list_menu(profile["subscription_type"], is_enterprise)
        elif choice == "13":
            is_enterprise = input("Is enterprise? (y/n): ").lower() == "y"
            show_store_packages_menu(profile["subscription_type"], is_enterprise)
        elif choice == "14":
            is_enterprise = input("Is enterprise? (y/n): ").lower() == "y"
            show_redeemables_menu(is_enterprise)
        elif choice == "00":
            show_bookmark_menu()
        elif choice == "99":
            print("Exiting the application.")
            sys.exit(0)
        elif choice.lower() == "r":
            msisdn = input("Enter msisdn (628xxxx): ")
            nik = input("Enter NIK: ")
            kk = input("Enter KK: ")
            import json
            res = dukcapil(SESSION.api_key, msisdn, kk, nik)
            print(json.dumps(res, indent=2))
            pause()
        elif choice.lower() == "v":
            msisdn = input("Enter the msisdn to validate (628xxxx): ")
            res = api_validate_msisdn(SESSION.api_key, active_user["tokens"], msisdn)
            import json
            print(json.dumps(res, indent=2))
            pause()
        elif choice.lower() == "n":
            show_notification_menu()
        else:
            print("Invalid choice. Please try again.")
            pause()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting the application.")
