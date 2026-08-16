"""Notification menu: list + mark-all-read."""
from __future__ import annotations

from ahsiata.api.notifications import get_notification_detail, get_notifications
from ahsiata.core.session import SESSION
from ahsiata.ui.style import C, p, title, rule, ok, fail
from ahsiata.ui.utils import clear_screen, pause


def show_notification_menu() -> None:
    user = SESSION.get_active_user()
    tokens = user["tokens"]

    while True:
        clear_screen()
        print(title("🔔 Notifikasi", color=C.MAGENTA))
        res = get_notifications(SESSION.api_key, tokens)
        if not isinstance(res, dict):
            print(fail("Gagal mengambil notifikasi"))
            pause()
            return

        notifications = res.get("data", {}).get("notifications", [])
        unread = sum(1 for n in notifications if n.get("is_read") is False)
        print(p(f"📩 Total: {len(notifications)} | 🔴 Belum dibaca: {unread}", C.BOLD))
        print(rule(color=C.BLUE))

        for idx, n in enumerate(notifications, start=1):
            status_emoji = "✅" if n.get("is_read") else "🔴"
            print(f"{idx}. {status_emoji} {n.get('brief_message', n.get('title', ''))}")

        print(rule(color=C.BLUE))
        print("1. ✅ Tandai dibaca semua")
        print("00. ↩️ Kembali")
        choice = input(p("👉 Pilih:", C.BOLD))

        if choice == "00":
            return
        if choice == "1":
            for n in notifications:
                if n.get("is_read") is False:
                    get_notification_detail(SESSION.api_key, tokens, n.get("id", ""))
            print(ok("Semua notifikasi ditandai dibaca"))
            pause()
