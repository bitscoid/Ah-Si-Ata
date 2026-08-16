"""Bookmark storage (favourite packages) backed by `bookmark.json`."""
from __future__ import annotations

import json
import os


_BOOKMARK_PATH = "bookmark.json"


class Bookmark:
    _instance = None
    _initialized = False

    packages: list[dict] = []
    _filepath: str = _BOOKMARK_PATH

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

    def initialize(self) -> None:
        """One-time load from disk. Kept out of `__init__` (no import side effects)."""
        if self._initialized:
            return
        if os.path.exists(self._filepath):
            self.load_bookmark()
        else:
            self._save([])
        self._initialized = True

    def _save(self, data: list[dict]) -> None:
        with open(self._filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def _ensure_schema(self) -> None:
        """Migrate legacy entries missing `family_name` or `order`."""
        updated = False
        for pkg in self.packages:
            if "family_name" not in pkg:
                pkg["family_name"] = ""
                updated = True
            if "order" not in pkg:
                pkg["order"] = 0
                updated = True
        if updated:
            self.save_bookmark()

    def load_bookmark(self) -> None:
        with open(self._filepath, "r", encoding="utf-8") as f:
            self.packages = json.load(f)
        self._ensure_schema()

    def save_bookmark(self) -> None:
        self._save(self.packages)

    def add_bookmark(
        self,
        family_code: str,
        family_name: str,
        is_enterprise: bool,
        variant_name: str,
        option_name: str,
        order: int,
    ) -> bool:
        key = (family_code, variant_name, order)
        if any(
            (p["family_code"], p["variant_name"], p["order"]) == key
            for p in self.packages
        ):
            print("Bookmark sudah ada.")
            return False
        self.packages.append({
            "family_name": family_name,
            "family_code": family_code,
            "is_enterprise": is_enterprise,
            "variant_name": variant_name,
            "option_name": option_name,
            "order": order,
        })
        self.save_bookmark()
        print("Bookmark ditambahkan.")
        return True

    def remove_bookmark(
        self,
        family_code: str,
        is_enterprise: bool,
        variant_name: str,
        order: int,
    ) -> bool:
        for i, pkg in enumerate(self.packages):
            if (
                pkg["family_code"] == family_code
                and pkg["is_enterprise"] == is_enterprise
                and pkg["variant_name"] == variant_name
                and pkg["order"] == order
            ):
                del self.packages[i]
                self.save_bookmark()
                print("Bookmark dihapus.")
                return True
        print("Bookmark tidak ditemukan.")
        return False

    def get_bookmarks(self) -> list[dict]:
        return self.packages.copy()


BOOKMARK = Bookmark()
