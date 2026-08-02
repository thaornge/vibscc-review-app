# Decisions Made Without Nga–Ngọc Confirmation and Handoff

Người hoàn thiện gói đã tự quyết định các điểm sau theo quyền tự thiết kế của spec, vì chưa có interface/code từ Ngọc:

1. Giữ stack production mặc định Streamlit + Supabase; mock dùng JSON `FakeRepository`.
2. Chọn repository boundary `snapshot + atomic_update`; Ngọc được map sang transaction/RPC tương đương.
3. Chọn single-entry Streamlit screens thay vì nhiều file page.
4. Dùng stable textual IDs trong mock: `CASE_<record_id>`, `ASG_<record_id>_<slot>`; production có thể dùng UUID.
5. Dùng `row_version` cho optimistic concurrency và giữ submitted initial row immutable.
6. Draft có thể incomplete; submit mới chạy strict validator.
7. Route/visibility được backend quyết định; UI không nhận route reason/audit/predictions ở blind payload.
8. Discussion proposal chỉ cần một người tạo và người kia confirm; reject chuyển ngay adjudication.
9. Mock auth là selector 4 reviewer + admin; production phải thay bằng Supabase Auth.
10. B001 được seed ở `DISCUSSION_REQUIRED`, T002 ở `ADJUDICATION_REQUIRED` để các màn hình nghiệm thu có dữ liệu ngay.
11. EXP-08 được kết luận `PATCH_REQUIRED`, chưa sửa algorithm Day 2 khi real final inputs chưa READY.

## Ngọc cần hiện thực tiếp

- Supabase schema/migrations, constraints, RLS và transaction/RPC.
- Auth adapter và server-side role checks.
- Task 06 bundle importer + blind reserve importer, validate-before-commit và idempotency.
- FINAL-07 export bundle + manifest hashes/count reconciliation.
- backup/snapshot/restore mock test.
- adapter integration với service layer và four-user/concurrency tests trên shared DB.

## Điều không được thay im lặng

- route names/human count;
- blind payload behavior;
- C/S/A constraints;
- initial annotation immutability;
- export headers trong data contract;
- test reserve không cần LLM prediction.

