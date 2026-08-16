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
            print("Failed to get family data.")
            pause()
            return

        family_detail = res["data"]
        member_info = family_detail.get("member_info", {})
        plan_type = member_info.get("plan_type", "")
        if plan_type == "":
            print("You are not family plan organizer.")
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
        print(f"Shared Quota: {remaining_quota} / {total_quota} | Exp: {end_date}".center(WIDTH))
        print("-" * WIDTH)

        print(f"Members: {len(members) - len(empty_slots)}/{len(members)}:")
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
            print(f"{idx}. {display_msisdn} ({alias}) | {member_type} | Add Chances: {add_chances}/{total_add_chances}")
            print(f"   Usage: {quota_used} / {quota_allocated}")
        print("-" * WIDTH)
        print()
        print("-" * WIDTH)
        print("Options:")
        print("-" * WIDTH)
        print("1. Change Member")
        print("limit <Slot Number> <Quota MB>  - set quota limit")
        print("del <Slot Number>               - remove member from slot")
        print("00. Back to Main Menu")
        print("-" * WIDTH)

        choice = input("Enter your choice: ").strip()
        if choice == "00":
            return

        if choice == "1":
            slot_idx = input("Enter the slot number: ").strip()
            target_msisdn = input("Enter the new member's phone number (start with 62): ").strip()
            parent_alias = input("Enter your alias: ").strip()
            child_alias = input("Enter the new member's alias: ").strip()
            try:
                slot_idx_int = int(slot_idx)
                if not (1 <= slot_idx_int <= len(members)):
                    print("Invalid slot number.")
                    pause()
                    continue
                if members[slot_idx_int - 1].get("msisdn") != "":
                    print("Selected slot is not empty. Cannot change member.")
                    pause()
                    continue

                family_member_id = members[slot_idx_int - 1]["family_member_id"]
                slot_id = members[slot_idx_int - 1]["slot_id"]

                validation = validate_msisdn(api_key, tokens, target_msisdn)
                if validation.get("status", "").lower() != "success":
                    print(f"MSISDN validation failed: {json.dumps(validation, indent=2)}")
                    pause()
                    continue
                print("MSISDN validation successful.")

                if validation["data"].get("family_plan_role", "") != "NO_ROLE":
                    print(f"{target_msisdn} is already part of another family plan.")
                    pause()
                    continue

                if input(f"Are you sure? (y/n): ").strip().lower() != "y":
                    print("Cancelled.")
                    pause()
                    continue

                change_res = change_member(api_key, tokens, parent_alias, child_alias, slot_id, family_member_id, target_msisdn)
                if change_res.get("status") == "SUCCESS":
                    print("Member changed successfully.")
                else:
                    print(f"Failed: {change_res.get('message', 'Unknown error')}")
                print(json.dumps(change_res, indent=4))
            except ValueError:
                print("Invalid slot number.")
            pause()

        elif choice.startswith("del "):
            try:
                _, slot_num = choice.split(" ", 1)
                slot_idx_int = int(slot_num)
                if not (1 <= slot_idx_int <= len(members)):
                    print("Invalid slot number.")
                    pause()
                    continue
                member = members[slot_idx_int - 1]
                if not member.get("msisdn"):
                    print("Slot already empty.")
                    pause()
                    continue
                if input(f"Remove {member.get('msisdn')} from slot {slot_idx_int}? (y/n): ").strip().lower() != "y":
                    print("Cancelled.")
                    pause()
                    continue
                res = remove_member(api_key, tokens, member["family_member_id"])
                if res.get("status") == "SUCCESS":
                    print("Member removed.")
                else:
                    print(f"Failed: {res.get('message', 'Unknown error')}")
                print(json.dumps(res, indent=4))
            except ValueError:
                print("Invalid slot number.")
            pause()

        elif choice.startswith("limit "):
            try:
                _, slot_num, new_quota_mb = choice.split(" ", 2)
                slot_idx_int = int(slot_num)
                new_quota_mb_int = int(new_quota_mb)
                if not (1 <= slot_idx_int <= len(members)):
                    print("Invalid slot number.")
                    pause()
                    continue
                member = members[slot_idx_int - 1]
                if not member.get("msisdn"):
                    print("Slot empty.")
                    pause()
                    continue
                original = member.get("usage", {}).get("quota_allocated", 0)
                new_bytes = new_quota_mb_int * 1024 * 1024
                res = set_quota_limit(api_key, tokens, original, new_bytes, member["family_member_id"])
                if res.get("status") == "SUCCESS":
                    print("Quota limit set.")
                else:
                    print(f"Failed: {res.get('message', 'Unknown error')}")
                print(json.dumps(res, indent=4))
            except ValueError:
                print("Invalid input.")
            pause()
