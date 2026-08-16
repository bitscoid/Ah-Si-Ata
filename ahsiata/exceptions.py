"""Exception hierarchy for Ah-Si-Ata."""
from __future__ import annotations


class AhsiataError(Exception):
    """Base for all Ah-Si-Ata errors."""


class ConfigError(AhsiataError):
    """Missing or invalid environment configuration."""


class AuthError(AhsiataError):
    """Authentication, OTP, or token refresh failure."""


class APIError(AhsiataError):
    """Main-backend (Engsel) API returned a non-SUCCESS response."""

    def __init__(self, status: str | None, message: str | None, payload: dict | None = None):
        self.status = status
        self.message = message or "Unknown API error"
        self.payload = payload or {}
        super().__init__(f"API error [{status}]: {self.message}")


class DecoyError(AhsiataError):
    """Decoy package lookup or refresh failure."""


class CipherError(AhsiataError):
    """Encryption, decryption, or signature failure."""
