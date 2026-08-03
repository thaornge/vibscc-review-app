# Data Dictionary

This document reflects the current Supabase-backed UI contract.

## Tables Used By UI

| Table | Purpose | UI fields used |
|---|---|---|
| `users` | Login account list and role lookup | `annotator_code`, `role`, `active` or `is_active` |
| `assignments` | Reviewer work queue | `assignment_id`, `record_id`, `annotator_code`, `status`, `slot_index` |
| `records` | Review text and metadata | `record_id`, `text_annotation`, `guideline_version`, `batch_id` |
| `review_routes` | Route/status per record | `record_id`, `review_route`, `status`, `required_humans` |
| `human_annotations` | Draft/submitted human labels | `assignment_id`, `record_id`, `annotator_code`, `eligibility`, `remove_reason`, `c_label`, `s_label`, `a_label`, `uncertain`, `uncertainty_reason`, `evidence`, `rule_id`, `note`, `guideline_version`, `is_draft`, `submitted_at` |
| `discussions` | Discussion proposals | `discussion_id`, `record_id`, `proposer_code`, `proposed_eligibility`, `proposed_c`, `proposed_s`, `proposed_a`, `status`, `reason` |
| `adjudications` | Admin final labels | `record_id`, `adjudicator_code`, `final_eligibility`, `final_c`, `final_s`, `final_a`, `reasoning`, `notes` |

## Label Payload

The Streamlit form uses display keys:

```text
eligibility
remove_reason
C_label
S_label
A_label
uncertain
uncertainty_reason
evidence
rule_id
note
guideline_version
```

Before saving to Supabase, `src/ui_supabase.py` maps them to database keys:

```text
C_label -> c_label
S_label -> s_label
A_label -> a_label
uncertain -> YES/NO
```

For `eligibility=REMOVE`, the UI sends `c_label`, `s_label`, and `a_label` as `None`.

Discussion proposals are additionally mapped by `SupabaseRepository.submit_proposal`:

```text
eligibility -> proposed_eligibility
c_label -> proposed_c
s_label -> proposed_s
a_label -> proposed_a
rationale -> reason
```

Adjudication rationale is stored as `reasoning`.

## UI Validation Rules

```text
REMOVE -> remove_reason required and C/S/A blank
OTHER_REMOVE -> note required
KEEP + C0 -> S0/A0
KEEP + C1 -> S1-S6/A1-A7
KEEP + C2 -> S0/A1-A7
Uncertain -> uncertainty_reason required
```
