# Mock Data

This directory contains CSV fixtures used by backend import/export scripts.

The cloud database has already been loaded by the backend/data owner. UI work should not rerun scripts in `scripts/` unless explicitly asked.

Important files:

- `mock_users.csv`
- `llm_input_pool_mock.csv`
- `llm_predictions_long_mock.csv`
- `review_routes_mock.csv`
- `test_reserve_candidates_mock.csv`

Legacy JSON mock files may still exist for tests or old local workflows, but the active Streamlit UI is wired to Supabase.
