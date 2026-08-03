# User Guide

## Start

Create `.env` with Supabase credentials and the app password:

```text
SUPABASE_URL=...
SUPABASE_KEY=...
SUPABASE_SERVICE_ROLE_KEY=...
APP_PASSWORD_ANN_01=...
APP_PASSWORD_ANN_02=...
APP_PASSWORD_ADMIN_PHUC=...
```

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Sign in with an account and its password. Reviewer accounts open review and discussion workflows. Admin accounts open adjudication.

## My Review

1. Open `My Review`.
2. Select an assignment.
3. Read the record text.
4. Fill the label form.
5. Use `Save Draft` to save without final submission.
6. Use `Submit` to submit the annotation.

For `REMOVE`, choose one remove reason. If the reason is `OTHER_REMOVE`, fill `Note`.

## Discussion

1. Open `Discussion`.
2. Select a record requiring discussion.
3. Review both submitted annotations.
4. Create a proposal, or confirm/reject an existing proposal.

Proposal labels and rationale are saved to the discussion record. Rejecting a proposal sends the record to adjudication.

## Adjudication

1. Log in as an admin account.
2. Open `Adjudication`.
3. Select an escalated record.
4. Enter the final label and rationale.
5. Submit adjudication.
