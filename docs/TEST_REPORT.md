# Test Report

Ngày chạy: 02/08/2026. Môi trường kiểm tra: Python 3.12, pytest 9.1.1, Streamlit 1.60.0.

## Review app Checkpoint 1–2

Command:

```text
python -m pytest -q tests
```

Kết quả: `18 passed in 0.04s`.

Coverage hành vi:

- C/S/A/REMOVE/uncertainty validation;
- route/assignment integrity;
- blind payload không chứa prediction, route reason, audit flag hoặc reviewer khác;
- visible exact consensus;
- draft persistence sau repository reopen;
- submit lock;
- two-human agreement;
- visible Accept/Edit;
- concurrent duplicate submit chỉ một lần thành công;
- test reserve không có LLM prediction;
- discussion confirm;
- adjudication;
- mock coverage cho consensus/disagreement/uncertain/invalid/audit/test.

## Day 1–2 regression

Command chạy trong `day1_day2_nga/`:

```text
python -m pytest -q tests
```

Kết quả: `27 passed in 0.34s`.

Đã bổ sung dependency bị thiếu `PyYAML` và `jsonschema` vào requirements của Day 1–2.

## App smoke

Command:

```text
python -m streamlit run app.py --server.headless true
```

Kết quả: PASS — server khởi động và in URL local.

## Chưa thuộc Checkpoint 2 của Nga

- four-device UAT với shared Supabase;
- RLS/security test trên production adapter;
- production import/export reconciliation;
- deployed URL.

