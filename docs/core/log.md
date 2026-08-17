# ahsiata/core/log.py — log diagnostik

Menulis baris ber-timestamp ke `ahsiata.log` (CWD).

## Ringkasan

Pencatatan raw respons/kesalahan untuk debugging. Tidak pernah raise — kegagalan tulis (mis. disk penuh) diabaikan diam-diam. Dipanggil dari [api/auth.py](../api/auth.md) (OTP/token gagal) dan [api/client.py](../api/client.md) (dekripsi/signature gagal; respons `status != "SUCCESS"`).

## Fungsi

- `log(entry: str) -> None` — append `[YYYY-MM-DDTHH:MM:SS] <entry>\n`; `except OSError: pass`.

## Alur/Detail penting

- `_LOG_PATH = "ahsiata.log"` — relatif CWD, dibuat otomatis saat pertama ditulis.
- Pemotongan raw respons: pemanggil memotong `raw=...[:2000]`.

## Catatan

- Bukan pengganti `logging` stdlib; tidak ada level/rotasi. Ganti saat butuh otomasi (lihat `ponytail:` di [cli.md](../ahsiata/cli.md)).