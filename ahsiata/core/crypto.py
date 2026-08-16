"""Cryptographic primitives: AES-CBC encryption, HMAC signatures."""
from __future__ import annotations

import base64
import hashlib
import hmac
import os
from base64 import urlsafe_b64decode, urlsafe_b64encode

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

from ahsiata.config import CONFIG


# -- xdata encryption ---------------------------------------------------------

def _derive_iv(xtime_ms: int) -> bytes:
    """IV = first 16 hex chars of SHA256(xtime_ms)."""
    sha = hashlib.sha256(str(xtime_ms).encode()).hexdigest()
    return sha[:16].encode()


def encrypt_xdata(plaintext: str, xtime_ms: int) -> str:
    iv = _derive_iv(xtime_ms)
    key = CONFIG.xdata_key.encode()
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return urlsafe_b64encode(cipher.encrypt(pad(plaintext.encode(), 16, style="pkcs7"))).decode()


def decrypt_xdata(xdata: str, xtime_ms: int) -> str:
    iv = _derive_iv(xtime_ms)
    key = CONFIG.xdata_key.encode()
    ct = urlsafe_b64decode(xdata + "=" * ((4 - len(xdata) % 4) % 4))
    pt = AES.new(key, AES.MODE_CBC, iv).decrypt(ct)
    return unpad(pt, 16, style="pkcs7").decode()


# -- HMAC signatures ----------------------------------------------------------

def make_x_signature(id_token: str, method: str, path: str, sig_time_sec: int) -> str:
    key = f"{CONFIG.x_api_base_secret};{id_token};{method};{path};{sig_time_sec}".encode("utf-8")
    msg = f"{id_token};{sig_time_sec};".encode("utf-8")
    return hmac.new(key, msg, hashlib.sha512).hexdigest()


def make_x_signature_payment(
    access_token: str,
    sig_time_sec: int,
    package_code: str,
    token_payment: str,
    payment_method: str,
    payment_for: str,
    path: str,
) -> str:
    salt = CONFIG.payment_sign_salt
    key = f"{CONFIG.x_api_base_secret};{sig_time_sec}#{salt};POST;{path};{sig_time_sec}".encode("utf-8")
    msg = f"{access_token};{token_payment};{sig_time_sec};{payment_for};{payment_method};{package_code};".encode("utf-8")
    return hmac.new(key, msg, hashlib.sha512).hexdigest()


def make_x_signature_bounty(
    access_token: str,
    sig_time_sec: int,
    package_code: str,
    token_payment: str,
) -> str:
    salt = CONFIG.payment_sign_salt
    path = "api/v8/personalization/bounties-exchange"
    key = f"{CONFIG.x_api_base_secret};{access_token};{sig_time_sec}#{salt};POST;{path};{sig_time_sec}".encode("utf-8")
    msg = f"{access_token};{token_payment};{sig_time_sec};{package_code};".encode("utf-8")
    return hmac.new(key, msg, hashlib.sha512).hexdigest()


def make_x_signature_loyalty(
    sig_time_sec: int,
    package_code: str,
    token_confirmation: str,
    path: str,
) -> str:
    salt = CONFIG.payment_sign_salt
    key = f"{CONFIG.x_api_base_secret};{sig_time_sec}#{salt};POST;{path};{sig_time_sec}".encode("utf-8")
    msg = f"{token_confirmation};{sig_time_sec};{package_code};".encode("utf-8")
    return hmac.new(key, msg, hashlib.sha512).hexdigest()


def make_x_signature_bounty_allotment(
    sig_time_sec: int,
    package_code: str,
    token_confirmation: str,
    path: str,
    destination_msisdn: str,
) -> str:
    salt = CONFIG.payment_sign_salt
    key = (
        f"{CONFIG.x_api_base_secret};{sig_time_sec}#{salt};"
        f"{destination_msisdn};POST;{path};{sig_time_sec}"
    ).encode("utf-8")
    msg = f"{token_confirmation};{sig_time_sec};{destination_msisdn};{package_code};".encode("utf-8")
    return hmac.new(key, msg, hashlib.sha512).hexdigest()


def make_ax_api_signature(
    ts_for_sign: str,
    contact: str,
    code: str,
    contact_type: str,
) -> str:
    """CIAM OIDC token signature: HMAC-SHA256 with AX_API_SIG_KEY."""
    key = CONFIG.ax_api_sig_key.encode("ascii")
    preimage = f"{ts_for_sign}password{contact_type}{contact}{code}openid"
    digest = hmac.new(key, preimage.encode("utf-8"), hashlib.sha256).digest()
    return base64.b64encode(digest).decode("ascii")


# -- Encrypted-field helpers --------------------------------------------------

def encrypt_circle_msisdn(msisdn: str) -> str:
    """Return urlsafe_b64(ct) + iv_ascii16 (last 16 chars)."""
    key = CONFIG.encrypted_field_key.encode("ascii")
    iv_ascii = os.urandom(8).hex()
    iv = iv_ascii.encode("ascii")
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ct = cipher.encrypt(pad(msisdn.encode("utf-8"), AES.block_size))
    ct_b64 = base64.urlsafe_b64encode(ct).decode("ascii")
    return ct_b64 + iv_ascii


def decrypt_circle_msisdn(encrypted_msisdn_b64: str) -> str:
    iv_ascii = encrypted_msisdn_b64[-16:]
    b64_part = encrypted_msisdn_b64[:-16]
    key = CONFIG.encrypted_field_key.encode("ascii")
    iv = iv_ascii.encode("ascii")

    padding = len(b64_part) % 4
    if padding:
        b64_part += "=" * (4 - padding)
    try:
        ct = base64.urlsafe_b64decode(b64_part)
        pt_padded = AES.new(key, AES.MODE_CBC, iv).decrypt(ct)
        pt = unpad(pt_padded, AES.block_size, style="pkcs7")
        return pt.decode("utf-8")
    except Exception:
        return ""
