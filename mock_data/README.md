# Synthetic mock coverage

Nguồn fixture chính là `src/mock_seed.py`; app tự import fixture vào `.local/mock_state.json` ở lần chạy đầu.

| Record | Route | Scenario |
|---|---|---|
| V001 | SINGLE_VISIBLE_REVIEW | consensus, Accept |
| V002 | SINGLE_VISIBLE_REVIEW | consensus, Edit |
| B001 | DOUBLE_BLIND | human disagreement, discussion demo |
| B002 | DOUBLE_BLIND | LLM uncertain |
| A001 | DOUBLE_BLIND_AUDIT | random audit |
| I001 | DOUBLE_BLIND | invalid prediction |
| T001 | DOUBLE_BLIND_TEST | no LLM prediction, normal review |
| T002 | DOUBLE_BLIND_TEST | no LLM prediction, adjudication demo |

Fixture chỉ chứa dữ liệu synthetic, không chứa raw/private mapping hay secret.

