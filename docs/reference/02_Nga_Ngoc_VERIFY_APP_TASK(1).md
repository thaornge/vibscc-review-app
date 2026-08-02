# Nga + Ngọc - VERIFY-09: Minimal Human Verification App

> Đọc task tổng trước: `01_TASKS/00_ViBSCC_Day3_Task_Package.md`.

## 1. Mục tiêu

Tạo một web app tối giản để bốn annotator ở bốn máy cùng review dữ liệu qua shared persistent database. App phải hỗ trợ đúng blind/visible/discussion/adjudication workflow và export cho `07_finalize_labels.py`.

App là công cụ hỗ trợ hoàn thành dataset, không phải sản phẩm thương mại. Không xây dashboard, chat realtime, gọi LLM trực tiếp, analytics phức tạp hoặc tính năng ngoài scope.

## 2. Stack và quyền tự thiết kế

Stack mặc định:

```text
Streamlit Community Cloud
+ Supabase PostgreSQL/Auth
+ private GitHub repository
```

- Nga tạo private repo, add Ngọc và Phúc.
- Nga là integration/repository lead.
- Ngọc phụ trách persistence/import-export/data integrity.

Đây là stack mặc định. Có thể thay đổi chi tiết nội bộ hoặc đề xuất stack tương đương nếu vẫn đáp ứng multi-user, persistence, blind integrity, import/export, acceptance tests và deadline. Thay đổi ảnh hưởng contract/deadline phải báo Phúc trước.

## 3. Workflow khóa

### Production

```text
LLM khác nhau / uncertain / invalid
→ DOUBLE_BLIND

LLM consensus + random audit
→ DOUBLE_BLIND_AUDIT

LLM consensus + không audit/test
→ SINGLE_VISIBLE_REVIEW
```

### Blind-only test candidate

```text
TEST_RESERVE_CANDIDATE
→ DOUBLE_BLIND_TEST
→ không cần và không được phụ thuộc LLM predictions
```

### Resolution

```text
2 human giống nhau
→ RESOLVED_HUMAN_AGREEMENT

2 human khác nhau
→ DISCUSSION_REQUIRED
→ proposal + confirm/reject
→ không chốt: ADJUDICATION_REQUIRED
→ Phúc adjudicate
```

App không tự tạo final corpus.

## 4. Access tối thiểu

Hai role là đủ:

| Role | Quyền tối thiểu |
|---|---|
| REVIEWER | Chỉ thấy assignment của mình; blind không thấy LLM/human khác; visible thấy consensus; tham gia discussion của case mình |
| ADMIN | Import/export, xem all cases, adjudicate, reopen có audit reason |

Blind integrity là requirement phương pháp luận, không phải tính năng tùy chọn.

## 5. Entities tối thiểu

Thiết kế bảng có thể thay đổi, nhưng hệ thống phải biểu diễn được:

1. User/Annotator.
2. Record.
3. Hai LLM predictions có provenance.
4. Review case/route.
5. Assignment/slot.
6. Human annotation ban đầu.
7. Discussion resolution.
8. Adjudication resolution.
9. Import/export run.
10. Audit event hoặc cơ chế tương đương để không mất lịch sử.

Field dictionary tham chiếu chi tiết nằm trong `02_SHARED_SPEC/01_VERIFY_APP_SPEC.md` và `02_DATA_CONTRACT.md`.

## 6. Phân chia theo phase

### Phase 0 - Làm chung, hoàn tất trước Checkpoint 1

- Đọc spec/contract.
- Chọn stack cuối.
- Tạo private repo.
- Chốt interface UI ↔ persistence.
- Chốt internal schema/ERD.
- Import được mock schema cơ bản.
- Tạo `docs/TECH_DECISIONS.md`.

### Phase 1A - Nga

- Streamlit pages/UI.
- Authentication/session đơn giản.
- Blind form.
- Visible Accept/Edit.
- Discussion proposal/confirm/reject.
- Adjudication page.
- Save draft.
- FakeRepository/mock backend.
- State machine và UI tests.
- README/user guide.

### Phase 1B - Ngọc

- Supabase schema/migrations.
- Shared persistence.
- Import Task 06 bundle.
- Import blind-only test reserve.
- Export Task 07 bundle.
- Constraints/reconciliation.
- Backup snapshot/restore test.
- Supabase repository và integration tests.

### Phase 2 - Integration

- Thay fake backend bằng real repository.
- Kiểm thử bốn users.
- Kiểm thử concurrent submit.
- Kiểm thử blind visibility.
- Import full mock bundle và export sample.

### Phase 3 - Deploy/UAT

- Deploy app.
- Tạo bốn reviewer account + admin test.
- UAT trên bốn browser/máy nếu có thể.
- Fix P0/P1 bắt buộc.
- Tag release/final commit.

## 7. Checkpoint và deadline

### 23:00 ngày 01/08/2026

Nga gửi repo URL, commit SHA, `TECH_DECISIONS.md`, repo tree, schema/ERD sơ bộ và command mock. Ngọc xác nhận đã vào repo và thống nhất interface.

### 12:00 ngày 02/08/2026

- Nga: UI mock chạy độc lập.
- Ngọc: DB/import-export chạy độc lập.

### 12:00 ngày 03/08/2026

Integration + deployed candidate + sample export + UAT sơ bộ; không còn P0.

### 17:00 ngày 03/08/2026

Final submission.

## 8. Input Day 3

Real production inputs chưa có. Dùng:

`03_MOCK_DATA/01_VERIFY_APP/`

Mock phải cover:

- consensus;
- disagreement C/S/A/eligibility;
- uncertain;
- parse/constraint invalid;
- random audit;
- visible Accept/Edit;
- blind human agreement/disagreement;
- discussion resolution/escalation;
- adjudication;
- test blind-only không có LLM predictions.

## 9. Save/submit semantics

- Save Draft bắt buộc; reload/login lại không mất draft.
- Autosave từng phím là MAY, không bắt buộc.
- Submit khóa initial annotation.
- Không update/overwrite initial label âm thầm.
- Reopen chỉ admin, có reason/audit history.
- UI và backend đều validate C/S/A.

## 10. Repository tree gợi ý

> Cây dưới đây là **gợi ý**, không phải cấu trúc bắt buộc. Có thể đổi tên/cấu trúc nếu vẫn đáp ứng contract, tests và deliverables.

```text
vibscc-review-app/
├── app.py                              # Streamlit entrypoint, session và navigation.
├── pages/
│   ├── 01_My_Review.py                # Blind/visible review page cho reviewer.
│   ├── 02_Discussion.py               # Proposal, confirm/reject, escalation.
│   ├── 03_Adjudication.py             # Phúc xử lý escalated cases.
│   └── 04_Admin_Import_Export.py       # Import, validation, export, progress tối thiểu.
├── src/
│   ├── config.py                       # Đọc env/Streamlit secrets.
│   ├── auth.py                         # Login/logout/current user.
│   ├── constants.py                    # Roles, routes, statuses, label domains.
│   ├── validators.py                   # Label/schema validation.
│   ├── state_machine.py                # Workflow transitions.
│   ├── models.py                       # Domain models/dataclasses.
│   ├── repository_base.py              # Interface UI ↔ persistence.
│   ├── repository_fake.py              # Mock backend để Nga không chờ Ngọc.
│   ├── repository_supabase.py          # Supabase implementation.
│   ├── review_service.py               # Assign/start/draft/submit/Accept/Edit.
│   ├── discussion_service.py           # Discussion workflow.
│   ├── adjudication_service.py         # Admin adjudication.
│   ├── import_service.py               # Validate + import bundles.
│   └── export_service.py               # Export FINAL-07 bundle.
├── db/
│   ├── 001_schema.sql                  # Core entities/tables.
│   ├── 002_constraints.sql             # FK/unique/check constraints.
│   ├── 003_access_policies.sql         # Minimal access/blind policies.
│   └── 004_transaction_functions.sql   # Atomic submit/state updates nếu cần.
├── scripts/
│   ├── import_task06_bundle.py          # Import LLM production outputs.
│   ├── import_test_reserve.py           # Import blind-only test candidates.
│   ├── export_task07_bundle.py          # Export history/resolutions.
│   ├── validate_database.py             # Reconciliation/integrity checks.
│   └── backup_snapshot.py               # Snapshot backup.
├── mock_data/
│   ├── llm_input_pool_mock.csv          # Synthetic production texts.
│   ├── llm_predictions_long_mock.csv    # Two LLM predictions.
│   ├── llm_comparison_mock.csv          # Comparison results.
│   ├── review_routes_mock.csv           # Production routes.
│   ├── test_reserve_candidates_mock.csv # Blind-only test candidates.
│   └── mock_users.csv                   # ANN_01..04 + ADMIN_PHUC.
├── tests/
│   ├── test_label_constraints.py        # C/S/A validity.
│   ├── test_state_machine.py            # Workflow transitions.
│   ├── test_blind_visibility.py         # No leakage before submit.
│   ├── test_assignment_integrity.py     # Slots/users integrity.
│   ├── test_import_export.py            # Idempotency/reconciliation.
│   └── test_end_to_end_mock.py           # Full mock workflow.
├── docs/
│   ├── TECH_DECISIONS.md                # Stack/trade-offs/schema decisions.
│   ├── DATA_DICTIONARY.md               # Actual tables/fields.
│   ├── USER_GUIDE.md                    # Reviewer/admin instructions.
│   ├── DEPLOYMENT.md                    # Streamlit + Supabase deploy.
│   ├── BACKUP_RESTORE.md                # Backup/recovery.
│   └── EXP08_TEST_RESERVE_COMPATIBILITY.md # Task 08 PASS/PATCH conclusion.
├── .streamlit/config.toml               # Non-secret Streamlit config.
├── .env.example                         # Variable names only.
├── .gitignore                           # Block secrets/real data/backups.
├── requirements.txt                     # Dependencies.
└── README.md                            # Setup, mock, test, deploy, import/export.
```

## 11. Subtask Nga - EXP-08 compatibility

Nga kiểm tra code Task 08 hiện tại và ghi kết luận:

```text
PASS_WITHOUT_PATCH
hoặc
PATCH_REQUIRED
```

Task 08 phải hiểu rằng:

- `TEST_RESERVE_CANDIDATE` không đồng nghĩa toàn bộ final test.
- Candidate reserve khoảng 11,5% được human blind-finalize trước.
- Sau đó Task 08 chọn final test khoảng 10% `N_model`, stratified + group-aware.
- Reserve dư quay lại train/dev pool.
- Fixed split dùng chung cho mọi preprocessing view.

Không cần chạy real split trong Day 3.

## 12. Deliverables

- Private GitHub repo.
- Deployed app URL.
- README + user/deployment/backup docs.
- Mock data and commands.
- Automated tests + `TEST_REPORT.md`.
- `UAT_REPORT.md`.
- Sample review export ZIP/folder.
- Known issues.
- Contribution summary Nga/Ngọc.

## 13. Acceptance tối thiểu

- 4 users đăng nhập/submit được.
- Blind route không lộ LLM/human khác.
- Test blind-only không yêu cầu prediction.
- Visible route Accept/Edit đúng.
- Discussion/adjudication đúng state.
- Draft persistent.
- Invalid labels không lưu được.
- Import idempotent.
- Concurrent submit không overwrite.
- Export đủ history/provenance và row counts khớp.
- Không có secrets/real data trong repo.

Chi tiết: `04_EXPECTED_OUTPUTS/01_ACCEPTANCE_MATRIX.csv`.

## 14. Bàn giao

Xem `06_SUBMISSIONS/01_NGA_NGOC_SUBMISSION_INSTRUCTIONS.md`.

Nếu có điểm chưa rõ, input không khớp, contract gây xung đột hoặc cần thay đổi ảnh hưởng integration, liên hệ Phúc trước khi triển khai thay đổi đó.
