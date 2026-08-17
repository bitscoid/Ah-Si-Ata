# ahsiata/ui/utils.py — helper UI umum

Clear screen, pause, HTML→teks, format kuota byte & harga.

## Ringkasan

Utilitas kecil tanpa state. `display_html` dipakai untuk Syarat & Ketentuan paket (T&C HTML dari server); `format_quota_byte`/`format_price` untuk angka kuota dan harga Rupiah.

## Fungsi/Kelas

- `clear_screen() -> None` — `os.system("cls" if nt else "clear")`.
- `pause() -> None` — `input("⏎ Lanjut…")`.
- `_HTMLToText(HTMLParser)` — parser: `<li>` → bullet `- `, `<br>` → newline; `get_text()` merapikan multi-newline lalu `textwrap.wrap(width=80, replace_whitespace=False)`.
- `display_html(html_text: str, width: int = 80) -> str` — parse + wrap.
- `format_quota_byte(quota_byte: int) -> str` — `>= GB` → `"X.XX GB"`, `>= MB` → MB, `>= KB` → KB, else `"N B"`.
- `format_price(price: int | float | str) -> str` — buang nondigit, format `Rp. 1.000` (titik ribu); input non-numerik dikembalikan apa adanya.

## Alur/Detail penting

- `format_quota_byte` dipakai Family Plan & Circle; `format_price` dipakai kl.menu, HOT, package list, payment.
- `display_html` dipanggil di `show_package_details` (T&C) — lihat [package/details.md](package/details.md).

## Catatan

- `format_price` menerima string bertanda mata uang (`"Rp..."`) lalu ekstrak digit — aman untuk payload server yang kadang string.