# VERIFY-09 - Human Verification App Specification

## 1. Phạm vi

### In scope

- Shared multi-user web app.
- Blind review, visible Accept/Edit, discussion, adjudication.
- Save draft và submit lock.
- Import Task 06 and blind-only test reserve.
- Export complete review history cho FINAL-07.
- Minimal progress/status.
- Backup/reconciliation.

### Out of scope

- Chạy LLM trong app.
- Tạo final corpus/split/modeling.
- Dashboard/analytics đẹp.
- Chat realtime.
- Email notifications.
- Mobile app.
- Quản trị nhiều dataset/project.

## 2. Routes

| Route | Input có LLM? | Human count | Visibility |
|---|---:|---:|---|
| DOUBLE_BLIND | Có nhưng ẩn | 2 | Blind |
| DOUBLE_BLIND_AUDIT | Có nhưng ẩn | 2 | Blind |
| SINGLE_VISIBLE_REVIEW | Có consensus | 1 | Visible Accept/Edit |
| DOUBLE_BLIND_TEST | Không bắt buộc | 2 | Blind |

Route quyết định trước khi assign. Reviewer không tự chọn route.

## 3. Comparison semantics

Hai LLM chỉ consensus khi giống toàn bộ tuple:

```text
eligibility + C + S + A
```

Prediction invalid/parse error/constraint error luôn đi blind. `uncertain=true` của bất kỳ LLM nào luôn đi blind.

## 4. Human label schema

Tối thiểu:

```text
record_id
annotator_code
review_route
visibility_mode
decision_action
eligibility
remove_reason
C_label
S_label
A_label
uncertain
uncertainty_reason
evidence
rule_id
note
guideline_version
started_at
submitted_at
```

Constraints:

```text
REMOVE → C/S/A null + remove_reason required
C0 → S0/A0
C1 → S1-S6/A1-A7
C2 → S0/A1-A7
```

## 5. Entities/fields tham chiếu

Thiết kế nội bộ được phép đổi, nhưng tối thiểu cần lưu:

### User/Annotator

- stable user ID;
- `annotator_code` như ANN_01..ANN_04;
- role REVIEWER/ADMIN;
- active flag.

### Record

- immutable `record_id`;
- `text_annotation`;
- `guideline_version`;
- `data_role`;
- content hash/import run.

### LLM prediction

- record_id;
- model slot 1/2;
- model ID/version;
- prompt/schema version;
- predicted eligibility/C/S/A;
- uncertainty/evidence;
- parse/constraint status;
- run ID.

### Review case

- case ID;
- record_id;
- route/reason/audit flag;
- required human count;
- status;
- import run.

### Assignment

- case ID;
- reviewer;
- slot;
- visibility;
- status/timestamps;
- uniqueness rules preventing same reviewer occupying both slots.

### Human annotation

- assignment ID;
- initial decision fields;
- action BLIND_LABEL/ACCEPT/EDIT;
- draft/submitted status;
- timestamps/version.

### Discussion resolution

- case ID;
- proposal labels;
- proposer;
- second reviewer confirm/reject;
- rationale/status/timestamps.

### Adjudication resolution

- case ID;
- adjudicator;
- final decision fields;
- rationale;
- guideline version/time.

### Import/export/audit

- run ID;
- schema version;
- file hashes/counts;
- actor/timestamp;
- append-only events or equivalent history.


## 5A. Reference database schema - gợi ý, không khóa cứng

Các bảng dưới đây là một thiết kế tham chiếu đủ đơn giản để triển khai bằng Supabase/PostgreSQL. Nhóm được phép gộp/tách/đổi tên bảng hoặc dùng ORM, miễn không làm mất dữ liệu và vẫn export đúng contract.

### `profiles`

| Field | Kiểu gợi ý | Bắt buộc | Ý nghĩa/constraint |
|---|---|---:|---|
| `user_id` | UUID/TEXT | Có | Khóa duy nhất, có thể ánh xạ Supabase Auth user. |
| `annotator_code` | TEXT | Có | Mã ổn định như ANN_01; unique; dùng khi export thay vì tên thật. |
| `display_name` | TEXT | Không | Chỉ để UI nội bộ; không cần export corpus. |
| `role` | TEXT | Có | REVIEWER hoặc ADMIN ở MVP. |
| `is_active` | BOOLEAN | Có | Tắt quyền truy cập mà không xóa lịch sử. |
| `created_at` | TIMESTAMPTZ | Có | Audit. |

### `import_runs`

| Field | Kiểu gợi ý | Bắt buộc | Ý nghĩa/constraint |
|---|---|---:|---|
| `import_run_id` | UUID/TEXT | Có | Unique run ID. |
| `source_run_id` | TEXT | Có | ID của Task 06 hoặc blind-test bundle; unique để idempotent. |
| `import_type` | TEXT | Có | TASK06_PRODUCTION hoặc BLIND_TEST_RESERVE. |
| `schema_version` | TEXT | Có | Contract version. |
| `guideline_version` | TEXT | Có | Version áp dụng cho records. |
| `input_sha256` | TEXT | Có | Hash toàn bundle/manifest để chặn import trùng hoặc sai. |
| `record_count` | INTEGER | Có | Reconciliation. |
| `imported_by` | FK/profile | Có | Actor. |
| `imported_at` | TIMESTAMPTZ | Có | Audit. |

### `records`

| Field | Kiểu gợi ý | Bắt buộc | Ý nghĩa/constraint |
|---|---|---:|---|
| `record_id` | TEXT | Có | Primary/external key từ annotation pool; immutable. |
| `text_annotation` | TEXT | Có | Text pseudonymized duy nhất reviewer được xem. |
| `content_hash` | TEXT | Có | Phát hiện text bị thay giữa pipeline. |
| `data_role` | TEXT | Có | PRODUCTION hoặc TEST_RESERVE_CANDIDATE ở app MVP. |
| `guideline_version` | TEXT | Có | Version dùng khi review. |
| `batch_id` | TEXT | Có | Batch/run hiển thị và audit. |
| `import_run_id` | FK | Có | Nguồn import. |
| `created_at` | TIMESTAMPTZ | Có | Audit. |

Không lưu raw comment, URL, source post, collector hoặc private entity mapping.

### `llm_predictions`

| Field | Kiểu gợi ý | Bắt buộc | Ý nghĩa/constraint |
|---|---|---:|---|
| `prediction_id` | UUID/BIGINT | Có | Internal unique ID. |
| `record_id` | FK | Có | Record liên quan. |
| `model_slot` | SMALLINT | Có | 1 hoặc 2; unique cùng record/run. |
| `model_id` | TEXT | Có | Provider/model name. |
| `model_version` | TEXT | Có | Snapshot/version cụ thể. |
| `prompt_version` | TEXT | Có | Prompt provenance. |
| `predicted_eligibility` | TEXT | Có nếu parse valid | KEEP/REMOVE. |
| `predicted_C/S/A` | TEXT | Có điều kiện | Theo constraints. |
| `uncertain` | BOOLEAN | Có | Routing. |
| `uncertainty_reason` | TEXT | Khi uncertain | Structured reason. |
| `evidence` | TEXT | Không | Evidence của LLM. |
| `parse_status` | TEXT | Có | VALID/INVALID_JSON/SCHEMA_ERROR... |
| `constraint_valid` | BOOLEAN | Có | False phải route blind. |
| `run_id` | TEXT/FK | Có | Run provenance. |

Bảng này có thể rỗng đối với `DOUBLE_BLIND_TEST`.

### `review_cases`

| Field | Kiểu gợi ý | Bắt buộc | Ý nghĩa/constraint |
|---|---|---:|---|
| `case_id` | UUID/BIGINT | Có | Internal unique ID. |
| `record_id` | FK | Có | Unique trong active import run. |
| `review_route` | TEXT | Có | Một trong bốn routes đã khóa. |
| `route_reason` | TEXT | Có | DISAGREEMENT, UNCERTAIN, INVALID, AUDIT, CONSENSUS, TEST... |
| `audit_flag` | BOOLEAN | Có | True chỉ với audit route. |
| `required_reviews` | SMALLINT | Có | 1 hoặc 2, phải khớp route. |
| `case_status` | TEXT | Có | State-machine status. |
| `import_run_id` | FK | Có | Provenance. |
| `created_at` | TIMESTAMPTZ | Có | Audit. |
| `resolved_at` | TIMESTAMPTZ | Khi resolved | Completion. |

### `review_assignments`

| Field | Kiểu gợi ý | Bắt buộc | Ý nghĩa/constraint |
|---|---|---:|---|
| `assignment_id` | UUID/BIGINT | Có | Unique. |
| `case_id` | FK | Có | Case. |
| `reviewer_id` | FK/profile | Có | Assigned reviewer. |
| `review_slot` | SMALLINT | Có | 1/2; unique cùng case. |
| `visibility_mode` | TEXT | Có | BLIND hoặc VISIBLE, phải khớp route. |
| `assignment_status` | TEXT | Có | ASSIGNED/IN_PROGRESS/SUBMITTED. |
| `assigned_at` | TIMESTAMPTZ | Có | Audit. |
| `started_at` | TIMESTAMPTZ | Không | Bắt đầu. |
| `submitted_at` | TIMESTAMPTZ | Khi submitted | Khóa initial label. |

Bắt buộc `UNIQUE(case_id, reviewer_id)` để một người không nhận hai slots.

### `human_annotations`

| Field | Kiểu gợi ý | Bắt buộc | Ý nghĩa/constraint |
|---|---|---:|---|
| `annotation_id` | UUID/BIGINT | Có | Unique. |
| `assignment_id` | FK | Có | Một active initial annotation/assignment. |
| `decision_action` | TEXT | Có | BLIND_LABEL/ACCEPT/EDIT. |
| `eligibility` | TEXT | Có | KEEP/REMOVE. |
| `remove_reason` | TEXT | Khi REMOVE | Mã chuẩn. |
| `C_label/S_label/A_label` | TEXT | Khi KEEP | Validate cả UI và backend. |
| `uncertain` | BOOLEAN | Có | Human uncertainty. |
| `uncertainty_reason` | TEXT | Khi uncertain | Lý do. |
| `evidence` | TEXT | Theo rule | Bằng chứng. |
| `rule_id` | TEXT | Không | Guideline section/rule. |
| `note` | TEXT | Không | Ca khó/lỗi data. |
| `guideline_version` | TEXT | Có | Version applied. |
| `save_status` | TEXT | Có | DRAFT/SUBMITTED. |
| `row_version` | INTEGER | Nên có | Optimistic concurrency. |
| `created_at/updated_at/submitted_at` | TIMESTAMPTZ | Có điều kiện | Audit. |

Một row SUBMITTED không được sửa âm thầm. Có thể lưu version mới khi admin reopen, nhưng initial version phải còn.

### `discussion_resolutions`

| Field | Kiểu gợi ý | Bắt buộc | Ý nghĩa/constraint |
|---|---|---:|---|
| `discussion_id` | UUID/BIGINT | Có | Unique. |
| `case_id` | FK | Có | Một active discussion/case. |
| `status` | TEXT | Có | OPEN/PENDING_CONFIRMATION/RESOLVED/ESCALATED. |
| `proposed_eligibility/C/S/A` | TEXT | Khi proposal | Valid tuple. |
| `proposed_by` | FK/profile | Khi proposal | Một trong hai reviewers. |
| `slot1_confirmed_by/slot2_confirmed_by` | FK/profile | Khi resolved | Xác nhận đúng participants. |
| `rationale` | TEXT | Có khi resolved/escalated | Không để rỗng. |
| `resolved_at` | TIMESTAMPTZ | Khi resolved | Audit. |

### `adjudication_resolutions`

| Field | Kiểu gợi ý | Bắt buộc | Ý nghĩa/constraint |
|---|---|---:|---|
| `adjudication_id` | UUID/BIGINT | Có | Unique. |
| `case_id` | FK | Có | Chỉ case ADJUDICATION_REQUIRED. |
| `adjudicator_id` | FK/profile | Có | ADMIN/Phúc. |
| `eligibility/C/S/A` | TEXT | Có điều kiện | Valid final tuple. |
| `rationale` | TEXT | Có | Bắt buộc. |
| `guideline_version` | TEXT | Có | Version applied. |
| `resolved_at` | TIMESTAMPTZ | Có | Audit. |

### `audit_events`

| Field | Kiểu gợi ý | Bắt buộc | Ý nghĩa/constraint |
|---|---|---:|---|
| `event_id` | BIGINT/UUID | Có | Append-only ID. |
| `actor_id` | FK/profile | Có | Ai thực hiện. |
| `case_id/assignment_id` | FK | Không | Context. |
| `event_type` | TEXT | Có | IMPORT/START/SAVE_DRAFT/SUBMIT/REOPEN/... |
| `metadata` | JSONB/TEXT | Không | Không chứa raw PII/secrets. |
| `created_at` | TIMESTAMPTZ | Có | Audit order. |

## 5B. Reference constraints

- `UNIQUE(record_id, import_run_id)` cho case active.
- `UNIQUE(record_id, model_slot, run_id)` cho prediction.
- `UNIQUE(case_id, review_slot)` và `UNIQUE(case_id, reviewer_id)`.
- `UNIQUE(assignment_id)` trong active initial annotation.
- Route `SINGLE_VISIBLE_REVIEW` → required_reviews=1, visibility=VISIBLE.
- Các double routes → required_reviews=2, visibility=BLIND.
- Discussion chỉ tạo khi đủ hai SUBMITTED annotations và tuples khác nhau.
- Adjudication chỉ tạo khi discussion ESCALATED.
- Mọi submit/state update quan trọng nên atomic transaction hoặc RPC tương đương.

## 6. State machine

### Double blind/test/audit

```text
READY
→ ASSIGNED
→ IN_REVIEW
→ WAITING_SECOND_REVIEW
→ HUMAN_AGREEMENT | DISCUSSION_REQUIRED
→ DISCUSSION_IN_PROGRESS
→ RESOLVED_DISCUSSION | ADJUDICATION_REQUIRED
→ RESOLVED_ADJUDICATION
```

### Single visible

```text
READY
→ ASSIGNED
→ IN_REVIEW
→ RESOLVED_VISIBLE_ACCEPT | RESOLVED_VISIBLE_EDIT
```

Invalid transition phải bị backend từ chối.

## 7. Blind integrity

### MUST

- Blind reviewer chỉ thấy `record_id`, `text_annotation`, guideline/batch info và form.
- Không thấy LLM1/LLM2, consensus/audit flag, reviewer khác hoặc human notes.
- Hai human chỉ thấy nhau sau khi cả hai đã submit và case chuyển discussion.
- Test reserve không cần LLM prediction row.
- Initial submission không bị overwrite.

RLS hoặc backend authorization đều được, nhưng test phải chứng minh behavior.

## 8. Visible Accept/Edit

- Chỉ dùng LLM consensus không audit/test.
- Hiển thị consensus label và evidence LLM.
- Accept: lưu đầy đủ tuple human-confirmed, không chỉ boolean.
- Edit: reviewer nhập đầy đủ valid labels và reason/evidence ngắn.
- Không ghi đè original LLM prediction.

## 9. Discussion/adjudication

Không cần chat realtime.

1. Hai initial human labels khác nhau.
2. App mở labels/evidence/notes sau blind phase.
3. Một người nhập proposal + rationale.
4. Người còn lại confirm hoặc reject.
5. Confirm → discussion resolved.
6. Reject/không chốt → adjudication required.
7. Phúc/Admin nhập adjudicated labels + rationale.

## 10. Draft và concurrency

- Save Draft persisted trong database.
- Reload/re-login không mất draft.
- Submit atomic: annotation + assignment/case status + audit event.
- Duplicate/concurrent submit không tạo hai initial rows.
- Có optimistic version, DB unique constraint hoặc cơ chế tương đương.

## 11. Assignment

- Double routes có đúng hai reviewer khác nhau.
- Single route có một reviewer.
- Không reviewer nhận hai slots cùng case.
- Có thể cân bằng tải bằng heuristic đơn giản + fixed seed.
- Reproducibility được ưu tiên; không cần optimizer phức tạp.

## 12. Import

App hỗ trợ:

### Task 06 production bundle

- input pool;
- two LLM predictions;
- comparison;
- routes.

### Blind-only test bundle

- record_id/text/guideline/batch/data role/route;
- không có prediction.

Import phải validate toàn bundle trước commit. Lỗi một phần → rollback. Import lại cùng run/hash không nhân đôi dữ liệu.

## 13. Export

App export:

```text
review_cases.csv
human_annotations_long.csv
discussion_resolutions.csv
adjudication_resolutions.csv
review_completion_report.md
export_manifest.json
```

App không export `final_labeled.csv` như source of truth. FINAL-07 xử lý truth table và `final_source`.

## 14. Access table

| Actor | Blind case | Visible case | Discussion | Adjudication | Import/export |
|---|---|---|---|---|---|
| Reviewer | Own assignment, no LLM | Own consensus | Own case after both submit | No | No |
| Admin/Phúc | Audit/admin view | Audit/admin view | All unresolved | Yes | Yes |
| Developer mock | Synthetic only | Synthetic only | Synthetic only | Synthetic only | Mock only |

## 15. Deployment/secrets

- Private GitHub.
- No real data in repo.
- `.env.example` only names variables.
- Streamlit secrets/Supabase config outside source.
- Do not deploy service-role key to client-side UI if avoidable.
- Disable public signup or pre-create accounts.

## 16. Backup/recovery

At minimum:

- snapshot before/after import;
- end-of-day review snapshot;
- pre-migration snapshot;
- final pre-export snapshot;
- manifest with schema version, counts and hashes;
- restore test on mock database.

## 17. Definition of Done

- All routes pass mock end-to-end.
- 4 accounts work.
- 0 blind leakage.
- 0 invalid submission stored.
- 0 duplicate/overwrite under concurrency test.
- Draft persists.
- Import idempotent.
- Export reconciles with DB.
- Backup/restore mock pass.
- App deployed and docs complete.
- No P0; P1 resolved before real import.

## 18. Quyền thay đổi thiết kế

Spec khóa behavior và contracts, không khóa:

- UUID vs integer;
- table names/count;
- ORM vs SQL;
- component layout;
- test framework;
- internal service organization.

Mọi thay đổi output/route/security behavior phải trao đổi với Phúc.
