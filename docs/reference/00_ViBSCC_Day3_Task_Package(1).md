# ViBSCC Day 3 \- Task Package tổng của cả nhóm

## 1\. Mục tiêu chung

Day 3 không yêu cầu hoàn thành toàn bộ corpus. Mục tiêu là chuẩn bị những khối kỹ thuật có thể xây bằng mock ngay bây giờ, để khi guideline freeze và dữ liệu thật xuất hiện chỉ cần thay input và chạy:

- Nhung hoàn thiện sampling/export contract.  
- Nga và Ngọc dựng công cụ verify nhiều người dùng.  
- Nga đọc trước luồng post-gold và Task 08 để tránh code Day 3 không tương thích với dữ liệu thật sau này.

## 2\. Task và deadline

| Người | Task | Output chính | Deadline |
| :---- | :---- | :---- | :---- |
| Nhung | SAMPLE-04B | Code export, mock outputs, validators, reports | 12:00 02/08/2026 |
| Nga | VERIFY-09A | UI/workflow, FakeRepository, repo/integration lead | 17:00 03/08/2026 |
| Ngọc | VERIFY-09B | Supabase, importer/exporter, integrity/backup | 17:00 03/08/2026 |
| Nga \+ Ngọc | Integration/deploy | Private repo, deployed app, UAT, sample Task 07 export | 17:00 03/08/2026 |
| Nga | POST-GOLD LLM-06 \+ EXP-08 | Chỉ chạy khi input được Phúc đánh dấu READY | Không cố định |

## 3\. File task riêng

- **Nhung:** `01_TASKS/01_Nhung_TASK.md`  
- **Nga \+ Ngọc:** `01_TASKS/02_Nga_Ngoc_VERIFY_APP_TASK.md`  
- **Nga \- giai đoạn sau gold/final corpus:** `01_TASKS/03_Nga_POST_GOLD_LLM06_AND_EXP08_TASK.md`

Mọi người đọc task tổng trước rồi mới đọc task riêng.

## 4\. Mốc Nga-Ngọc

### Checkpoint 1 \- 23:00 ngày 01/08/2026

Nga gửi repo private, commit SHA, `TECH_DECISIONS.md`, repo tree, schema/ERD sơ bộ và command chạy mock. Ngọc xác nhận đã vào repo và thống nhất contract.

### Checkpoint 2 \- 12:00 ngày 02/08/2026

- Nga: UI mock chạy blind/visible/discussion/adjudication với fake backend.  
- Ngọc: schema, persistence, import/export và validator chạy riêng với mock.

### Checkpoint 3 \- 12:00 ngày 03/08/2026

Deployed candidate, integration commit, sample import/export và UAT sơ bộ. Không được còn lỗi P0.

### Final \- 17:00 ngày 03/08/2026

Private repo, deployed app, release/final SHA, UAT 4 account, test report, docs và sample export.

## 5\. Input hiện có và chưa có

### Đã có

- Annotation pool không GLiNER: link trong `02_SHARED_SPEC/00_INPUT_STATUS_AND_LINKS.md`.  
- Guideline folder và PDF p1.0.

### Chưa có

- Frozen guideline.  
- Manifest hoàn chỉnh sau toàn bộ calibration.  
- Gold thật và reference thật.  
- Test reserve thật.  
- LLM production inputs/predictions/routes thật.  
- Final labeled corpus thật.

Không chờ input chưa có. Dùng synthetic mock cùng schema.

## 6\. Yêu cầu chung

### MUST

- Giữ nguyên `record_id`.  
- Không join bằng row order.  
- Lưu đầy đủ provenance.  
- Blind route không lộ LLM hoặc human khác trước khi submit.  
- Multi-user dùng shared persistent storage.  
- Validator chặn constraint sai.  
- Export nối được FINAL-07/EXP-08.  
- Có tests và report PASS/FAIL.

### MUST NOT

- Đưa real raw/private mapping lên GitHub.  
- Để secret trong source/repo/log.  
- Cho LLM consensus tự động thành final label.  
- Dùng visible review để tạo test reference.  
- Ghi đè initial human label sau submit.  
- Xây chức năng ngoài scope làm chậm deadline.

### SHOULD

- Streamlit \+ Supabase.  
- Private GitHub repository do Nga tạo, add Ngọc và Phúc.  
- Dùng layer/interface để Nga và Ngọc làm song song.  
- Có backup snapshot và reconciliation.

## 7\. Phân loại lỗi nghiệm thu

- **P0 \- blocker:** sai route, lộ blind, mất/ghi đè dữ liệu, thiếu export, invalid labels được lưu, không chạy multi-user.  
- **P1 \- sửa trước real data:** draft không bền, import không idempotent, backup/restore lỗi, thiếu command/docs quan trọng.  
- **P2 \- không chặn:** UI chưa đẹp, mobile chưa hoàn hảo, thiếu dashboard, naming chưa tối ưu.

## 8\. Cách nộp

Chi tiết ở `06_SUBMISSIONS/`. Tin nhắn nhóm chỉ cần link \+ trạng thái ngắn; toàn bộ command, counts, logs, limitations đặt trong README/report.

## 9\. Điểm cần trao đổi với Phúc trước khi tự đổi

- Thay route hoặc số human reviewer.  
- Đổi schema export/handoff.  
- Đổi policy gold/test reserve.  
- Cho dữ liệu thật lên repo/app khi chưa được duyệt.  
- Thay stack làm ảnh hưởng deadline/integration.  
- Bất kỳ xung đột nào giữa guideline và contract.

