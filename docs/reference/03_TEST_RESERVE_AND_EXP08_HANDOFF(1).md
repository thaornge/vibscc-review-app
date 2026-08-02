# Test Reserve Candidate → Human Blind → FINAL-07 → EXP-08

## 1. Mục tiêu

Tạo benchmark test gần phân phối thật, không bị thiên về những câu hai LLM bất đồng hoặc hard cases.

## 2. Quy trình bắt buộc

### Step 1 - Nhung reserve candidates

Sau guideline freeze và gold selection:

```text
N_model = canonical KEEP cuối - 500 gold
candidate reserve target ≈ 11,5% N_model
```

- random representative;
- group-aware;
- chọn trước khi dùng LLM outcomes để quyết định độ khó;
- exclude Training/Calibration/Gold;
- output blind-only bundle.

### Step 2 - Review app

Mọi candidate:

```text
DOUBLE_BLIND_TEST
→ 2 human blind
→ agreement/discussion/adjudication
```

Không yêu cầu LLM predictions. Không visible Accept/Edit.

### Step 3 - FINAL-07

Phúc merge human history và tạo final labels/provenance cho toàn bộ candidates.

### Step 4 - Nga EXP-08

Sau final labels:

```text
candidate reserve ≈ 11,5%
→ select final test ≈ 10% N_model
→ stratified by final_C + group-aware
```

- final test gần corpus distribution;
- group leakage = 0;
- reserve dư trở lại train/dev pool;
- split manifest khóa trước preprocessing;
- mọi models/views dùng cùng test.

## 3. Không được làm

- Không lấy toàn bộ LLM disagreement làm test.
- Không chỉ lấy uncertain/hard/random audit.
- Không dùng visible LLM review để tạo test label.
- Không tune prompt/model/routing trên test.
- Không cho từng preprocessing scenario tự chọn test riêng.

## 4. Handoff files

### Nhung → App

- test_reserve_candidates_blind_input.csv
- private candidate manifest (Phúc/Nhung giữ)

### App → Phúc FINAL-07

- review_cases.csv
- human_annotations_long.csv
- discussion/adjudication resolutions
- export manifest/completion report

### Phúc → Nga

- final-labeled candidate records
- role/duplicate manifests
- finalization report

## 5. Task 08 report

Nga báo:

- N_model;
- candidate target/actual;
- final test target/actual;
- C/S/A distribution corpus vs test;
- group leakage count;
- reserve dư count;
- warnings/constraint conflicts;
- seed/config.
