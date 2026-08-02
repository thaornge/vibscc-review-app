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

Supabase config is loaded from root `.env`:

```text
SUPABASE_URL
SUPABASE_KEY
SUPABASE_SERVICE_ROLE_KEY
```

`SUPABASE_SERVICE_ROLE_KEY` is preferred by `SupabaseRepository`; `SUPABASE_KEY` is a fallback.

## Form Decisions

- C/S/A use compact horizontal radio controls.
- `S6` is available for `C1`.
- `remove_reason` uses fixed radio options.
- `OTHER_REMOVE` requires `Note`.
- `Uncertainty reason` is disabled until `Uncertain` is checked.
- Evidence is entered manually.
