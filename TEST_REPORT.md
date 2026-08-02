# Test Report — Nga Checkpoint 2

Date: 2026-08-02 (Asia/Ho_Chi_Minh)

## Result

```text
21 passed in 0.04s
Python compileall: PASS
Streamlit headless startup: PASS (Uvicorn started on test port 8765)
```

## Automated coverage

- valid and invalid C/S/A dependency constraints;
- uncertainty reason requirement;
- blind response excludes prediction, audit flag and other reviewer;
- blind-only test reserve works without predictions;
- draft survives repository reload;
- duplicate initial submit is rejected;
- matching blind labels resolve by human agreement;
- disagreement opens discussion;
- discussion confirm resolves;
- discussion reject escalates and admin adjudicates;
- non-admin adjudication is rejected;
- visible Accept resolves;
- invalid state transition is rejected.

## Deferred to integration with Ngọc

- Supabase migrations/RLS and real authentication;
- four simultaneous browser/account UAT;
- atomic concurrent submit against PostgreSQL;
- Task 06 bundle import, Task 07 export and reconciliation;
- backup/restore and deployed candidate.

These are not claimed as PASS in Nga's independent FakeRepository checkpoint.
