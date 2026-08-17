# ahsiata/ui/purchase/single.py — beli N kali via option code

Pembelian berulang satu paket (opsi `8` di detail paket).

## Ringkasan

`purchase_n_times_by_option_code` membeli paket yang sama N kali dengan jeda opsional; mendukung decoy. Prefix angka acak `randint(1000, 9999)` pada `item_name` sama seperti loop ([loop.md](loop.md)).

## Fungsi

- `purchase_n_times_by_option_code(n: int, option_code: str, use_decoy: bool, delay_seconds: int, pause_on_success: bool, token_confirmation_idx: int = 0) -> int` — return jumlah sukses:
  - `get_package(option_code)` → `price` + `token_confirmation` (sebenarnya, dari server — beda dengan loop).
  - Per iterasi: item name `f"{randint(1000,9999)} {nama}"`; decoy → `settle_with_decoy(..., token_confirmation_idx)`; else → `settlement_balance(..., ask_overwrite=True)`.
  - Sukses jika `status == "SUCCESS"`; `pause_on_success` → pause; `delay_seconds` → sleep sebelum iterasi berikutnya.

## Alur/Detail penting

- Pemanggil: [ui/package/details.md](../package/details.md) opsi `8` dengan `token_confirmation_idx=1`.

## Catatan

- `n < 1` ditolak di pemanggil (detail menu), bukan di sini.