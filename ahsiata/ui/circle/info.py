"""Circle (Family Hub) info + bonus sub-menus."""
from __future__ import annotations

from datetime import datetime
import json

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
from ahsiata.ui.utils import clear_screen, format_quota_byte, pause

WIDTH = 55


def show_circle_creation(api_key: str, tokens: dict) -> None:
    clear_screen()
    print("Create a new Circle")
    print("-" * WIDTH)

    parent_name = input("Enter your name (Parent): ")
    group_name = input("Enter Circle name: ")
    member_msisdn = input("Enter initial member's MSISDN (e.g., 6281234567890): ")
    member_name = input("Enter initial member's name: ")

    create_res = create_circle(api_key, tokens, parent_name, group_name, member_msisdn, member_name)
    print("Server Response:")
    print(json.dumps(create_res, indent=2))
    pause()


def _show_bonus_list(api_key: str, tokens: dict, parent_subs_id: str, family_id: str) -> None:
    clear_screen()
    print("Fetching bonus data...")
    bonus_data = get_bonus_data(api_key, tokens, parent_subs_id, family_id)
    if bonus_data.get("status") != "SUCCESS":
        print("Failed to fetch bonus data.")
        pause()
        return

    bonus_list = bonus_data.get("data", {}).get("bonuses", [])
    if not bonus_list:
        print("No bonus data available.")
        pause()
        return

    print("=" * WIDTH)
    print("Circle Bonus List".center(WIDTH))
    print("=" * WIDTH)

    for idx, bonus in enumerate(bonus_list, start=1):
        print(f"{idx}. {bonus.get('name', 'N/A')} | Type: {bonus.get('bonus_type', 'N/A')}")
        print(f"   Action: {bonus.get('action_type', 'N/A')} | Param: {bonus.get('action_param', 'N/A')}")

    print("-" * WIDTH)
    print("Enter the number of the bonus to view detail.")
    print("00. Back")
    choice = input("Pilih opsi: ")
    if choice == "00":
        return
    if not choice.isdigit() or not (1 <= int(choice) <= len(bonus_list)):
        print("Invalid choice.")
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
        print(f"Unhandled Action Type: {action_type}")
        pause()


def show_circle_info(api_key: str, tokens: dict) -> None:
    user = SESSION.get_active_user()
    my_msisdn = user.get("number", "") if user else ""

    while True:
        clear_screen()
        group_res = get_group_data(api_key, tokens)
        if group_res.get("status") != "SUCCESS":
            print("Failed to fetch circle data.")
            pause()
            return

        group_data = group_res.get("data", {})
        group_id = group_data.get("group_id", "")
        if not group_id:
            print("You are not part of any Circle.")
            if input("Create new? (y/n): ").lower() == "y":
                show_circle_creation(api_key, tokens)
            else:
                pause()
            return

        if group_data.get("group_status") == "BLOCKED":
            print("This Circle is currently blocked.")
            pause()
            return

        group_name = group_data.get("group_name", "N/A")
        owner_name = group_data.get("owner_name", "N/A")

        members_res = get_group_members(api_key, tokens, group_id)
        if members_res.get("status") != "SUCCESS":
            print("Failed to fetch circle members.")
            pause()
            return

        members = members_res.get("data", {}).get("members", [])
        if not members:
            print("No members found.")
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
            print("Failed to fetch spending tracker data.")
            pause()
            return
        spending = spending_res.get("data", {})
        spend = spending.get("spend", 0)
        target = spending.get("target", 0)

        clear_screen()
        print("=" * WIDTH)
        print(f"Circle: {group_name}".center(WIDTH))
        print(f"Owner: {owner_name} {parrent_msisdn}".center(WIDTH))
        print("-" * WIDTH)
        print(f"Package: {package_name} | {remaining} / {allocation}".center(WIDTH))
        print("-" * WIDTH)
        print(f"Spending: Rp{spend:,} / Rp{target:,}".center(WIDTH))
        print("=" * WIDTH)

        for idx, member in enumerate(members, start=1):
            msisdn = decrypt_circle_msisdn(api_key, member.get("msisdn", ""))
            member_id = member.get("member_id", "")
            member_role = member.get("member_role", "N/A")
            member_name = member.get("member_name", "N/A")
            join_ts = member.get("join_date", 0)
            slot_type = member.get("slot_type", "N/A")
            member_status = member.get("status", "N/A")
            allocated = format_quota_byte(member.get("allocation", 0))
            remaining_mb = format_quota_byte(member.get("remaining", 0))
            used = format_quota_byte(member.get("allocation", 0) - member.get("remaining", 0))

            display_msisdn = msisdn if msisdn else "<No Number>"
            me_mark = "(You)" if str(msisdn) == str(my_msisdn) else ""
            member_type = "Parent" if member_role == "PARENT" else "Member"

            print(f"{idx}. {display_msisdn} ({member_name}) | {member_type} {me_mark}")
            print(f"   Joined: {datetime.fromtimestamp(join_ts).strftime('%Y-%m-%d')} | Slot: {slot_type} | Status: {member_status}")
            print(f"   Usage: {used} / {allocated}")
            print("-" * WIDTH)

        print("-" * WIDTH)
        print("Options:")
        print("1. Invite Member to Circle")
        print("del <number> - Remove Member")
        print("acc <number> - Accept Invitation")
        print("2. View Circle Bonus List")
        print("00. Kembali ke menu utama")
        choice = input("Pilih opsi: ")

        if choice == "00":
            return

        if choice == "1":
            msisdn_to_invite = input("MSISDN to invite (628...): ")
            validate_res = validate_circle_member(api_key, tokens, msisdn_to_invite)
            if validate_res.get("status") == "SUCCESS":
                if validate_res.get("data", {}).get("response_code", "") != "200-2001":
                    print(f"Cannot invite: {validate_res.get('data', {}).get('message', 'Unknown')}")
                    pause()
                    continue
            member_name = input("Member name: ")
            invite_res = invite_circle_member(api_key, tokens, msisdn_to_invite, member_name, group_id, parent_member_id)
            if invite_res.get("status") == "SUCCESS" and invite_res.get("data", {}).get("response_code", "") == "200-00":
                print(f"Invitation sent to {msisdn_to_invite}.")
            else:
                print(f"Failed: {invite_res.get('data', {}).get('message', 'Unknown')}")
            pause()

        elif choice.startswith("del "):
            try:
                idx = int(choice.split(" ", 1)[1])
                if not (1 <= idx <= len(members)):
                    print("Invalid member number.")
                    pause()
                    continue
                target = members[idx - 1]
                if target.get("member_role") == "PARENT":
                    print("Cannot remove the parent.")
                    pause()
                    continue
                is_last_member = len(members) == 2
                if is_last_member:
                    print("Cannot remove the last member.")
                    pause()
                    continue
                msisdn = decrypt_circle_msisdn(api_key, target.get("msisdn", ""))
                if input(f"Remove {msisdn}? (y/n): ").lower() != "y":
                    print("Cancelled.")
                    pause()
                    continue
                res = remove_circle_member(api_key, tokens, target["member_id"], group_id, parent_member_id, is_last_member)
                if res.get("status") == "SUCCESS":
                    print(f"{msisdn} removed.")
                else:
                    print(f"Error: {res}")
            except ValueError:
                print("Invalid input.")
            pause()

        elif choice.startswith("acc "):
            try:
                idx = int(choice.split(" ", 1)[1])
                if not (1 <= idx <= len(members)):
                    print("Invalid member number.")
                    pause()
                    continue
                target = members[idx - 1]
                if target.get("status") != "INVITED":
                    print("Not in invited state.")
                    pause()
                    continue
                msisdn = decrypt_circle_msisdn(api_key, target.get("msisdn", ""))
                if input(f"Accept invitation for {msisdn}? (y/n): ").lower() != "y":
                    print("Cancelled.")
                    pause()
                    continue
                res = accept_circle_invitation(api_key, tokens, group_id, target["member_id"])
                if res.get("status") == "SUCCESS":
                    print(f"Invitation for {msisdn} accepted.")
                else:
                    print(f"Error: {res}")
            except ValueError:
                print("Invalid input.")
            pause()

        elif choice == "2":
            _show_bonus_list(api_key, tokens, parent_subs_id, group_id)
