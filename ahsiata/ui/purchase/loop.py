"""Purchase-by-family loop: iterate all options of a family and buy each."""
from __future__ import annotations

from random import randint

from ahsiata.api.packages import get_family, get_package
from ahsiata.api.purchase.balance import settlement_balance
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
        print("No active user tokens found.")
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

    print(f"Family: {data['package_family']['name']}\nTotal packages: {len(payment_targets)}")
    print(f"Start from option number: {start_from_option}")
    print(f"Use decoy: {use_decoy}")
    print(f"Delay between purchases: {delay_seconds}s")
    print(f"Pause on success: {pause_on_success}")

    for i, (variant, option, items) in enumerate(zip(target_variants, target_options, payment_targets)):
        real_price = option["price"]
        rnd_prefix = randint(1000, 9999)
        items[0]["item_name"] = f"{rnd_prefix} {variant['name']} {option['name']}"

        if use_decoy:
            # Caller decides which decoy prefix to apply; for simplicity use balance decoy.
            from ahsiata.core.decoy import DECOY
            decoy = DECOY.get_decoy("balance")
            if decoy:
                decoy_detail = get_package(api_key, tokens, decoy["option_code"])
                if decoy_detail:
                    items.append(PaymentItem(
                        item_code=decoy_detail["package_option"]["package_option_code"],
                        product_type="",
                        item_price=decoy_detail["package_option"]["price"],
                        item_name=decoy_detail["package_option"]["name"],
                        tax=0,
                        token_confirmation=decoy_detail["token_confirmation"],
                    ))
                    overwrite = real_price + decoy_detail["package_option"]["price"]
                    res = settlement_balance(
                        api_key, tokens, items, "BUY_PACKAGE", False,
                        overwrite_amount=overwrite, token_confirmation_idx=1,
                    )
                    if isinstance(res, dict) and res.get("status") != "SUCCESS":
                        error_msg = res.get("message", "")
                        if "Bizz-err.Amount.Total" in error_msg:
                            try:
                                valid_amount = int(error_msg.split("=")[1].strip())
                            except (IndexError, ValueError):
                                continue
                            print(f"Adjusted total amount to: {valid_amount}")
                            res = settlement_balance(
                                api_key, tokens, items, "BUY_PACKAGE", False,
                                overwrite_amount=valid_amount, token_confirmation_idx=1,
                            )
                else:
                    res = settlement_balance(api_key, tokens, items, "BUY_PACKAGE", True)
            else:
                res = settlement_balance(api_key, tokens, items, "BUY_PACKAGE", True)
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
            import time
            print(f"Waiting {delay_seconds}s...")
            time.sleep(delay_seconds)

    print()
    print(f"Total successful: {len(successful)}/{len(payment_targets)}")
    for s in successful:
        print(f" - {s['variant']} | {s['option']}")
    pause()
