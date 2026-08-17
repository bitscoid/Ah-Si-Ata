# ahsiata/core/decoy.py — cache paket decoy

Singleton `DECOY` yang meng-cache paket decoy dari `decoy_data/decoy-*.json`, refresh otomatis tiap 5 menit.

## Ringkasan

Konsep decoy: paket dummy ditambahkan ke keranjang pembayaran supaya `total_amount` bisa diubah untuk memengaruhi hasil settlement. Modul ini hanya mengelola cache (nama decoy → `option_code` + harga); eksekusi pembelian ada di [api/purchase/balance.py](../api/purchase/balance.md) `settle_with_decoy` / `append_decoy_item`.

## Konstanta

- `_DECOY_PATH_PREFIX = "decoy_data/decoy-"`; `_DECOY_PAYMENT_TYPES = ("balance", "qris", "qris0")`.
- `_PRIO_SUBSCRIPTION_TYPES = ("PRIORITAS", "PRIOHYBRID", "GO")`.
- `_DECOY_TTL_SECONDS = 300`.
- 6 nama decoy dikelola: `{default,prio}-{balance,qris,qris0}`.

## Kelas

- `DecoyPackage` — singleton `__new__` + `_initialized` (instance: `DECOY`).
  - `check_subscriber_change() -> None` — jika `subscriber_id` user aktif berubah: reset decoys, set `prefix` (`prio-` bila `subscription_type` di `_PRIO_SUBSCRIPTION_TYPES`, selain itu `default-`).
  - `fetch_decoy_data(decoy_name: str) -> None` — baca JSON lokal, resolve `option_code` via `get_package_details` (family/variant/order), simpan `{option_code, price, last_fetched_at}`.
  - `get_decoy(payment_type: str) -> dict | None` — cek perubahan subscriber; tolak tipe di luar `balance/qris/qris0`; refresh jika `last_fetched_at` lebih tua dari TTL; return entry.
  - `reset_decoys() -> None` — kembalikan ke `_INITIAL_DECOYS` (semua `option_code: ""`, `price: 0`, `last_fetched_at: 0`).

## Alur/Detail penting

- File decoy: `decoy_data/decoy-<name>.json` dengan kunci `{family_name, family_code, is_enterprise, migration_type, variant_code, option_name, order, price}`. Yang dibaca kode: `price` + field resolusi `{family_code, variant_code, order, is_enterprise, migration_type}`.
- `decoy-default-pass20.json` ada di repo tapi **tidak dibaca** — hanya 6 nama `{default,prio}-{balance,qris,qris0}` yang dikelola.

## Catatan

- Membaca file + panggil API di dalam satu method; kegagalan dicetak `fail` dan cache dibiarkan lama.