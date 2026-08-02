# Data Dictionary

This document reflects the current Supabase-backed UI contract.

## Tables Used By UI

| Table | Purpose | UI fields used |
|---|---|---|
| `users` | Sidebar account selector | `annotator_code`, `role`, `active` or `is_active` |
| `assignments` | Reviewer work queue | `assignment_id`, `record_id`, `annotator_code`, `status`, `slot_index` |
| `records` | Review text and metadata | `record_id`, `text_annotation`, `guideline_version`, `batch_id` |
| `review_routes` | Route/status per record | `record_id`, `review_route`, `status`, `required_humans` |
| `human_annotations` | Draft/submitted human labels | `assignment_id`, `record_id`, `annotator_code`, labels, notes |
| `discussions` | Discussion proposals | `discussion_id`, `record_id`, `proposer_code`, proposal labels, `status`, `rationale` |
| `adjudications` | Admin final labels | `record_id`, `adjudicator_code`, final labels, `rationale` |

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

## UI Validation Rules

```text
REMOVE -> remove_reason required and C/S/A blank
OTHER_REMOVE -> note required
KEEP + C0 -> S0/A0
KEEP + C1 -> S1-S6/A1-A7
KEEP + C2 -> S0/A1-A7
Uncertain -> uncertainty_reason required
```
