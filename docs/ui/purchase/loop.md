# ahsiata/ui/purchase/loop.py — beli semua paket dalam family

Loop pembelian massal (CLI `6`): iterate semua option family dari indeks awal, settle satu per satu.

## Ringkasan

`purchase_by_family` memuat family, menyusun `PaymentItem` untuk tiap option mulai `start_from_option`, lalu settle berurutan dengan jeda opsional. `item_name` diberi prefix angka acak `randint(1000, 9999)` — trik anti-dedup/anti-deteksi server. Laporan sukses di akhir.

## Fungsi

- `purchase_by_family(family_code: str, use_decoy: bool, pause_on_success: bool, delay_seconds: int, start_from_option: int) -> None` — untuk tiap target:
  - `items[0]["item_name"] = f"{randint(1000,9999)} <variant> <option>"`.
  - `use_decoy` → `DECOY.get_decoy("balance")` + `get_package` → `settle_with_decoy(..., "BUY_PACKAGE", token_confirmation_idx=1)`.
  - else → `settlement_balance(..., "BUY_PACKAGE", ask_overwrite=True)`.
  - Sukses jika luaran dict `status == "SUCCESS"` → catat `(variant, order.name, price)`; `pause_on_success` → `pause()`; `delay_seconds` → `time.sleep`.

## Alur/Detail penting

- `token_confirmation` pada item di-loop di-set `""` (tidak dari server); `settlement_balance` mengambil token dari item `token_confirmation_idx` — untuk flow decoy indeks 1.
- Parameter menu datang dari input CLI `6` di [cli.md](../../ahsiata/cli.md) (family, mulai, decoy y/n, jeda y/n, detik).

## Catatan

- Decoy di-loop memakai prefix `default-`/`prio-` sesuai `subscription_type` (lihat [core/decoy.md](../../core/decoy.md)).