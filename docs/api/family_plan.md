# ahsiata/api/family_plan.py — API Family Plan (Akrab Organizer)

Endpoint Family Plan: info plan, validasi MSISDN, ganti/hapus member, alokasi kuota.

## Ringkasan

Lima fungsi POST tipis di atas `send_api_request`; semua payload memakai `lang: "en"` dan `is_enterprise: False`. Tidak ada validasi `status` — UI yang mengecek.

## Fungsi

- `get_family_data(api_key, tokens) -> dict` — `sharings/api/v8/family-plan/member-info`; payload `{group_id: 0, is_enterprise, lang}`.
- `validate_msisdn(api_key, tokens, msisdn) -> dict` — `api/v8/auth/check-dukcapil`; payload `{with_bizon: True, with_family_plan: True, with_optimus: True, with_regist_status: True, with_enterprise: True, is_enterprise: False, msisdn, lang}`.
- `change_member(api_key, tokens, parent_alias, alias, slot_id, family_member_id, new_msisdn) -> dict` — `sharings/api/v8/family-plan/change-member`; payload menyertakan `msisdn` polos (tidak dienkripsi, beda dengan Circle).
- `remove_member(api_key, tokens, family_member_id) -> dict` — `sharings/api/v8/family-plan/remove-member`.
- `set_quota_limit(api_key, tokens, original_allocation, new_allocation, family_member_id) -> dict` — `sharings/api/v8/family-plan/allocate-quota`; `member_allocations` satu entry dengan `original_*_allocation`, `new_allocation`, `message: ""`, `status: ""` (voice/text allocation `0`).

## Alur/Detail penting

- Pemanggil UI: [ui/family_plan.py](../ui/family_plan.md) — `show_family_info` (menu `8`, `V` di CLI).
- `validate_msisdn` dipakai pre-check: UI menolak jika `family_plan_role != "NO_ROLE"`.

## Catatan

- Nilai kuota dalam byte (UI mengonversi MB → byte sebelum panggil).