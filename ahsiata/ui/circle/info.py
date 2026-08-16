"""Circle (Family Hub) info + bonus sub-menus."""
from __future__ import annotations

from datetime import datetime

from ahsiata.api.circle import (
    accept_circle_invitation,
    get_bonus_data,
    get_group_data,
    get_group_members,
    invite_circle_member,
    remove_circle_member,
    spending_tracker,
    validate_circle_member,
    create_circle,
)
from ahsiata.api.encrypt import decrypt_circle_msisdn
from ahsiata.core.session import SESSION
from ahsiata.ui.style import C, p, title, rule, ok, fail, warn, info
from ahsiata.ui.utils import clear_screen, format_quota_byte, pause

WIDTH = 55


def show_circle_creation(api_key: str, tokens: dict) -> None:
    clear_screen()
    print(title("🫂 Buat Circle", color=C.MAGENTA))

    parent_name = input("🧭 Nama Anda (Parent): ")
    group_name = input("🧭 Nama Circle: ")
    member_msisdn = input("🧭 MSISDN member (628…): ")
    member_name = input("🧭 Nama member: ")

    create_res = create_circle(api_key, tokens, parent_name, group_name, member_msisdn, member_name)
    if isinstance(create_res, dict) and create_res.get("status") == "SUCCESS":
        print(ok("Circle berhasil dibuat."))
    else:
        print(fail("Gagal membuat Circle."))
    pause()


def _show_bonus_list(api_key: str, tokens: dict, parent_subs_id: str, family_id: str) -> None:
    while True:
        clear_screen()
        print(info("⏳ Mengambil data bonus…"))
        bonus_data = get_bonus_data(api_key, tokens, parent_subs_id, family_id)
        if bonus_data.get("status") != "SUCCESS":
            print(fail("Gagal mengambil data bonus."))
            pause()
            return

        bonus_list = bonus_data.get("data", {}).get("bonuses", [])
        if not bonus_list:
            print(warn("Tidak ada data bonus tersedia."))
            pause()
            return

        print(rule(char="=", color=C.YELLOW))
        print(title("🏆 Bonus Circle", color=C.YELLOW))
        print(rule(char="=", color=C.YELLOW))

        for idx, bonus in enumerate(bonus_list, start=1):
            print(f"{idx}. {p(bonus.get('name', 'N/A'), C.BOLD, C.WHITE)} | 🏷 {bonus.get('bonus_type', 'N/A')}")
            print(f"   🎯 Aksi: {bonus.get('action_type', 'N/A')} | Param: {bonus.get('action_param', 'N/A')}")

        print(rule(char="-", color=C.YELLOW))
        print(p(f"{'':>3}  {'B':>2} Kembali", C.DIM))
        print()
        choice = input(p("🧭 Pilih : ", C.YELLOW)).strip()
        if choice.lower() == "b":
            return
        if not choice.isdigit() or not (1 <= int(choice) <= len(bonus_list)):
            print(fail("Pilihan tidak valid."))
            pause()
            return

        selected = bonus_list[int(choice) - 1]
        action_type = selected.get("action_type", "")
        action_param = selected.get("action_param", "")

        if action_type == "PLP":
            from ahsiata.ui.package.list import get_packages_by_family
            get_packages_by_family(action_param)
        elif action_type == "PDP":
            from ahsiata.ui.package.details import show_package_details
            show_package_details(api_key, tokens, action_param, False)
        else:
            print(fail(f"Tipe aksi yang tidak ditangani: {action_type}"))
            pause()


def show_circle_info(api_key: str, tokens: dict) -> None:
    user = SESSION.get_active_user()
    my_msisdn = user.get("number", "") if user else ""

    while True:
        clear_screen()
        group_res = get_group_data(api_key, tokens)
        if group_res.get("status") != "SUCCESS":
            print(fail("Gagal mengambil data circle."))
            pause()
            return

        group_data = group_res.get("data", {})
        group_id = group_data.get("group_id", "")
        if not group_id:
            print(warn("Anda tidak tergabung dalam Circle apa pun."))
            if input(p("🧭 Buat baru? (y/n): ", C.YELLOW)).lower() == "y":
                show_circle_creation(api_key, tokens)
            else:
                pause()
            return

        if group_data.get("group_status") == "BLOCKED":
            print(fail("Circle ini saat ini diblokir."))
            pause()
            return

        group_name = group_data.get("group_name", "N/A")
        owner_name = group_data.get("owner_name", "N/A")

        members_res = get_group_members(api_key, tokens, group_id)
        if members_res.get("status") != "SUCCESS":
            print(fail("Gagal mengambil anggota Circle."))
            pause()
            return

        members = members_res.get("data", {}).get("members", [])
        if not members:
            print(fail("Tidak ada anggota ditemukan."))
            pause()
            return

        parent_member_id = ""
        parent_subs_id = ""
        parrent_msisdn = ""
        for member in members:
            if member.get("member_role") == "PARENT":
                parent_member_id = member.get("member_id", "")
                parent_subs_id = member.get("subscriber_number", "")
                parrent_msisdn = decrypt_circle_msisdn(api_key, member.get("msisdn", ""))

        package = members_res.get("data", {}).get("package", {})
        package_name = package.get("name", "N/A")
        benefit = package.get("benefit", {})
        allocation = format_quota_byte(benefit.get("allocation", 0))
        remaining = format_quota_byte(benefit.get("remaining", 0))

        spending_res = spending_tracker(api_key, tokens, parent_subs_id, group_id)
        if spending_res.get("status") != "SUCCESS":
            print(fail("Gagal mengambil data spending tracker."))
            pause()
            return
        spending = spending_res.get("data", {})
        spend = spending.get("spend", 0)
        target = spending.get("target", 0)

        clear_screen()
        print(rule(char="=", color=C.MAGENTA))
        print(title(f"🫂 {group_name}", color=C.MAGENTA))
        print(rule(char="=", color=C.MAGENTA))
        print(p(f"👤 Pemilik: {owner_name} {parrent_msisdn}", C.CYAN))
        print(rule())
        print(p(f"📦 Paket: {package_name} | {remaining} / {allocation}", C.BOLD, C.YELLOW))
        print(rule())
        print(p(f"💸 Pengeluaran: Rp{spend:,} / Rp{target:,}", C.BOLD))

        for idx, member in enumerate(members, start=1):
            msisdn = decrypt_circle_msisdn(api_key, member.get("msisdn", ""))
            member_role = member.get("member_role", "N/A")
            member_name = member.get("member_name", "N/A")
            join_ts = member.get("join_date", 0)
            slot_type = member.get("slot_type", "N/A")
            member_status = member.get("status", "N/A")
            allocated = format_quota_byte(member.get("allocation", 0))
            used = format_quota_byte(member.get("allocation", 0) - member.get("remaining", 0))

            display_msisdn = msisdn if msisdn else "<No Number>"
            me_mark = "(You)" if str(msisdn) == str(my_msisdn) else ""
            member_type = "Parent" if member_role == "PARENT" else "Member"

            print(f"{idx}. {p(display_msisdn, C.BOLD)} ({member_name}) | {p(member_type, C.CYAN)} {p('(You)', C.GREEN) if me_mark else ''}")
            print(f"   📅 Bergabung: {datetime.fromtimestamp(join_ts).strftime('%Y-%m-%d')} | 🔢 Slot: {slot_type} | 📊 Status: {member_status}")
            print(p(f"   📊 Pemakaian: {used} / {allocated}", C.YELLOW))
            print(rule())

        print(rule(char="-", color=C.MAGENTA))
        print(p("⚙️ Opsi:", C.BOLD, C.WHITE))
        print("1. ➕ Undang Member")
        print("del <nomor> — ❌ hapus")
        print("acc <nomor> — ✔️ terima undangan")
        print("2. 🏆 Bonus Circle")
        print(p(f"{'':>3}  {'B':>2} Kembali", C.DIM))
        print()
        choice = input(p("🧭 Pilih : ", C.YELLOW)).strip()

        if choice.lower() == "b":
            return

        if choice == "1":
            msisdn_to_invite = input(p("🧭 MSISDN diundang (628…): ", C.YELLOW))
            validate_res = validate_circle_member(api_key, tokens, msisdn_to_invite)
            if validate_res.get("status") == "SUCCESS":
                if validate_res.get("data", {}).get("response_code", "") != "200-2001":
                    print(fail(f"Tidak dapat mengundang: {validate_res.get('data', {}).get('message', 'Unknown')}"))
                    pause()
                    continue
            member_name = input(p("🧭 Nama member: ", C.YELLOW))
            invite_res = invite_circle_member(api_key, tokens, msisdn_to_invite, member_name, group_id, parent_member_id)
            if invite_res.get("status") == "SUCCESS" and invite_res.get("data", {}).get("response_code", "") == "200-00":
                print(ok(f"Undangan terkirim ke {msisdn_to_invite}."))
            else:
                print(fail(f"Gagal: {invite_res.get('data', {}).get('message', 'Unknown')}"))
            pause()

        elif choice.startswith("del "):
            try:
                idx = int(choice.split(" ", 1)[1])
                if not (1 <= idx <= len(members)):
                    print(fail("Nomor member tidak valid."))
                    pause()
                    continue
                target = members[idx - 1]
                if target.get("member_role") == "PARENT":
                    print(fail("Tidak dapat menghapus parent."))
                    pause()
                    continue
                is_last_member = len(members) == 2
                if is_last_member:
                    print(fail("Tidak dapat menghapus member terakhir."))
                    pause()
                    continue
                msisdn = decrypt_circle_msisdn(api_key, target.get("msisdn", ""))
                if input(p(f"🧭 Hapus {msisdn}? (y/n): ", C.YELLOW)).lower() != "y":
                    print(warn("Dibatalkan."))
                    pause()
                    continue
                res = remove_circle_member(api_key, tokens, target["member_id"], group_id, parent_member_id, is_last_member)
                if res.get("status") == "SUCCESS":
                    print(ok(f"{msisdn} dihapus."))
                else:
                    print(fail(f"Error: {res}"))
            except ValueError:
                print(fail("Input tidak valid."))
            pause()

        elif choice.startswith("acc "):
            try:
                idx = int(choice.split(" ", 1)[1])
                if not (1 <= idx <= len(members)):
                    print(fail("Nomor member tidak valid."))
                    pause()
                    continue
                target = members[idx - 1]
                if target.get("status") != "INVITED":
                    print(fail("Tidak dalam status diundang."))
                    pause()
                    continue
                msisdn = decrypt_circle_msisdn(api_key, target.get("msisdn", ""))
                if input(p(f"🧭 Terima undangan untuk {msisdn}? (y/n): ", C.YELLOW)).lower() != "y":
                    print(warn("Dibatalkan."))
                    pause()
                    continue
                res = accept_circle_invitation(api_key, tokens, group_id, target["member_id"])
                if res.get("status") == "SUCCESS":
                    print(ok(f"Undangan untuk {msisdn} diterima."))
                else:
                    print(fail(f"Error: {res}"))
            except ValueError:
                print(fail("Input tidak valid."))
            pause()

        elif choice == "2":
            _show_bonus_list(api_key, tokens, parent_subs_id, group_id)
