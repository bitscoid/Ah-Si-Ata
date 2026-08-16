"""Family Plan menu: change member, remove, set quota limit."""
from __future__ import annotations

from datetime import datetime
import json

from ahsiata.api.family_plan import (
    change_member,
    get_family_data,
    remove_member,
    set_quota_limit,
    validate_msisdn,
)
from ahsiata.ui.utils import clear_screen, format_quota_byte, pause

WIDTH = 55


def show_family_info(api_key: str, tokens: dict) -> None:
    while True:
        clear_screen()
        res = get_family_data(api_key, tokens)
        if not res.get("data"):
            print("Gagal mendapatkan data family.")
            pause()
            return

        family_detail = res["data"]
        member_info = family_detail.get("member_info", {})
        plan_type = member_info.get("plan_type", "")
        if plan_type == "":
            print("Anda bukan organizer family plan.")
            pause()
            return

        parent_msisdn = member_info.get("parent_msisdn", "N/A")
        members = member_info.get("members", [])
        empty_slots = [slot for slot in members if slot.get("msisdn") == ""]

        total_quota = format_quota_byte(member_info.get("total_quota", 0))
        remaining_quota = format_quota_byte(member_info.get("remaining_quota", 0))
        end_date_ts = member_info.get("end_date", 0)
        end_date = datetime.fromtimestamp(end_date_ts).strftime("%Y-%m-%d") if end_date_ts else "N/A"

        clear_screen()
        print("-" * WIDTH)
        print(f"Plan: {plan_type} | Parent: {parent_msisdn}".center(WIDTH))
        print(f"Kuota Bersama: {remaining_quota} / {total_quota} | Berlaku s/d: {end_date}".center(WIDTH))
        print("-" * WIDTH)

        print(f"Anggota: {len(members) - len(empty_slots)}/{len(members)}:")
        for idx, member in enumerate(members, start=1):
            print("-" * WIDTH)
            msisdn = member.get("msisdn", "N/A")
            display_msisdn = msisdn if msisdn else "<Empty Slot>"
            alias = member.get("alias", "N/A")
            member_type = member.get("member_type", "N/A")
            add_chances = member.get("add_chances", 0)
            total_add_chances = member.get("total_add_chances", 0)

            usage = member.get("usage", {})
            quota_allocated = format_quota_byte(usage.get("quota_allocated", 0))
            quota_used = format_quota_byte(usage.get("quota_used", 0))
            print(f"{idx}. {display_msisdn} ({alias}) | {member_type} | Tambah Kesempatan: {add_chances}/{total_add_chances}")
            print(f"   Pemakaian: {quota_used} / {quota_allocated}")
        print("-" * WIDTH)
        print()
        print("-" * WIDTH)
        print("Opsi:")
        print("-" * WIDTH)
        print("1. Ganti Member")
        print("limit <Nomor Slot> <Kuota MB>  - atur batas kuota")
        print("del <Nomor Slot>               - hapus member dari slot")
        print("00. Kembali ke menu utama")
        print("-" * WIDTH)

        choice = input("Masukkan pilihan Anda: ").strip()
        if choice == "00":
            return

        if choice == "1":
            slot_idx = input("Masukkan nomor slot: ").strip()
            target_msisdn = input("Masukkan nomor telepon member baru (awali dengan 62): ").strip()
            parent_alias = input("Masukkan alias Anda: ").strip()
            child_alias = input("Masukkan alias member baru: ").strip()
            try:
                slot_idx_int = int(slot_idx)
                if not (1 <= slot_idx_int <= len(members)):
                    print("Nomor slot tidak valid.")
                    pause()
                    continue
                if members[slot_idx_int - 1].get("msisdn") != "":
                    print("Slot terpilih tidak kosong. Tidak dapat mengganti member.")
                    pause()
                    continue

                family_member_id = members[slot_idx_int - 1]["family_member_id"]
                slot_id = members[slot_idx_int - 1]["slot_id"]

                validation = validate_msisdn(api_key, tokens, target_msisdn)
                if validation.get("status", "").lower() != "success":
                    print(f"Validasi MSISDN gagal: {json.dumps(validation, indent=2)}")
                    pause()
                    continue
                print("Validasi MSISDN berhasil.")

                if validation["data"].get("family_plan_role", "") != "NO_ROLE":
                    print(f"{target_msisdn} sudah tergabung dalam family plan lain.")
                    pause()
                    continue

                if input("Apakah Anda yakin? (y/n): ").strip().lower() != "y":
                    print("Dibatalkan.")
                    pause()
                    continue

                change_res = change_member(api_key, tokens, parent_alias, child_alias, slot_id, family_member_id, target_msisdn)
                if change_res.get("status") == "SUCCESS":
                    print("Member berhasil diganti.")
                else:
                    print(f"Gagal: {change_res.get('message', 'Unknown error')}")
                print(json.dumps(change_res, indent=4))
            except ValueError:
                print("Nomor slot tidak valid.")
            pause()

        elif choice.startswith("del "):
            try:
                _, slot_num = choice.split(" ", 1)
                slot_idx_int = int(slot_num)
                if not (1 <= slot_idx_int <= len(members)):
                    print("Nomor slot tidak valid.")
                    pause()
                    continue
                member = members[slot_idx_int - 1]
                if not member.get("msisdn"):
                    print("Slot sudah kosong.")
                    pause()
                    continue
                if input(f"Hapus {member.get('msisdn')} dari slot {slot_idx_int}? (y/n): ").strip().lower() != "y":
                    print("Dibatalkan.")
                    pause()
                    continue
                res = remove_member(api_key, tokens, member["family_member_id"])
                if res.get("status") == "SUCCESS":
                    print("Member dihapus.")
                else:
                    print(f"Gagal: {res.get('message', 'Unknown error')}")
                print(json.dumps(res, indent=4))
            except ValueError:
                print("Nomor slot tidak valid.")
            pause()

        elif choice.startswith("limit "):
            try:
                _, slot_num, new_quota_mb = choice.split(" ", 2)
                slot_idx_int = int(slot_num)
                new_quota_mb_int = int(new_quota_mb)
                if not (1 <= slot_idx_int <= len(members)):
                    print("Nomor slot tidak valid.")
                    pause()
                    continue
                member = members[slot_idx_int - 1]
                if not member.get("msisdn"):
                    print("Slot kosong.")
                    pause()
                    continue
                original = member.get("usage", {}).get("quota_allocated", 0)
                new_bytes = new_quota_mb_int * 1024 * 1024
                res = set_quota_limit(api_key, tokens, original, new_bytes, member["family_member_id"])
                if res.get("status") == "SUCCESS":
                    print("Batas kuota diatur.")
                else:
                    print(f"Gagal: {res.get('message', 'Unknown error')}")
                print(json.dumps(res, indent=4))
            except ValueError:
                print("Input tidak valid.")
            pause()
