"""Notification menu: list + mark-all-read."""
from __future__ import annotations

from ahsiata.api.notifications import get_notification_detail, get_notifications
from ahsiata.core.session import SESSION
from ahsiata.ui.utils import clear_screen, pause


def show_notification_menu() -> None:
    user = SESSION.get_active_user()
    tokens = user["tokens"]

    while True:
        clear_screen()
        print("=" * 55)
        print("Notifikasi".center(55))
        print("=" * 55)
        res = get_notifications(SESSION.api_key, tokens)
        if not isinstance(res, dict):
            print("Failed to fetch notifications.")
            pause()
            return

        notifications = res.get("data", {}).get("notifications", [])
        unread = sum(1 for n in notifications if n.get("is_read") is False)
        print(f"Total notifications: {len(notifications)} | Unread: {unread}")
        print("-" * 55)

        for idx, n in enumerate(notifications, start=1):
            status = "READ" if n.get("is_read") else "UNREAD"
            print(f"{idx}. [{status}] {n.get('brief_message', n.get('title', ''))}")

        print("-" * 55)
        print("1. Tandai semua sudah dibaca")
        print("00. Back to Main Menu")
        choice = input("Enter your choice: ")

        if choice == "00":
            return
        if choice == "1":
            for n in notifications:
                if n.get("is_read") is False:
                    get_notification_detail(SESSION.api_key, tokens, n.get("id", ""))
            print("All notifications marked as read.")
            pause()
