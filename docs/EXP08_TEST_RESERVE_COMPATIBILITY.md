# EXP-08 Test Reserve Compatibility

## Kết luận

`PATCH_REQUIRED`

## Lý do

Code Day 2 hiện tại `day1_day2_nga/src/08_split_and_build_views.py` tạo train/dev/test trực tiếp trên toàn bộ modeling rows theo ratio chung. Nó chưa biểu diễn policy mới:

1. `TEST_RESERVE_CANDIDATE` chỉ là candidate pool khoảng 11,5% `N_model`, không phải toàn bộ final test.
2. Candidate phải được human blind-finalize trước.
3. Final test khoảng 10% `N_model` phải được chọn từ candidate pool, stratified chủ yếu theo `final_C` và group-aware.
4. Candidate dư phải quay lại train/dev pool.
5. Split manifest phải khóa trước preprocessing và dùng chung cho mọi view.

## Patch dự kiến sau khi input READY

- nhận `final_labeled_corpus.csv` + role/duplicate manifests;
- thêm `--candidate-role TEST_RESERVE_CANDIDATE`, `--final-test-ratio` và seed rõ ràng;
- chọn group-aware final test chỉ từ candidate pool;
- trả candidate dư về train/dev assignment;
- báo target/actual, C/S/A deviation, group leakage và reserve dư;
- thêm tests chứng minh test chỉ lấy candidate, không group leakage và manifest dùng chung.

Không chạy real split trong Checkpoint 1–2 vì FINAL-07 chưa READY.

