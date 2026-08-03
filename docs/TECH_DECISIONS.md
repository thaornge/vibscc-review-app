# Technical Decisions

## Ownership Boundary

The UI layer owns Streamlit pages, layout, and mapping between UI form keys and repository payloads.

Backend/data ownership stays in:

- `src/models.py`
- `src/repository_base.py`
- `src/repository_supabase.py`
- `scripts/`

If a UI workflow needs a new query or a changed persistence behavior, document the missing repository method or field and ask the backend owner to implement it.

## Repository Use

The app uses `SupabaseRepository()` from `src.repository_supabase`.

Current UI calls:

- `get_assigned_cases_for_user`
- `save_draft`
- `submit_annotation`
- `get_discussion_cases`
- `submit_proposal`
- `resolve_discussion`
- `get_adjudication_cases`
- `submit_adjudication`

The UI does not run import/export scripts.

## Environment

Supabase config and per-account passwords are loaded from root `.env` locally:

```text
SUPABASE_URL
SUPABASE_KEY
SUPABASE_SERVICE_ROLE_KEY
APP_PASSWORD_<ANNOTATOR_CODE>
```

`SUPABASE_SERVICE_ROLE_KEY` is preferred by `SupabaseRepository`; `SUPABASE_KEY` is a fallback.

For deployment, configure the same values as platform environment variables or Streamlit secrets. The app fails closed when no active account has a configured password.

## Access Control

`src/auth.py` provides per-account login using `APP_PASSWORD_<ANNOTATOR_CODE>`. Every Streamlit entry point creates the repository and calls `require_login(repo)`, including the top-level app and each page under `pages/`, so direct page URLs are also protected.

After login, the current account is stored in Streamlit session state and shown in the sidebar. There is no post-login account switcher.

## Form Decisions

- C/S/A use compact horizontal radio controls.
- `S6` is available for `C1`.
- `remove_reason` uses fixed radio options.
- `OTHER_REMOVE` requires `Note`.
- `Uncertainty reason` is disabled until `Uncertain` is checked.
- Evidence is entered manually.
- Discussion proposals map UI labels into `proposed_eligibility`, `proposed_c`, `proposed_s`, `proposed_a`, and map rationale into `reason`.
