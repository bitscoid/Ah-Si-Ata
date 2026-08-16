"""Single-package purchase helpers: N times by option code or by family variant."""
from __future__ import annotations

import time
from random import randint

from ahsiata.api.packages import get_package
from ahsiata.api.purchase.balance import settle_with_decoy, settlement_balance
from ahsiata.core.decoy import DECOY
from ahsiata.core.session import SESSION
from ahsiata.type_dict import PaymentItem
from ahsiata.ui.style import C, p, ok, fail
from ahsiata.ui.utils import pause


def purchase_n_times_by_option_code(
    n: int,
    option_code: str,
    use_decoy: bool,
    delay_seconds: int,
    pause_on_success: bool,
    token_confirmation_idx: int = 0,
) -> int:
    """Buy a package by its option code, N times. Returns success count."""
    api_key = SESSION.api_key
    tokens = SESSION.get_active_tokens()
    if tokens is None:
        return 0

    detail = get_package(api_key, tokens, option_code)
    if not detail:
        print(fail("Gagal mengambil detail paket."))
        return 0

    price = detail["package_option"]["price"]
    token_confirmation = detail["token_confirmation"]
    successful = 0

    for i in range(n):
        print(ok(f"✅ [{i + 1}/{n}] {detail['package_option']['name']}"))
        rnd = randint(1000, 9999)
        items = [PaymentItem(
            item_code=option_code,
            product_type="",
            item_price=price,
            item_name=f"{rnd} {detail['package_option']['name']}",
            tax=0,
            token_confirmation=token_confirmation,
        )]
        if use_decoy:
            decoy = DECOY.get_decoy("balance")
            decoy_detail = get_package(api_key, tokens, decoy["option_code"]) if decoy else None
            res = settle_with_decoy(
                api_key, tokens, items, "BUY_PACKAGE", decoy_detail,
                token_confirmation_idx=token_confirmation_idx,
            )
        else:
            res = settlement_balance(
                api_key, tokens, items, "BUY_PACKAGE", True,
                token_confirmation_idx=token_confirmation_idx,
            )
        if isinstance(res, dict) and res.get("status") == "SUCCESS":
            successful += 1
        if pause_on_success:
            pause()
        if delay_seconds and i < n - 1:
            time.sleep(delay_seconds)
    return successful
