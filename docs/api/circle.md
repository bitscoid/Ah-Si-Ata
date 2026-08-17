# ahsiata/api/circle.py — API Circle / Family Hub

Endpoint Circle (Family Hub). MSISDN member selalu dienkripsi sebelum dikirim.

## Ringkasan

Sembilan fungsi POST tipis; payload baku `{is_enterprise: False, lang: "en"}` ditambah kunci spesifik. MSISDN pada payload (`msisdn`, `members[].msisdn`) melewati `encrypt_circle_msisdn(api_key, msisdn)`; respons yang memuat MSISDN terenkripsi didekripsi di layer UI ([ui/circle/info.py](../ui/circle/info.md)).

## Fungsi

- `get_group_data(api_key, tokens) -> dict` — `family-hub/api/v8/groups/status`.
- `get_group_members(api_key, tokens, group_id) -> dict` — `family-hub/api/v8/members/info`; payload `{group_id, is_enterprise, lang}`.
- `validate_circle_member(api_key, tokens, msisdn) -> dict` — `family-hub/api/v8/members/validate`; `msisdn` terenkripsi.
- `invite_circle_member(api_key, tokens, msisdn, name, group_id, member_id_parent) -> dict` — `family-hub/api/v8/members/invite`; payload `{access_token, group_id, members: [{msisdn (enc), name}], member_id_parent}`.
- `remove_circle_member(api_key, tokens, member_id, group_id, member_id_parent, is_last_member=False) -> dict` — `family-hub/api/v8/members/remove`; payload dengan `is_last_member`.
- `accept_circle_invitation(api_key, tokens, group_id, member_id) -> dict` — `family-hub/api/v8/groups/accept-invitation`; payload `{access_token, group_id, member_id}`.
- `create_circle(api_key, tokens, parent_name, group_name, member_msisdn, member_name) -> dict` — `family-hub/api/v8/groups/create`; `members` satu entry terenkripsi.
- `spending_tracker(api_key, tokens, parent_subs_id, family_id) -> dict` — `gamification/api/v8/family-hub/spending-tracker`; payload `{parent_subs_id, family_id}`.
- `get_bonus_data(api_key, tokens, parent_subs_id, family_id) -> dict` — `gamification/api/v8/family-hub/bonus/list`.

## Alur/Detail penting

- Semua dikirim lewat `send_api_request` (`api/client.py`) → body terenkripsi `xdata`.
- Tidak ada validasi `status` di sini — UI yang mengecek.

## Catatan

- Enkripsi MSISDN memakai `ENCRYPTED_FIELD_KEY`, bukan kunci khusus (lihat [core/crypto.py](../core/crypto.md) `encrypt_circle_msisdn`).