# ViBSCC Review App — Checkpoints 1 & 2 (Nga)

Minimal Streamlit application for VERIFY-09 human verification. This checkpoint build uses a JSON-backed `FakeRepository`; it does not call an LLM or connect to Supabase.

## Scope completed

- Reviewer/admin mock sessions (`ANN_01`…`ANN_04`, `ADMIN_PHUC`).
- `DOUBLE_BLIND`, `DOUBLE_BLIND_AUDIT`, `DOUBLE_BLIND_TEST` and `SINGLE_VISIBLE_REVIEW`.
- Visible Accept/Edit, persisted draft and locked initial submit.
- Human agreement/disagreement, discussion proposal/confirm/reject and admin adjudication.
- Label constraints enforced by repository code.
- Blind response does not expose LLM data, audit flag or the other reviewer before discussion.
- Tests and technical documents for Checkpoints 1–2.

## Run on Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open the local URL printed by Streamlit. Select a mock account in the sidebar, then use the Pages menu.

## Run tests

```powershell
python -m pytest -q
```

## Suggested walkthrough

1. `ANN_01` opens `PMOCK001` to try visible Accept/Edit.
2. `ANN_01` and `ANN_02` open `PMOCK002` to submit equal or different blind labels.
3. If labels differ, both open Discussion; one proposes and the other confirms or rejects.
4. `ADMIN_PHUC` opens Adjudication. `PMOCK004` is pre-seeded so this page is immediately testable.
5. `ANN_03`/`ANN_04` open `TMOCK001`: this test-reserve case has no LLM prediction.
6. Use **Reset toàn bộ mock data** on the home page to restore the original scenarios.

## Repository handoff

`ReviewRepository` is the UI–persistence contract. Ngọc can implement `SupabaseRepository` without changing the page workflow. See `docs/TECH_DECISIONS.md` and `docs/DATA_DICTIONARY.md`.

## Important limitations

- Mock account selector is not production authentication.
- JSON persistence is for single-process checkpoint demonstration, not concurrent multi-user deployment.
- Import/export, Supabase migrations, RLS, atomic RPC, backup/restore and deployment belong to Ngọc/integration phases.
- Synthetic data only. Never commit real/private data or secrets.

## Create the GitHub checkpoint commit

```powershell
git init
git add .
git commit -m "Complete Nga VERIFY-09 checkpoints 1 and 2"
git branch -M main
git remote add origin <PRIVATE_REPOSITORY_URL>
git push -u origin main
git rev-parse --short HEAD
```

Send the repository URL and the final command's output as the checkpoint SHA.
