"""Active session and refresh-token state for the logged-in user."""
from __future__ import annotations

from ahsiata.ui.style import fail
import json
import os
import time

from ahsiata.config import CONFIG
from ahsiata.api.auth import get_new_token
from ahsiata.api.profile import get_profile


class Session:
    """Singleton-style wrapper around multi-account refresh-token state.

    Backed by two files in the CWD:
      - `refresh-tokens.json` — list of {number, subscriber_id, subscription_type, refresh_token}
      - `active.number` — the currently active account
    """

    _instance = None
    _initialized = False

    api_key: str = ""

    refresh_tokens: list[dict] = []
    active_user: dict | None = None
    last_refresh_time: int | None = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        # No disk I/O at import time; state loads in `initialize()`.
        self.api_key = CONFIG.api_key

    def initialize(self) -> None:
        """One-time load of accounts + active number from disk.

        Called by the CLI entry point. Kept out of `__init__` so importing
        the package has no side effects (testable, headless-safe).
        """
        if self._initialized:
            return

        if os.path.exists("refresh-tokens.json"):
            self.load_tokens()
        else:
            with open("refresh-tokens.json", "w", encoding="utf-8") as f:
                json.dump([], f, indent=4)

        self.load_active_number()
        self.last_refresh_time = int(time.time())
        self._initialized = True

    # -- Persistence ----------------------------------------------------------

    def load_tokens(self) -> None:
        with open("refresh-tokens.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        self.refresh_tokens = []
        for entry in data:
            if "number" in entry and "refresh_token" in entry:
                self.refresh_tokens.append(entry)
            else:
                print(f"⚠️ Entri token tidak valid: {entry}")

    def write_tokens_to_file(self) -> None:
        with open("refresh-tokens.json", "w", encoding="utf-8") as f:
            json.dump(self.refresh_tokens, f, indent=4)

    def write_active_number(self) -> None:
        if self.active_user:
            with open("active.number", "w", encoding="utf-8") as f:
                f.write(str(self.active_user["number"]))
        elif os.path.exists("active.number"):
            os.remove("active.number")

    def load_active_number(self) -> None:
        if not os.path.exists("active.number"):
            return
        with open("active.number", "r", encoding="utf-8") as f:
            number_str = f.read().strip()
        if number_str.isdigit():
            self.set_active_user(int(number_str))

    # -- Account management ---------------------------------------------------

    def add_refresh_token(self, number: int, refresh_token: str) -> None:
        existing = next((rt for rt in self.refresh_tokens if rt["number"] == number), None)
        if existing:
            existing["refresh_token"] = refresh_token
        else:
            tokens = get_new_token(self.api_key, refresh_token, "")
            profile_data = get_profile(self.api_key, tokens["access_token"], tokens["id_token"])
            sub_id = profile_data["profile"]["subscriber_id"]
            sub_type = profile_data["profile"]["subscription_type"]
            self.refresh_tokens.append({
                "number": int(number),
                "subscriber_id": sub_id,
                "subscription_type": sub_type,
                "refresh_token": refresh_token,
            })
        self.write_tokens_to_file()
        self.set_active_user(number)

    def remove_refresh_token(self, number: int) -> None:
        self.refresh_tokens = [rt for rt in self.refresh_tokens if rt["number"] != number]
        with open("refresh-tokens.json", "w", encoding="utf-8") as f:
            json.dump(self.refresh_tokens, f, indent=4)
        if self.active_user and self.active_user["number"] == number:
            if self.refresh_tokens:
                first = self.refresh_tokens[0]
                tokens = get_new_token(self.api_key, first["refresh_token"], first.get("subscriber_id", ""))
                if tokens:
                    self.set_active_user(first["number"])
            else:
                input("Tidak ada user tersisa. Tekan enter untuk melanjutkan…")
                self.active_user = None

    def set_active_user(self, number: int) -> bool:
        rt_entry = next((rt for rt in self.refresh_tokens if rt["number"] == number), None)
        if not rt_entry:
            print(fail(f"Tidak ada refresh token ditemukan untuk nomor: {number}"))
            input("Tekan enter untuk melanjutkan…")
            return False

        tokens = get_new_token(self.api_key, rt_entry["refresh_token"], rt_entry.get("subscriber_id", ""))
        if not tokens:
            print(fail(f"Gagal mendapatkan token untuk nomor: {number}. Refresh token mungkin tidak valid atau sudah kedaluwarsa."))
            input("Tekan enter untuk melanjutkan…")
            return False

        profile_data = get_profile(self.api_key, tokens["access_token"], tokens["id_token"])
        self.active_user = {
            "number": int(number),
            "subscriber_id": profile_data["profile"]["subscriber_id"],
            "subscription_type": profile_data["profile"]["subscription_type"],
            "tokens": tokens,
        }
        rt_entry["subscriber_id"] = self.active_user["subscriber_id"]
        rt_entry["subscription_type"] = self.active_user["subscription_type"]
        rt_entry["refresh_token"] = tokens["refresh_token"]
        self.write_tokens_to_file()
        self.last_refresh_time = int(time.time())
        self.write_active_number()
        return True

    # -- Token rotation -------------------------------------------------------

    def renew_active_user_token(self) -> bool:
        if not self.active_user:
            print(fail("Tidak ada user aktif atau refresh token hilang."))
            input("Tekan enter untuk melanjutkan…")
            return False

        tokens = get_new_token(
            self.api_key,
            self.active_user["tokens"]["refresh_token"],
            self.active_user["subscriber_id"],
        )
        if not tokens:
            print(fail("Gagal memperbarui token user aktif."))
            input("Tekan enter untuk melanjutkan…")
            return False

        self.active_user["tokens"] = tokens
        self.last_refresh_time = int(time.time())
        self.add_refresh_token(self.active_user["number"], tokens["refresh_token"])
        print("✅ Token user aktif berhasil diperbarui.")
        return True

    def get_active_user(self) -> dict | None:
        if not self.active_user:
            if self.refresh_tokens:
                first = self.refresh_tokens[0]
                tokens = get_new_token(self.api_key, first["refresh_token"], first.get("subscriber_id", ""))
                if tokens:
                    self.set_active_user(first["number"])
            return None

        if (
            self.last_refresh_time is None
            or (int(time.time()) - self.last_refresh_time) > CONFIG.token_refresh_interval
        ):
            self.renew_active_user_token()
            self.last_refresh_time = int(time.time())
        return self.active_user

    def get_active_tokens(self) -> dict | None:
        user = self.get_active_user()
        return user["tokens"] if user else None


SESSION = Session()
