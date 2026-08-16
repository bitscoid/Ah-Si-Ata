"""Account / login menu: add, switch, remove accounts."""
from __future__ import annotations

from ahsiata.api.auth import get_otp, submit_otp
from ahsiata.core.session import SESSION
from ahsiata.ui.style import C, p, rule, center, disp_w, ok, fail, warn, info

from ahsiata.ui.utils import clear_screen, pause


def _login_prompt(api_key: str) -> tuple[str, str] | None:
    """Run the OTP login flow; return (phone_number, refresh_token) on success."""
    clear_screen()
    print()
    print(rule(char="=", color=C.BLUE))
    print(p(center("📱 Login MyXL", 55), C.BOLD, C.B_WHITE))
    print(rule(char="=", color=C.BLUE))
    print()
    print(p(center("Masukkan nomor XL untuk menerima OTP", 55), C.DIM))
    print(rule(char="-", color=C.BLUE))
    print(p("Nomor XL  : ", C.BOLD), end="")
    phone_number = input().strip()
    if phone_number.startswith("0"):
        phone_number = "62" + phone_number[1:]
    if not phone_number.startswith("628") or len(phone_number) < 10 or len(phone_number) > 14:
        print(fail("Nomor tidak valid. Pakai format 0819… atau 62819…"))
        return None

    try:
        print(p(f"📤 Mengirim OTP ke {phone_number}…", C.DIM))
        subscriber_id = get_otp(phone_number)
        if not subscriber_id:
            print(fail("OTP tidak terkirim. Coba lagi."))
            return None
        print(ok("OTP terkirim"))
        print()
        print(rule(char="=", color=C.BLUE))
        print(p(center("🔑 Verifikasi OTP", 55), C.BOLD, C.B_WHITE))
        print(rule(char="=", color=C.BLUE))
        print()
        print(p(center("Masukkan kode 6 digit yang dikirim via SMS", 55), C.DIM))
        print(rule(char="-", color=C.BLUE))

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

        print()
        print(rule(char="=", color=C.BLUE))
        print(p(center("📋 Ganti Akun", 55), C.BOLD, C.B_WHITE))
        print(rule(char="=", color=C.BLUE))
        print()
        if not users:
            print(info("Tidak ada akun tersimpan"))
        else:
            numbers = [str(u.get("number", "")) for u in users]
            types = [str(u.get("subscription_type", "")) for u in users]
            nw, tw = max(map(len, numbers)), max(map(len, types))

            print(f"{'#':>3}  {p('Nomor'.ljust(nw), C.BOLD, C.WHITE)}  {p('Tipe'.center(tw), C.BOLD, C.WHITE)}  {p('Status'.center(8), C.BOLD, C.WHITE)}")
            print(rule(char="-", color=C.BLUE))
            for idx, (user, num, typ) in enumerate(zip(users, numbers, types), 1):
                is_active = active_user and user["number"] == active_user["number"]
                ic = "✅" if is_active else "💾"
                icon = p(ic, C.GREEN if is_active else C.YELLOW)
                row = f"{idx:>3}  {p(num.ljust(nw), C.BOLD)}  {p(typ.center(tw), C.CYAN)}  "
                pad = 8 - disp_w(ic)
                print(row + " " * (pad // 2) + icon)

        print(rule(char="-", color=C.BLUE))
        print(p(f"{'':>3}  {'A':>2} Tambah    {'D':>2} Hapus    {'B':>2} Kembali", C.DIM))
        print()
        choice = input(p("🧭 Pilih : ", C.YELLOW)).strip()

        if choice.lower() == "b":
            return active_user["number"] if active_user else None

        if choice.lower() == "a":
            add_user = True
            continue

        if choice.isdigit() and 1 <= int(choice) <= len(users):
            return users[int(choice) - 1]["number"]

        if choice.lower().startswith("d"):
            tail = choice[1:]
            if tail == "":
                tail = input(p("🧭 Hapus nomor urut: ", C.BOLD))
            if not tail.isdigit():
                print(fail("Format: D<nomor urut>, contoh: D2"))
                pause()
                continue
            del_idx = int(tail)
            if active_user and users[del_idx - 1]["number"] == active_user["number"]:
                print(fail("Akun aktif tidak bisa dihapus"))
                pause()
                continue
            if not (1 <= del_idx <= len(users)):
                print(fail("Nomor urut tidak valid"))
                pause()
                continue

            user_to_delete = users[del_idx - 1]
            confirm = input(p(f"❌ Hapus {user_to_delete['number']}? (y/n): ", C.BOLD))
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
