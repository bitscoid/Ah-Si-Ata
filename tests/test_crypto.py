"""Offline tests for the crypto/signing primitives (no network).

Run: python -m unittest discover -s tests -v
"""
import os
import unittest

# Required env must be present before importing any `ahsiata.*` module.
os.environ.setdefault("BASE_API_URL", "https://api.example.test/")
os.environ.setdefault("BASE_CIAM_URL", "https://ciam.example.test/")
os.environ.setdefault("BASIC_AUTH", "dGVzdDp0ZXN0")
os.environ.setdefault("AX_FP_KEY", "18b4d589826af50241177961590e6693")
os.environ.setdefault("UA", "test-agent")
os.environ.setdefault("API_KEY", "dGVzdA==")
os.environ.setdefault("ENCRYPTED_FIELD_KEY", "5dccbf08920a5527")
os.environ.setdefault("XDATA_KEY", "5dccbf08920a5527b99e222789c34bb7")
os.environ.setdefault("AX_API_SIG_KEY", "18b4d589826af50241177961590e6693")
os.environ.setdefault("X_API_BASE_SECRET", "test-secret")

from ahsiata.core.crypto import (  # noqa: E402
    decrypt_circle_msisdn,
    decrypt_xdata,
    encrypt_circle_msisdn,
    encrypt_xdata,
    make_ax_api_signature,
    make_x_signature,
)


class XDataTest(unittest.TestCase):
    def test_roundtrip(self):
        for xtime_ms in (1700000000000, 1700000000123):
            pt = '{"a": 1}'
            ct = encrypt_xdata(pt, xtime_ms)
            self.assertEqual(decrypt_xdata(ct, xtime_ms), pt)

    def test_wrong_xtime_fails(self):
        ct = encrypt_xdata("secret", 1000)
        with self.assertRaises(Exception):
            decrypt_xdata(ct, 2000)


class CircleMsisdnTest(unittest.TestCase):
    def test_roundtrip(self):
        enc = encrypt_circle_msisdn("6281234567890")
        self.assertEqual(decrypt_circle_msisdn(enc), "6281234567890")

    def test_garbage_returns_empty(self):
        self.assertEqual(decrypt_circle_msisdn("not-base64"), "")


class SignatureTest(unittest.TestCase):
    def test_x_signature_deterministic_sha512(self):
        sig = make_x_signature("tok", "POST", "api/v8/x", 1700000000)
        self.assertEqual(sig, make_x_signature("tok", "POST", "api/v8/x", 1700000000))
        self.assertEqual(len(sig), 128)  # hex-encoded sha512

    def test_ax_api_signature_deterministic(self):
        sig = make_ax_api_signature("2026-08-16T00:00:00.000+0700", "628123", "123456", "SMS")
        self.assertEqual(sig, make_ax_api_signature("2026-08-16T00:00:00.000+0700", "628123", "123456", "SMS"))


if __name__ == "__main__":
    unittest.main()