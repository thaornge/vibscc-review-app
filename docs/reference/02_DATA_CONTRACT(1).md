# ViBSCC Day 3 - Data Contract

## 1. Nguyên tắc chung

- `record_id` là khóa xuyên pipeline và không được sửa.
- Không join theo row order.
- CSV UTF-8; header exact theo contract hoặc có documented mapping.
- Null dùng empty field trong CSV, không dùng chuỗi `NA` trừ khi code cũ bắt buộc và mapping rõ.
- Mỗi output có schema version/run ID/guideline version trong manifest/report.
- Internal DB schema có thể khác; export contract không được đổi không báo Phúc.

## 2. Nhãn hợp lệ

- eligibility: KEEP, REMOVE.
- C: C0, C1, C2.
- S: S0..S6.
- A: A0..A7.
- uncertain: true/false hoặc YES/NO, nhưng export phải chuẩn hóa.

Constraints:

```text
REMOVE → C/S/A null, remove_reason required
KEEP+C0 → S0,A0
KEEP+C1 → S1-S6,A1-A7
KEEP+C2 → S0,A1-A7
```

## 3. Task 04B outputs

### `gold_dev_llm_input.csv`

- record_id
- text_annotation
- guideline_version
- batch_id

### `gold_dev_reference.csv`

- record_id
- final_eligibility
- final_C
- final_S
- final_A
- resolution_source
- guideline_version

### `gold_hidden_llm_input.csv`

Giống dev input, không có labels/sample subtype.

### `gold_hidden_reference_private.csv`

Giống dev reference; private.

### `llm_production_input.csv`

- record_id
- text_annotation
- guideline_version
- batch_id

### `test_reserve_candidates_blind_input.csv`

- record_id
- text_annotation
- guideline_version
- batch_id
- data_role = TEST_RESERVE_CANDIDATE
- review_route = DOUBLE_BLIND_TEST

### `data_role_manifest_private.csv`

- record_id
- text_duplicate_group
- data_role
- selection_seed
- selection_order
- source_pool_version
- guideline_version
- run_id

## 4. Task 06 → App

### `llm_predictions_long.csv`

- record_id
- run_id
- model_slot
- model_id
- model_version
- prompt_version
- guideline_version
- predicted_eligibility
- predicted_C
- predicted_S
- predicted_A
- uncertain
- uncertainty_reason
- evidence
- parse_status
- constraint_valid

Exactly two valid/importable prediction rows per production record unless route reason is prediction error represented explicitly.

### `llm_comparison.csv`

- record_id
- comparison_status: EXACT/DISAGREE/ERROR
- llm_consensus
- consensus_eligibility
- consensus_C
- consensus_S
- consensus_A
- disagreement_axes
- any_uncertain
- any_invalid

### `review_routes.csv`

- record_id
- review_route
- route_reason
- audit_flag
- required_humans

Allowed production routes:

- DOUBLE_BLIND
- DOUBLE_BLIND_AUDIT
- SINGLE_VISIBLE_REVIEW

## 5. Blind test → App

`test_reserve_candidates_blind_input.csv` không có LLM predictions. App phải import route `DOUBLE_BLIND_TEST` độc lập.

## 6. App → FINAL-07

### `review_cases.csv`

- record_id
- import_run_id
- data_role
- review_route
- route_reason
- audit_flag
- required_reviews
- case_status
- resolved_at

### `human_annotations_long.csv`

- record_id
- assignment_id
- annotator_code
- review_slot
- visibility_mode
- decision_action
- eligibility
- remove_reason
- C_label
- S_label
- A_label
- uncertain
- uncertainty_reason
- evidence
- rule_id
- note
- guideline_version
- started_at
- submitted_at

### `discussion_resolutions.csv`

- record_id
- discussion_status
- resolved_eligibility
- resolved_C
- resolved_S
- resolved_A
- proposed_by
- confirmed_by_slot_1
- confirmed_by_slot_2
- rationale
- resolved_at

### `adjudication_resolutions.csv`

- record_id
- adjudicated_eligibility
- adjudicated_C
- adjudicated_S
- adjudicated_A
- adjudicator_code
- rationale
- guideline_version
- resolved_at

### `export_manifest.json`

- schema_version
- import_run_id(s)
- exported_at
- row counts
- unresolved count
- sha256 per file

## 7. FINAL-07 → EXP-08

Minimum:

- final_labeled_corpus.csv: record_id, text_annotation, final eligibility/C/S/A, final_source, guideline_version, data_role, text_duplicate_group.
- finalization_report.md: counts, unresolved=0, constraint errors=0.
- role/duplicate manifests.

EXP-08 không tự resolve review history.

## 8. Provenance

Final source categories tham chiếu:

- HUMAN_GOLD
- HUMAN_BLIND_AGREEMENT
- HUMAN_DISCUSSION_CONSENSUS
- HUMAN_ADJUDICATED
- HUMAN_VERIFIED_LLM
- HUMAN_CORRECTED_LLM

App không nhất thiết tính final_source; FINAL-07 áp truth table dựa trên exported history.
