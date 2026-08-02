# User Guide

## Reviewer

1. Chọn mock account `ANN_01`–`ANN_04` ở sidebar.
2. Mở **My Review**, chọn assignment.
3. Với blind case, chỉ đọc text và điền nhãn; không có LLM/audit/human khác.
4. Với visible case, xem consensus rồi chọn **ACCEPT** hoặc **EDIT**. Edit phải có note ngắn.
5. **Save draft** để giữ dữ liệu sau reload. **Submit & lock** để nộp initial annotation; không thể sửa lại.
6. Khi hai blind reviewers khác nhãn, vào **Discussion**. Một người đề xuất tuple + rationale; người còn lại confirm hoặc reject/escalate.

## Admin

1. Chọn `ADMIN_PHUC`.
2. Vào **Adjudication** để xử lý case đã escalated; tuple và rationale bắt buộc.
3. Vào **Admin** để xem count hoặc reset toàn bộ synthetic mock.

## Demo nhanh

- `ANN_01` / V001: visible Accept.
- `ANN_03` / V002: visible Edit.
- `ANN_03` và `ANN_04` / B002: tạo agreement hoặc disagreement.
- `ANN_01` / B001: proposal; `ANN_02`: confirm/reject.
- `ADMIN_PHUC` / T002: adjudication đã seed sẵn.

Không dùng mock login hoặc JSON repository với dữ liệu thật.

