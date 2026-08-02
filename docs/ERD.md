# Preliminary ERD

```mermaid
erDiagram
    PROFILE ||--o{ REVIEW_ASSIGNMENT : receives
    IMPORT_RUN ||--o{ RECORD : imports
    RECORD ||--o{ LLM_PREDICTION : has
    RECORD ||--|| REVIEW_CASE : opens
    REVIEW_CASE ||--o{ REVIEW_ASSIGNMENT : requires
    REVIEW_ASSIGNMENT ||--o| HUMAN_ANNOTATION : produces
    REVIEW_CASE ||--o| DISCUSSION_RESOLUTION : may_need
    REVIEW_CASE ||--o| ADJUDICATION_RESOLUTION : may_need
    PROFILE ||--o{ AUDIT_EVENT : performs
```

Reference constraints for Ngọc's database implementation:

- unique `(record_id, import_run_id)` active case;
- unique `(record_id, model_slot, run_id)` prediction;
- unique `(case_id, review_slot)` and `(case_id, reviewer_id)`;
- one active initial annotation per assignment;
- one reviewer cannot fill both slots;
- single-visible requires one visible assignment;
- double routes require two different blind reviewers;
- submitted initial rows must remain immutable/versioned.
