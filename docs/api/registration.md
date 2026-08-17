# ahsiata/api/registration.py — registrasi Dukcapil

Satu endpoint registrasi data kependudukan.

## Ringkasan

`dukcapil` mengirim MSISDN + NIK + KK ke endpoint Dukcapil backend. Dipanggil dari menu `R` di CLI ([cli.md](../ahsiata/cli.md)); hasil ditampilkan via `_show_result`.

## Fungsi

- `dukcapil(api_key, msisdn, kk, nik) -> dict` — `api/v8/auth/regist/dukcapil`; payload `{msisdn, kk, nik, lang: "en"}`; `id_token` yang dikirim ke `send_api_request` adalah string kosong `""`.

## Alur/Detail penting

- Endpoint ini tampaknya tidak menuntut autentikasi Bearer — `id_token` kosong.
- Struktur `{kk, nik}`: kode mengirim key `kk` dan `nik` polos (tidak terenkripsi).

## Catatan

- Tidak ada validasi respons `status` di sini; UI hanya menampilkan apa yang dikembalikan.