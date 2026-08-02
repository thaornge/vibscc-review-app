# Nga — Checkpoint 1 & Checkpoint 2 Completion Report

## Kết luận

- Checkpoint 1, phần kỹ thuật trong source: **COMPLETE**.
- Checkpoint 2, phần Nga/UI + FakeRepository: **COMPLETE**.
- Private repo URL/commit SHA: **external action pending** vì không có repository đích/credential trong input.
- Ngọc Checkpoint 2B (Supabase/import-export): **not claimed**.

## Deliverable đã hoàn thành

| Yêu cầu | Trạng thái | Bằng chứng |
|---|---|---|
| Stack/technical decisions | PASS | `TECH_DECISIONS.md` |
| UI ↔ persistence interface | PASS | `src/repository_base.py` |
| Schema/ERD sơ bộ | PASS | `DATA_DICTIONARY_AND_ERD.md` |
| Mock schema/data chạy độc lập | PASS | `src/mock_seed.py`, `FakeRepository` |
| Blind form/no leakage | PASS | app + tests |
| Visible Accept/Edit | PASS | app + tests |
| Discussion proposal/confirm/reject | PASS | app + tests |
| Adjudication | PASS | app + tests |
| Save Draft persists | PASS | JSON state + test reopen |
| Submit lock/concurrency | PASS | row_version + atomic update tests |
| 4 reviewer accounts + admin mock | PASS | synthetic users |
| README/user guide | PASS | README + `USER_GUIDE.md` |
| State/constraint tests | PASS | 18/18 |
| Day 1–2 regression | PASS | 27/27 |
| EXP-08 compatibility review | PASS | conclusion `PATCH_REQUIRED` |
| No secret/real data | PASS | `.env`/`.venv` excluded; synthetic only |

## Command bàn giao

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pytest -q tests
python -m streamlit run app.py
```

## Giới hạn trung thực

Checkpoint 1 yêu cầu gửi private repo URL và commit SHA. ZIP không thể tự tạo đúng repository nhóm hoặc add collaborator nếu chưa được cung cấp tài khoản/repository target, nên hai metadata này không được bịa. Nga cần tạo/push private repo, add Ngọc và Phúc, rồi ghi URL/SHA vào báo cáo nhóm.

Deployed app, Supabase persistence, Task 07 export và four-machine UAT thuộc Checkpoint 3/final hoặc phần Ngọc, không được đánh dấu hoàn tất trong gói Checkpoint 1–2 này.

