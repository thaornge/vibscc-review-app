# ViBSCC Review App — Nga Checkpoint 1–2

Bản bàn giao này hoàn tất phạm vi của Nga tại Checkpoint 1 và Checkpoint 2:

- kiến trúc và interface UI ↔ persistence;
- Streamlit UI mock cho blind, visible Accept/Edit, discussion và adjudication;
- mock login với 4 reviewer + 1 admin;
- `FakeRepository` lưu JSON bền vững qua reload;
- Save Draft, Submit Lock và optimistic concurrency;
- state transition và label validation;
- synthetic mock cover mọi route quan trọng;
- tests, user guide, technical decisions, ERD và handoff cho Ngọc;
- kiểm tra tương thích EXP-08;
- toàn bộ tài nguyên Day 1–2 cũ trong `day1_day2_nga/`.

Phần Supabase/import-export thật của Ngọc không được đánh dấu là hoàn thành trong gói này.

## Chạy app trên Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Khi Streamlit hỏi email onboarding, để trống rồi nhấn Enter. Mở URL được in ra, thường là `http://localhost:8501`.

## Chạy test

```powershell
python -m pytest -q tests
```

Kết quả tại thời điểm đóng gói: `18 passed`.

## Reset mock

```powershell
python scripts\reset_mock.py
```

Mock state mặc định nằm tại `.local/mock_state.json` và bị `.gitignore` loại khỏi commit. Có thể đổi bằng `VIBSCC_MOCK_DB_PATH`.

## Tài khoản mock

- `ANN_01`, `ANN_02`, `ANN_03`, `ANN_04`: reviewer.
- `ADMIN_PHUC`: admin/adjudicator.

Đây là mock authentication cho Checkpoint 2, không phải production authentication.

## Cấu trúc

```text
vibscc-review-app/
├── app.py
├── src/                         # domain, workflow, repository interface/fake
├── tests/                       # 18 tests của review app
├── scripts/reset_mock.py
├── docs/                        # decisions, ERD, guide, reports, references
├── mock_data/                   # mô tả synthetic fixture
├── day1_day2_nga/               # nguyên bộ code/tài nguyên Nga từ ZIP cũ
├── .streamlit/config.toml
├── .env.example
├── .gitignore
└── requirements.txt
```

Đọc tiếp `docs/CHECKPOINT_1_2_REPORT.md` và `docs/DECISIONS_AND_NGOC_HANDOFF.md` trước khi tích hợp Supabase.

