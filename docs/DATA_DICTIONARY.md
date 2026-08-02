# Checkpoint Data Dictionary

The JSON mock is not the final database schema. It demonstrates the minimum objects that the Supabase repository must map.

| Object | Important fields |
|---|---|
| User | `user_id`, `annotator_code`, `role`, `is_active` |
| Review case | `case_id`, immutable `record_id`, text, guideline/batch, route, status |
| Assignment | `assignment_id`, reviewer, slot, visibility, status, draft, submitted annotation |
| LLM consensus | full eligibility/C/S/A tuple and evidence; visible route only |
| Discussion | proposer, proposed tuple, rationale, response and status |
| Adjudication | admin, final decision tuple, rationale, resolved time |

Production database must additionally store full Task 06 prediction provenance, import/export runs, content hashes, row versions and append-only audit events as defined in the shared specification.

## Human annotation contract

`eligibility`, `remove_reason`, `C_label`, `S_label`, `A_label`, `uncertain`, `uncertainty_reason`, `evidence`, `rule_id`, `note`, `guideline_version`, decision action and timestamps.

Constraints:

```text
REMOVE → C/S/A null + remove_reason required
KEEP+C0 → S0/A0
KEEP+C1 → S1-S6/A1-A7
KEEP+C2 → S0/A1-A7
```
