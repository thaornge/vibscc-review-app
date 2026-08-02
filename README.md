# ViBSCC Review App

Streamlit UI for human review workflows backed by Supabase.

The backend/data-loading code lives in `src/repository_supabase.py`, `src/repository_base.py`, `src/models.py`, and `scripts/`. UI work should call the repository methods instead of editing backend query code directly.

## Setup

Create `.env` in the project root:

```text
SUPABASE_URL=...
SUPABASE_KEY=...
SUPABASE_SERVICE_ROLE_KEY=...
```

Install and run:

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Use the Streamlit sidebar account selector, then open the pages:

- `My Review`
- `Discussion`
- `Adjudication`

## Current UI Scope

- Reviewer assignment list from `SupabaseRepository.get_assigned_cases_for_user`.
- Draft save through `save_draft`.
- Submit through `submit_annotation`.
- Discussion proposal/resolve through `submit_proposal` and `resolve_discussion`.
- Admin adjudication through `get_adjudication_cases` and `submit_adjudication`.

The `scripts/` directory contains import/export utilities that have already been run for cloud data. Do not rerun them unless the backend/data owner asks for it.

## Verification

```powershell
python -m py_compile app.py src\app_context.py src\ui_supabase.py src\repository_supabase.py pages\01_My_Review.py pages\02_Discussion.py pages\03_Adjudication.py
python -m pytest tests\test_validators.py
```
