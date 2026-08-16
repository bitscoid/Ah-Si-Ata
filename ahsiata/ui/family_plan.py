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
from ahsiata.ui.style import C, p, title, rule, center, ok, fail, warn, info
from ahsiata.ui.utils import clear_screen, format_quota_byte, pause

WIDTH = 55


def show_family_info(api_key: str, tokens: dict) -> None:
    while True:
        clear_screen()
        res = get_family_data(api_key, tokens)
        if not res.get("data"):
            print(fail("Gagal mendapatkan data family."))
            pause()
            return

        family_detail = res["data"]
        member_info = family_detail.get("member_info", {})
        plan_type = member_info.get("plan_type", "")
        if plan_type == "":
            print(fail("Anda bukan organizer family plan."))
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
        print(p(center(f"👨👩👧 Plan: {plan_type} | 🧑 Parent: {parent_msisdn}", WIDTH), C.BOLD, C.CYAN))
        print(p(center(f"📦 Kuota: {remaining_quota} / {total_quota} | ⏳ s/d: {end_date}", WIDTH), C.BOLD, C.YELLOW))
        print(rule())

        print(p(f"👥 Anggota: {len(members) - len(empty_slots)}/{len(members)}:", C.BOLD))
        for idx, member in enumerate(members, start=1):
            print(rule())
            msisdn = member.get("msisdn", "N/A")
            display_msisdn = msisdn if msisdn else "<Empty Slot>"
            msisdn_str = p(display_msisdn, C.BOLD, C.WHITE) if msisdn else p("<Kosong>", C.DIM)
            alias = member.get("alias", "N/A")
            member_type = member.get("member_type", "N/A")
            add_chances = member.get("add_chances", 0)
            total_add_chances = member.get("total_add_chances", 0)

            usage = member.get("usage", {})
            quota_allocated = format_quota_byte(usage.get("quota_allocated", 0))
            quota_used = format_quota_byte(usage.get("quota_used", 0))
            print(f"{idx}. {msisdn_str} ({alias}) | {p(member_type, C.CYAN)} | ➕ {add_chances}/{total_add_chances}")
            print(f"   📊 Pemakaian: {p(quota_used, C.YELLOW)} / {p(quota_allocated, C.YELLOW)}")
        print(rule())
        print()
        print(rule())
        print(p("⚙️ Opsi:", C.BOLD, C.WHITE))
        print(rule())
        print("1. 🔄 Ganti Member")
        print("limit <slot> <MB> — 🔒 batas kuota")
        print("del <slot> — 🗑 hapus member")
        print("00. ↩️ Kembali")
        print(rule())

        choice = input("👉 Pilih: ").strip()
        if choice == "00":
            return

        if choice == "1":
            slot_idx = input("👉 Nomor slot: ").strip()
            target_msisdn = input("👉 Nomor member (62…): ").strip()
            parent_alias = input("👉 Alias Anda: ").strip()
            child_alias = input("👉 Alias member: ").strip()
            try:
                slot_idx_int = int(slot_idx)
                if not (1 <= slot_idx_int <= len(members)):
                    print(fail("Nomor slot tidak valid."))
                    pause()
                    continue
                if members[slot_idx_int - 1].get("msisdn") != "":
                    print(fail("Slot terpilih tidak kosong."))
                    pause()
                    continue

                family_member_id = members[slot_idx_int - 1]["family_member_id"]
                slot_id = members[slot_idx_int - 1]["slot_id"]

                validation = validate_msisdn(api_key, tokens, target_msisdn)
                if validation.get("status", "").lower() != "success":
                    print(fail(f"Validasi MSISDN gagal: {json.dumps(validation, indent=2)}"))
                    pause()
                    continue
                print(ok("Validasi MSISDN berhasil."))

                if validation["data"].get("family_plan_role", "") != "NO_ROLE":
                    print(fail(f"{target_msisdn} sudah tergabung dalam family plan lain."))
                    pause()
                    continue

                if input("👉 Yakin? (y/n): ").strip().lower() != "y":
                    print(warn("Dibatalkan."))
                    pause()
                    continue

                change_res = change_member(api_key, tokens, parent_alias, child_alias, slot_id, family_member_id, target_msisdn)
                if change_res.get("status") == "SUCCESS":
                    print(ok("Member berhasil diganti."))
                else:
                    print(fail(f"Gagal: {change_res.get('message', 'Unknown error')}"))
                print(json.dumps(change_res, indent=4))
            except ValueError:
                print(fail("Nomor slot tidak valid."))
            pause()

        elif choice.startswith("del "):
            try:
                _, slot_num = choice.split(" ", 1)
                slot_idx_int = int(slot_num)
                if not (1 <= slot_idx_int <= len(members)):
                    print(fail("Nomor slot tidak valid."))
                    pause()
                    continue
                member = members[slot_idx_int - 1]
                if not member.get("msisdn"):
                    print(warn("Slot sudah kosong."))
                    pause()
                    continue
                if input(f"👉 Hapus {member.get('msisdn')} dari slot {slot_idx_int}? (y/n): ").strip().lower() != "y":
                    print(warn("Dibatalkan."))
                    pause()
                    continue
                res = remove_member(api_key, tokens, member["family_member_id"])
                if res.get("status") == "SUCCESS":
                    print(ok("Member dihapus."))
                else:
                    print(fail(f"Gagal: {res.get('message', 'Unknown error')}"))
                print(json.dumps(res, indent=4))
            except ValueError:
                print(fail("Nomor slot tidak valid."))
            pause()

        elif choice.startswith("limit "):
            try:
                _, slot_num, new_quota_mb = choice.split(" ", 2)
                slot_idx_int = int(slot_num)
                new_quota_mb_int = int(new_quota_mb)
                if not (1 <= slot_idx_int <= len(members)):
                    print(fail("Nomor slot tidak valid."))
                    pause()
                    continue
                member = members[slot_idx_int - 1]
                if not member.get("msisdn"):
                    print(warn("Slot kosong."))
                    pause()
                    continue
                original = member.get("usage", {}).get("quota_allocated", 0)
                new_bytes = new_quota_mb_int * 1024 * 1024
                res = set_quota_limit(api_key, tokens, original, new_bytes, member["family_member_id"])
                if res.get("status") == "SUCCESS":
                    print(ok("Batas kuota diatur."))
                else:
                    print(fail(f"Gagal: {res.get('message', 'Unknown error')}"))
                print(json.dumps(res, indent=4))
            except ValueError:
                print(fail("Input tidak valid."))
            pause()
