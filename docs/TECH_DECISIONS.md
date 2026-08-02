# Technical Decisions — VERIFY-09

## Status

Checkpoint 1 contract and Nga's independent Checkpoint 2 mock implementation.

## Stack

- Python 3.10+ and Streamlit for the minimal UI.
- `pytest` for automated behavior tests.
- `FakeRepository` backed by a local JSON state file for Checkpoint 2.
- Supabase PostgreSQL/Auth remains the integration target owned by Ngọc.

## Architecture

```text
Streamlit pages
      ↓
ReviewRepository interface
      ↓
FakeRepository (now) / SupabaseRepository (integration)
```

The fake repository is intentionally replaceable. The UI does not read JSON directly.

## Locked repository contract

The interface in `src/repository_base.py` covers:

- users and reviewer assignments;
- reviewer-safe case view;
- save draft and submit;
- discussion list, proposal and response;
- adjudication list and submission.

Ngọc may add importer/exporter/admin methods without changing these method signatures. Any incompatible change must be agreed before integration.

## Blind integrity

Blind filtering occurs in `case_for_reviewer`, before data reaches Streamlit. Blind responses exclude predictions, audit flag and the other assignment. Both submitted annotations become available only after the case enters discussion/resolution states.

Production must reproduce this behavior through backend authorization and/or Supabase RLS; hiding widgets alone is insufficient.

## Draft and submit semantics

- Draft is mutable and persisted to a JSON state file in the mock.
- Initial submit validates labels, changes assignment to `SUBMITTED` and removes draft.
- A second submit on the same assignment is rejected.
- Production submit must be one atomic database transaction/RPC and use unique constraints or optimistic versioning.

## State machine

Double routes: first submit → `WAITING_SECOND_REVIEW`; matching tuple → `RESOLVED_HUMAN_AGREEMENT`; different tuple → `DISCUSSION_REQUIRED`.

Discussion: proposal → `DISCUSSION_IN_PROGRESS`; confirm → `RESOLVED_DISCUSSION`; reject → `ADJUDICATION_REQUIRED`.

Admin resolution: `ADJUDICATION_REQUIRED` → `RESOLVED_ADJUDICATION`.

Visible resolution: Accept/Edit → their corresponding resolved statuses.

## Data and privacy

- `record_id` is immutable and used for joins; row order is never an identity.
- Only synthetic mock text is committed.
- `.env`, Streamlit secrets and runtime state are ignored.
- The application never runs an LLM and never converts LLM consensus directly into a final label.

## Day 2 reuse decision

The review app is a separate project. Day 2 Task 06 remains an upstream pipeline and Task 08 remains downstream. Task 06 mock outputs can be transformed into app import fixtures during integration. Shared label constraints are aligned conceptually; the working Day 2 scripts are not copied or destabilized.

## Known checkpoint limitation

JSON state is persistent across reloads but cannot guarantee real multi-user concurrency. That requirement is deferred to the Supabase integration phase, where database uniqueness, transactions and access policies must be tested.
