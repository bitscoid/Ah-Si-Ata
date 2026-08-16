"""Centralized configuration loaded from environment variables.

All env vars are read once at import time. Missing REQUIRED vars raise
immediately; OPTIONAL vars fall back to documented defaults.
"""
from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

# Populate env from `.env` (searched from CWD upward) once, at import.
# Without this, importing any `ahsiata.*` module outside `python main.py` fails.
load_dotenv()


def _required(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"{name} environment variable not set")
    return value


def _optional(name: str, default: str) -> str:
    return os.getenv(name, default)


@dataclass(frozen=True)
class Config:
    # XL backend endpoints (REQUIRED)
    base_api_url: str
    base_ciam_url: str

    # Auth credentials (REQUIRED)
    basic_auth: str
    ax_fp_key: str
    ua: str
    api_key: str

    # Encryption keys (REQUIRED for any encrypted request body)
    encrypted_field_key: str
    xdata_key: str
    ax_api_sig_key: str
    x_api_base_secret: str

    # Optional with defaults
    payment_sign_salt: str
    device_manufacturer: str
    device_model: str
    device_fake_msisdn: str
    app_version: str
    x_hv: str
    default_substype: str
    token_refresh_interval: int


CONFIG = Config(
    base_api_url=_required("BASE_API_URL"),
    base_ciam_url=_required("BASE_CIAM_URL"),
    basic_auth=_required("BASIC_AUTH"),
    ax_fp_key=_required("AX_FP_KEY"),
    ua=_required("UA"),
    api_key=_required("API_KEY"),
    encrypted_field_key=_required("ENCRYPTED_FIELD_KEY"),
    xdata_key=_required("XDATA_KEY"),
    ax_api_sig_key=_required("AX_API_SIG_KEY"),
    x_api_base_secret=_required("X_API_BASE_SECRET"),
    payment_sign_salt=_optional("PAYMENT_SIGN_SALT", "ae-hei_9Tee6he+Ik3Gais5="),
    device_manufacturer=_optional("DEVICE_MANUFACTURER", "samsung"),
    device_model=_optional("DEVICE_MODEL", "SM-N935F"),
    device_fake_msisdn=_optional("DEVICE_FAKE_MSISDN", "6281398370564"),
    app_version=_optional("APP_VERSION", "8.9.0"),
    x_hv=_optional("X_HV", "v3"),
    default_substype=_optional("DEFAULT_SUBSTYPE", "PREPAID"),
    token_refresh_interval=int(_optional("TOKEN_REFRESH_INTERVAL", "300")),
)
