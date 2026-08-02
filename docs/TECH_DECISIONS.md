# Technical Decisions — Checkpoint 1

## Trạng thái

`DECIDED_FOR_MOCK_INTEGRATION`, ngày 02/08/2026. Các quyết định ảnh hưởng persistence production cần Ngọc triển khai đúng contract hoặc đề xuất thay đổi trước Checkpoint 3.

## Quyết định

1. Stack mục tiêu giữ nguyên: Streamlit + Supabase PostgreSQL/Auth + private GitHub repository.
2. Checkpoint 2 của Nga dùng `FakeRepository` lưu JSON để UI chạy độc lập, nhưng mọi service chỉ phụ thuộc `Repository` protocol.
3. Repository contract gồm snapshot read và serializable atomic update. Supabase adapter có thể dùng transaction/RPC thay vì tải toàn store; behavior phải tương đương.
4. `record_id` là immutable pipeline key; `case_id` và `assignment_id` là internal stable IDs.
5. Route được quyết định trước khi assignment; reviewer không được chọn hoặc đổi route.
6. `SINGLE_VISIBLE_REVIEW` có 1 reviewer và chỉ mở exact two-model consensus. Các double route có 2 reviewer khác nhau và visibility `BLIND`.
7. Draft được phép chưa hoàn chỉnh; submit phải validate toàn bộ C/S/A và khóa initial annotation.
8. Mọi mutable assignment có `row_version`; update sai version bị từ chối để chặn lost update/concurrent overwrite.
9. Discussion chỉ mở sau hai initial submissions khác tuple; proposal cần reviewer còn lại confirm. Reject chuyển `ADJUDICATION_REQUIRED`.
10. Mock authentication dùng account selector để test workflow. Production phải dùng Supabase Auth với account pre-created và public signup disabled.
11. UI dùng một Streamlit entrypoint và screen navigation thay vì thư mục multipage. Quyết định này giảm session/state duplication nhưng không thay đổi behavior contract.
12. Dữ liệu Day 1–2 được giữ trong `day1_day2_nga/`, tách khỏi app để không trộn dependency và output.

## Interface UI ↔ persistence đã chốt

```python
class Repository(Protocol):
    def snapshot(self) -> dict: ...
    def atomic_update(self, operation): ...
    def reset(self) -> None: ...
```

Ngọc không bắt buộc hiện thực callback API nguyên xi ở production. Adapter/service có thể chuyển thành method cụ thể hoặc PostgreSQL RPC, nhưng phải giữ các guarantee:

- read theo stable ID, không theo row order;
- atomic submit;
- unique assignment/initial annotation;
- optimistic concurrency;
- append-only audit;
- authorization và blind filtering ở backend/RLS;
- lỗi giữa transaction không commit một phần.

## Trade-offs

- JSON repository không hỗ trợ multi-machine; nó chỉ là độc lập Checkpoint 2 của Nga.
- Backend filtering trong mock chứng minh behavior, không thay thế RLS production.
- Không tự xây importer/exporter Supabase trong phạm vi Nga Checkpoint 2 để tránh ghi đè trách nhiệm của Ngọc.

