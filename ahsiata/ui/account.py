"""Account / login menu: add, switch, remove accounts."""
from __future__ import annotations

from ahsiata.api.auth import get_otp, submit_otp
from ahsiata.core.session import SESSION
from ahsiata.ui.utils import clear_screen, pause


def _login_prompt(api_key: str) -> tuple[str, str] | None:
    """Run the OTP login flow; return (phone_number, refresh_token) on success."""
    clear_screen()
    print("-------------------------------------------------------")
    print("Login ke MyXL")
    print("-------------------------------------------------------")
    print("Masukan nomor XL (Contoh 6281234567890):")
    phone_number = input("Nomor: ")

    if not phone_number.startswith("628") or len(phone_number) < 10 or len(phone_number) > 14:
        print("Nomor tidak valid. Pastikan nomor diawali dengan '628' dan memiliki panjang yang benar.")
        return None

    try:
        subscriber_id = get_otp(phone_number)
        if not subscriber_id:
            return None
        print("OTP Berhasil dikirim ke nomor Anda.")

        for attempt in range(5, 0, -1):
            print(f"Sisa percobaan: {attempt}")
            otp = input("Masukkan OTP yang telah dikirim: ")
            if not otp.isdigit() or len(otp) != 6:
                print("OTP tidak valid. Pastikan OTP terdiri dari 6 digit angka.")
                continue

            tokens = submit_otp(api_key, "SMS", phone_number, otp)
            if not tokens:
                print("OTP salah. Silahkan coba lagi.")
                continue

            print("Berhasil login!")
            return phone_number, tokens["refresh_token"]

        print("Gagal login setelah beberapa percobaan. Silahkan coba lagi nanti.")
        return None
    except Exception as e:
        print(f"Gagal login: {e}")
        return None


def show_account_menu() -> int | None:
    """Show the account management screen; return the selected user number on switch, None on exit."""
    SESSION.load_tokens()
    in_menu = True
    add_user = False

    while in_menu:
        clear_screen()
        print("-------------------------------------------------------")
        if SESSION.get_active_user() is None or add_user:
            result = _login_prompt(SESSION.api_key)
            if not result:
                print("Gagal menambah akun. Silahkan coba lagi.")
                pause()
                continue

            number, refresh_token = result
            SESSION.add_refresh_token(int(number), refresh_token)
            SESSION.load_tokens()
            add_user = False
            continue

        users = SESSION.refresh_tokens
        active_user = SESSION.get_active_user()

        print("Akun Tersimpan:")
        if not users:
            print("Tidak ada akun tersimpan.")

        for idx, user in enumerate(users):
            is_active = active_user and user["number"] == active_user["number"]
            marker = "✅" if is_active else ""
            number = str(user.get("number", "")).ljust(14)
            sub_type = str(user.get("subscription_type", "")).center(12)
            print(f"{idx + 1}. {number} [{sub_type}] {marker}")

        print("-" * 55)
        print("Command:")
        print("0: Tambah Akun")
        print("Masukan nomor urut akun untuk berganti.")
        print("Masukan del <nomor urut> untuk menghapus akun tertentu.")
        print("00: Kembali ke menu utama")
        print("-" * 55)
        choice = input("Pilihan:")

        if choice == "00":
            in_menu = False
            return active_user["number"] if active_user else None

        if choice == "0":
            add_user = True
            continue

        if choice.isdigit() and 1 <= int(choice) <= len(users):
            return users[int(choice) - 1]["number"]

        if choice.startswith("del "):
            parts = choice.split()
            if len(parts) != 2 or not parts[1].isdigit():
                print("Perintah tidak valid. Gunakan format: del <nomor urut>")
                pause()
                continue
            del_idx = int(parts[1])
            if active_user and users[del_idx - 1]["number"] == active_user["number"]:
                print("Tidak dapat menghapus akun aktif. Silahkan ganti akun terlebih dahulu.")
                pause()
                continue
            if not (1 <= del_idx <= len(users)):
                print("Nomor urut tidak valid.")
                pause()
                continue

            user_to_delete = users[del_idx - 1]
            confirm = input(f"Yakin ingin menghapus akun {user_to_delete['number']}? (y/n): ")
            if confirm.lower() == "y":
                SESSION.remove_refresh_token(user_to_delete["number"])
                SESSION.load_tokens()
                print("Akun berhasil dihapus.")
            else:
                print("Penghapusan akun dibatalkan.")
            pause()
            continue

        print("Input tidak valid. Silahkan coba lagi.")
        pause()
