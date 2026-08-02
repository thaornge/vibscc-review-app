# User Guide

## Start

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Select an account in the sidebar. Reviewer accounts open review and discussion workflows. Admin accounts open adjudication.

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

Rejecting a proposal sends the record to adjudication.

## Adjudication

1. Log in as an admin account.
2. Open `Adjudication`.
3. Select an escalated record.
4. Enter the final label and rationale.
5. Submit adjudication.
