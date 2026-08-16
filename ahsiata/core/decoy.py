"""Decoy package cache. Refreshes from `decoy_data/decoy-*.json` every 5 minutes."""
from __future__ import annotations

import json
import os
import time

from ahsiata.api.packages import get_package_details
from ahsiata.core.session import SESSION


_DECOY_PATH_PREFIX = "decoy_data/decoy-"
_DECOY_PAYMENT_TYPES = ("balance", "qris", "qris0")
_PRIO_SUBSCRIPTION_TYPES = ("PRIORITAS", "PRIOHYBRID", "GO")
_DECOY_TTL_SECONDS = 300


_INITIAL_DECOYS = {
    name: {"option_code": "", "price": 0, "last_fetched_at": 0}
    for name in (
        "default-balance", "default-qris", "default-qris0",
        "prio-balance", "prio-qris", "prio-qris0",
    )
}


class DecoyPackage:
    _instance = None
    _initialized = False

    subscriber_id: str | None = None
    subscription_type: str | None = None
    prefix: str = "default-"

    decoys: dict = {}

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.decoys = {k: v.copy() for k, v in _INITIAL_DECOYS.items()}
        self._initialized = True

    def check_subscriber_change(self) -> None:
        user = SESSION.get_active_user()
        if user is None:
            return

        current_sub_id = user.get("subscriber_id", "")
        current_sub_type = user.get("subscription_type", "")
        if self.subscriber_id == current_sub_id:
            return

        print(f"Subscriber ID changed from {self.subscriber_id} to {current_sub_id}. Resetting decoy data.")
        self.reset_decoys()
        self.subscriber_id = current_sub_id
        self.subscription_type = current_sub_type
        self.prefix = "prio-" if current_sub_type in _PRIO_SUBSCRIPTION_TYPES else "default-"

    def fetch_decoy_data(self, decoy_name: str) -> None:
        user = SESSION.get_active_user()
        if user is None:
            print("No active user. Cannot fetch decoy package.")
            return

        path = _DECOY_PATH_PREFIX + decoy_name + ".json"
        print(f"Refreshing decoy data for: {decoy_name}")
        try:
            with open(path, "r", encoding="utf-8") as f:
                decoy = json.load(f)

            detail = get_package_details(
                SESSION.api_key,
                user["tokens"],
                decoy["family_code"],
                decoy["variant_code"],
                decoy["order"],
                decoy["is_enterprise"],
                decoy["migration_type"],
            )
            if detail is None:
                print(f"Could not fetch detail for {decoy_name}")
                return
            self.decoys[decoy_name] = {
                "option_code": detail["package_option"]["package_option_code"],
                "last_fetched_at": int(time.time()),
                "price": decoy["price"],
            }
            print(f"Decoy data for {decoy_name} refreshed successfully.")
        except Exception as e:
            print(f"Error fetching decoy data: {e}")

    def get_decoy(self, payment_type: str) -> dict | None:
        self.check_subscriber_change()
        if payment_type not in _DECOY_PAYMENT_TYPES:
            print(f"Unsupported payment type: {payment_type}")
            return None

        name = self.prefix + payment_type
        entry = self.decoys.get(name)
        if entry is None:
            return None
        if int(time.time()) - entry["last_fetched_at"] > _DECOY_TTL_SECONDS:
            self.fetch_decoy_data(name)
            entry = self.decoys.get(name)
        return entry

    def reset_decoys(self) -> None:
        self.decoys = {k: v.copy() for k, v in _INITIAL_DECOYS.items()}


DECOY = DecoyPackage()
