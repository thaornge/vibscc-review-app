# Nga - Task tiếp nối sau Gold: LLM-06 và EXP-08

> Đây là task đọc trước để hiểu luồng dữ liệu sau Day 3. Không có deadline ngày giờ cố định vì phụ thuộc dữ liệu thật. Khi input được Phúc đánh dấu `READY`, Phúc và Nga mới chốt deadline của stage tương ứng.

> Đối chiếu tên: phần nhóm đôi khi gọi “Task 5” trong trao đổi là phần hai LLM, tương ứng `LLM-06` trong pipeline Day 2. Không viết lại toàn bộ Task 06; chỉ integration, evaluation và production run.

## A. Khi có gold_dev

### Nga nhận từ ai

Từ Nhung/SAMPLE-04B:

```text
gold_dev_llm_input.csv
```

Từ Phúc hoặc người Phúc chỉ định:

```text
gold_dev_reference.csv
frozen guideline + guideline_version
gold manifest
```

### Nga làm gì

1. Chạy đúng hai LLM trên 200 gold_dev records.
2. So prediction với human-adjudicated reference.
3. Tính:
   - Macro-F1 C/S/A;
   - exact triplet;
   - conditional S/A;
   - parse/invalid JSON rate;
   - constraint violation;
   - uncertainty behavior;
   - consensus precision;
   - both-LLMs-wrong rate.
4. Được phép sửa prompt, few-shot, parser, uncertainty instruction, retry/configuration, model/version và routing policy.
5. Lưu mọi thay đổi trong changelog.
6. Trình Phúc duyệt và khóa:
   - model IDs/versions;
   - prompt version;
   - parser/schema version;
   - temperature/config;
   - retry policy;
   - routing/audit config.

### Output

```text
gold_dev_predictions/
gold_dev_evaluation.csv
gold_dev_evaluation_report.md
locked_llm_config.json
locked_prompt.txt
prompt_change_log.md
```

## B. Khi có gold_hidden

### Nga nhận từ ai

Từ Nhung:

```text
gold_hidden_llm_input.csv
```

Nga không nhận hidden reference trước khi run đã khóa.

### Nga làm gì

1. Dùng nguyên locked config từ gold_dev.
2. Chạy hai LLM trên toàn bộ 300 hidden records.
3. Không sửa prompt/model/parser/routing dựa trên từng lỗi hidden.
4. Khóa predictions và run manifest.
5. Gửi output cho Phúc.
6. Phúc/người được giao mới mở `gold_hidden_reference_private.csv` để evaluation.

### Output trước mở reference

```text
gold_hidden_predictions_long.csv
gold_hidden_comparison.csv
gold_hidden_run_manifest.json
gold_hidden_run_log.txt
```

### Output evaluation

```text
gold_hidden_evaluation.csv
gold_hidden_evaluation_report.md
```

Nếu hidden không đạt, không tự tune rồi chạy lại cùng hidden. Báo Phúc để quyết định dừng, sửa lỗi kỹ thuật, unfreeze guideline hoặc tạo hidden evaluation mới.

## C. Khi gold_hidden được Phúc chấp thuận

### Nga nhận từ Nhung

```text
llm_production_input.csv
llm_input_manifest_private.csv
```

### Nga chạy LLM-06 production

```text
input
→ LLM 1 độc lập
→ LLM 2 độc lập
→ parse/validate
→ compare eligibility+C+S+A
→ routing
```

### Output cho review app

```text
llm_predictions_long.csv
llm_comparison.csv
review_routes.csv
llm_run_report.md
llm_run_manifest.json
```

Bổ sung `uncertainty_reason` thành cột structured nếu code hiện tại chưa có. App chỉ import output, không gọi LLM trực tiếp.

## D. EXP-08 sau khi có final labels

### Nga nhận input từ ai

Từ Phúc/FINAL-07:

```text
final_labeled_corpus.csv
final_labeled_master_private.csv hoặc role-compatible private export
finalization_report.md
```

Từ Nhung:

```text
assignment_manifest_master.csv
test_reserve_candidates_manifest.csv
data_role_manifest.csv
duplicate_group_manifest.csv
```

Không đọc trực tiếp DB app để tự suy ra final labels. Luồng đúng:

```text
Review app export
→ Phúc chạy FINAL-07
→ Phúc bàn giao final-labeled input
→ Nga chạy EXP-08
```

### Nga làm gì

1. Validate unique IDs, no unresolved, constraints, roles và duplicate groups.
2. Loại gold khỏi modeling.
3. Áp dụng chính sách Training/Calibration mới nhất do Phúc chốt.
4. Từ candidate reserve ~11,5% đã có human final labels, chọn final test ~10% `N_model`:
   - group-aware;
   - stratified chủ yếu theo final_C;
   - gần corpus distribution;
   - không ưu tiên LLM disagreement/hard cases;
   - report size/distribution deviation;
   - reserve dư quay lại train/dev pool.
5. Chia train/dev để tổng thể gần 8:1:1.
6. Khóa `split_manifest.csv`.
7. Tạo preprocessing views sau split; mọi scenario dùng cùng manifest.

### Output

```text
split_manifest.csv
split_quality_report.md
model_views.parquet hoặc format đã chốt
train/dev/test exports nếu cần
run_manifest.json
```

## E. Chính sách Training/Calibration

Mặc định loại khỏi modeling. Nếu Phúc cho tái sử dụng:

- re-review bằng frozen guideline;
- adjudicate;
- chỉ thêm train;
- không thêm dev/test;
- lưu role/source/changelog.

Nga không tự đổi policy dựa trên số lượng mẫu.

## F. Handoff và trigger

| Stage | Trigger |
|---|---|
| Gold-dev run | Guideline frozen + gold_dev input/reference READY |
| Gold-hidden run | Locked config approved + hidden input READY |
| Production LLM | Hidden evaluation được Phúc chấp thuận |
| EXP-08 real run | FINAL-07 hoàn tất + final inputs READY |

Khi stage mở, Nga xác nhận ngắn:

```text
[Stage] input đã nhận: [link]. Trạng thái READY/BLOCKED. Điểm cần chốt: ...
```

Nếu có điểm chưa rõ, input không khớp hoặc cần đổi contract/policy, liên hệ Phúc trước khi chạy.
