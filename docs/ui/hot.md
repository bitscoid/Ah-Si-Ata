# ahsiata/ui/hot.py — menu paket HOT

Satu menu gabungan: paket HOT biasa (`hot_data/hot.json`) + bundle HOT-2.

## Ringkasan

Membaca `hot_data/hot.json` yang berisi `{"hot": [...], "bundles": [...]}` (struktur berubah dari layout lama `hot.json`/`hot2.json` terpisah). Nomor ≤ len(hot) = paket tunggal; nomor setelahnya = bundle multi-paket.

## Fungsi

- `show_hot_menu() -> None` — loop daftar; paket tunggal: `get_family(...)` → cari variant by `name` + option by `order` → `show_package_details(option_code, is_enterprise)`. Bundle: `_buy_bundle`.
- `_buy_bundle(api_key, tokens, selected: dict) -> None`:
  1. Resolve tiap paket via `get_package_details(family_code, variant_code, order, is_enterprise, migration_type)` → `PaymentItem` (item pertama jadi `main_detail`).
  2. Tampil detail: nama (dari `package_family.name - package_detail_variant.name - package_option.name`), harga, `payment_for` dari `main_detail["package_family"]["payment_for"]`, masa aktif, poin, plan, family code, parent code, benefit.
  3. Loop metode bayar: `1` Balance → `settlement_balance` (jika `overwrite_amount == -1`: peringatan "Pastikan saldo KURANG DARI <harga item terakhir>"); `2` E-Wallet → `show_multipayment`; `3` QRIS → `show_qris_payment`.
  4. Parameter dari bundle dict: `payment_for`, `ask_overwrite`, `overwrite_amount`, `token_confirmation_idx`, `amount_idx`.

## Alur/Detail penting

- Item `hot.json` tunggal: `{family_name, family_code, is_enterprise, variant_name, option_name, order}`.
- Item bundle: `{name, price, detail, packages: [...], payment_for, ask_overwrite, overwrite_amount, token_confirmation_idx, amount_idx}`.
- Decoy TIDAK dipakai di menu HOT (tidak ada opsi decoy).

## Catatan

- Ketergantungan pada struktur server: jika `get_package_details` gagal untuk satu paket bundle, pembelian dibatalkan (return).