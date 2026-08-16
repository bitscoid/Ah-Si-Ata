"""Purchase-by-family loop: iterate all options of a family and buy each."""
from __future__ import annotations

import time
from random import randint

from ahsiata.api.packages import get_family, get_package
from ahsiata.api.purchase.balance import settle_with_decoy, settlement_balance
from ahsiata.core.session import SESSION
from ahsiata.type_dict import PaymentItem
from ahsiata.ui.utils import pause


def purchase_by_family(
    family_code: str,
    use_decoy: bool,
    pause_on_success: bool,
    delay_seconds: int,
    start_from_option: int,
) -> None:
    api_key = SESSION.api_key
    tokens = SESSION.get_active_tokens()
    if tokens is None:
        print("Tidak ada token user aktif ditemukan.")
        pause()
        return

    data = get_family(api_key, tokens, family_code)
    if not data:
        print(f"Gagal mengambil data family untuk {family_code}.")
        pause()
        return

    successful: list[dict] = []
    payment_targets: list[list[PaymentItem]] = []
    target_variants: list[dict] = []
    target_options: list[dict] = []
    option_index = 1

    for variant in data["package_variants"]:
        for option in variant["package_options"]:
            if option_index >= start_from_option:
                payment_targets.append([PaymentItem(
                    item_code=option["package_option_code"],
                    product_type="",
                    item_price=option["price"],
                    item_name=option["name"],
                    tax=0,
                    token_confirmation="",
                )])
                target_variants.append(variant)
                target_options.append(option)
            option_index += 1

    print(f"Family: {data['package_family']['name']}\nTotal paket: {len(payment_targets)}")
    print(f"Mulai dari nomor opsi: {start_from_option}")
    print(f"Gunakan decoy: {use_decoy}")
    print(f"Jeda antar pembelian: {delay_seconds}s")
    print(f"Jeda saat berhasil: {pause_on_success}")

    for i, (variant, option, items) in enumerate(zip(target_variants, target_options, payment_targets)):
        real_price = option["price"]
        rnd_prefix = randint(1000, 9999)
        items[0]["item_name"] = f"{rnd_prefix} {variant['name']} {option['name']}"

        if use_decoy:
            # Caller decides which decoy prefix to apply; for simplicity use balance decoy.
            from ahsiata.core.decoy import DECOY
            decoy = DECOY.get_decoy("balance")
            decoy_detail = get_package(api_key, tokens, decoy["option_code"]) if decoy else None
            res = settle_with_decoy(api_key, tokens, items, "BUY_PACKAGE", decoy_detail, token_confirmation_idx=1)
        else:
            res = settlement_balance(api_key, tokens, items, "BUY_PACKAGE", True)

        if isinstance(res, dict) and res.get("status") == "SUCCESS":
            successful.append({
                "variant": variant["name"],
                "option": f"{option['order']}. {option['name']}",
                "price": real_price,
            })
            print(f"[{i + 1}/{len(payment_targets)}] {variant['name']} - {option['name']} : SUCCESS")
        else:
            print(f"[{i + 1}/{len(payment_targets)}] {variant['name']} - {option['name']} : FAILED")

        if pause_on_success:
            pause()

        if delay_seconds > 0 and i < len(payment_targets) - 1:
            print(f"Menunggu {delay_seconds}s...")
            time.sleep(delay_seconds)

    print()
    print(f"Total berhasil: {len(successful)}/{len(payment_targets)}")
    for s in successful:
        print(f" - {s['variant']} | {s['option']}")
    pause()
