# ahsiata/type_dict.py — kontrak data `PaymentItem`

Satu TypedDict yang menjadi kontrak item pembelian antara lapisan API dan UI.

## Ringkasan

Dipakai sebagai tipe untuk daftar `items` pada seluruh settlement (balance, QRIS, e-wallet) dan pembelian loop/N-kali. Tidak ada logika runtime; murni type hint.

## Kelas

- `PaymentItem(TypedDict)` — enam kunci:
  - `item_code: str` — `package_option_code`
  - `product_type: str` — selalu `""` pada praktiknya
  - `item_price: int`
  - `item_name: str` — kadang diberi prefix angka acak (lihat [ui/purchase/loop.py](../ui/purchase/loop.md))
  - `tax: int` — selalu `0`
  - `token_confirmation: str`

## Alur/Detail penting

- Dibuat di [ui/package/details.py](../ui/package/details.md) (dari `get_package`), [ui/hot.py](../ui/hot.md) `_buy_bundle`, dan [ui/purchase/loop.py](../ui/purchase/loop.md) / [single.py](../ui/purchase/single.md).
- Di-append item decoy di [api/purchase/balance.py](../api/purchase/balance.md) `append_decoy_item`.

## Catatan

- `item_price` diubah-ubah lewat `overwrite_amount` saat decoy; total yang dikirim ke server bisa berbeda dari harga asli (lihat `Bizz-err.Amount.Total` retry).