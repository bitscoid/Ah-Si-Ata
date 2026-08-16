"""Account / login menu: add, switch, remove accounts."""
from __future__ import annotations

from ahsiata.api.auth import get_otp, submit_otp
from ahsiata.core.session import SESSION
from ahsiata.ui.style import C, p, title, rule, center, ok, fail, warn, info
from ahsiata.ui.utils import clear_screen, pause


def _login_prompt(api_key: str) -> tuple[str, str] | None:
    """Run the OTP login flow; return (phone_number, refresh_token) on success."""
    clear_screen()
    print(title("📱 Login MyXL", color=C.BLUE))
    print(p(center("Masukkan nomor XL untuk menerima OTP", 55), C.DIM))
    print(rule(char="-", color=C.BLUE))
    print(p("Nomor XL  : ", C.BOLD), end="")
    phone_number = input().strip()

    if not phone_number.startswith("628") or len(phone_number) < 10 or len(phone_number) > 14:
        print(fail("Nomor tidak valid. Awali dengan '628' dan cek panjang."))
        return None

    try:
        print(p("📤 Mengirim OTP…", C.DIM))
        subscriber_id = get_otp(phone_number)
        if not subscriber_id:
            print(fail("OTP tidak terkirim. Coba lagi."))
            return None
        print(ok("OTP terkirim"))
        print(rule(char="-", color=C.BLUE))
        print(p("🔑 Verifikasi kode OTP 6 digit:", C.BOLD))

        for attempt in range(5, 0, -1):
            print(warn(f"Sisa percobaan: {attempt}"))
            print(p("Kode OTP  : ", C.BOLD), end="")
            otp = input().strip()
            if not otp.isdigit() or len(otp) != 6:
                print(fail("OTP 6 digit"))
                continue

            tokens = submit_otp(api_key, "SMS", phone_number, otp)
            if not tokens:
                print(fail("OTP salah"))
                continue

            print(ok("Login berhasil"))
            return phone_number, tokens["refresh_token"]

        print(fail("Gagal login"))
        return None
    except Exception as e:
        print(fail(f"Gagal login: {e}"))
        return None


def show_account_menu() -> int | None:
    """Show the account management screen; return the selected user number on switch, None on exit."""
    SESSION.load_tokens()
    in_menu = True
    add_user = False

    while in_menu:
        clear_screen()
        if SESSION.get_active_user() is None or add_user:
            result = _login_prompt(SESSION.api_key)
            if not result:
                print(fail("Gagal menambah akun"))
                pause()
                continue

            number, refresh_token = result
            SESSION.add_refresh_token(int(number), refresh_token)
            SESSION.load_tokens()
            add_user = False
            continue

        users = SESSION.refresh_tokens
        active_user = SESSION.get_active_user()

        print(title("📋 Ganti Nomor", color=C.BLUE))
        if not users:
            print(info("Tidak ada akun tersimpan"))
        else:
            numbers = [str(u.get("number", "")) for u in users]
            types = [str(u.get("subscription_type", "")) for u in users]
            nw, tw = max(map(len, numbers)), max(map(len, types))

            print(f"{'#':>3}  {p('Nomor'.ljust(nw), C.BOLD, C.WHITE)}  {p('Tipe'.center(tw), C.BOLD, C.WHITE)}  Status")
            print(rule(char="-", color=C.BLUE))
            for idx, (user, num, typ) in enumerate(zip(users, numbers, types), 1):
                is_active = active_user and user["number"] == active_user["number"]
                row = f"{idx:>3}  {p(num.ljust(nw), C.BOLD)}  {p(typ.center(tw), C.CYAN)}  "
                row += p("✅ Akun aktif", C.GREEN, C.BOLD) if is_active else p("Belum aktif", C.DIM)
                print(row)

        print(rule(char="-", color=C.BLUE))
        print(p("⚙️ Command:", C.BOLD))
        print(f"{'0':>3}  ➕ Tambah akun")
        print(f"{'00':>3}  ↩️ Kembali")
        print(f"{'del':>3}  🗑 Hapus akun (contoh: del 2)")
        print(f"{'#':>3}  🔢 Ganti akun (ketik nomor urut)")
        choice = input(p("👉 Pilihan: ", C.BOLD))

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
                print(fail("Format: del <nomor>"))
                pause()
                continue
            del_idx = int(parts[1])
            if active_user and users[del_idx - 1]["number"] == active_user["number"]:
                print(fail("Akun aktif tidak bisa dihapus"))
                pause()
                continue
            if not (1 <= del_idx <= len(users)):
                print(fail("Nomor urut tidak valid"))
                pause()
                continue

            user_to_delete = users[del_idx - 1]
            confirm = input(p(f"🗑 Hapus {user_to_delete['number']}? (y/n): ", C.BOLD))
            if confirm.lower() == "y":
                SESSION.remove_refresh_token(user_to_delete["number"])
                SESSION.load_tokens()
                print(ok("Akun dihapus"))
            else:
                print(info("Penghapusan dibatalkan"))
            pause()
            continue

        print(fail("Input tidak valid"))
        pause()
