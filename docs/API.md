# Frontend/API screen contract

**Status:** W01 design draft; not an implemented API or frontend.

This draft maps the committed shared contracts to Asad's chat, approval and trace
screens. Its source of truth is `backend/schemas/contracts/`; the sample amounts
in those files are illustrative and must never become production defaults. The
original design baseline had no API router or frontend client. As of 2026-11-17,
`main` includes backend routes, including `/api/v1/overview`, but not a connected
frontend API client. This document remains a design contract, not evidence that
the proposed screens are implemented.

## Data shown by the screens

| Screen data | Shared contract fields | UI rule |
|---|---|---|
| Conversation list and chat | `conversation_id`, `status`, `language_preference`, `created_at`, `updated_at`; messages use `message_id`, `sender`, `content`, `language`, `created_at` | Treat IDs and status as server state. Keep an unsent message draft local; sending it does not mean it was accepted or completed. |
| Task progress and trace | `run_id`, `task_id`, `intent_type`, `assigned_worker`, task `status`, `proposal_id`, `updated_at`; worker results include `summary` and source-labelled `evidence` | Show task outcomes and evidence sources, not hidden model reasoning. An absent result is not a successful result. |
| Approval detail | `proposal_id`, `proposal_version`, `action_type`, typed `payload`, confirmation/approval requirements, policy/profile versions and expiry; decisions identify actor, decision type and the same proposal version | Customer consent and administrator approval are distinct decisions. A changed proposal version invalidates earlier decisions. |
| Business context | `display_name`, `currency`, `timezone`, `terminology`, and enabled `capabilities` | Use configured display values. A visible capability is not authorization to call an action. |

The shared contracts require the backend to bind customer and business identity.
A customer ID or role displayed or selected in a screen is not proof of identity;
every read and action must be authorized by the backend.

## Operations overview counts (W02 proposal)

The count-only response is a proposed contract for Asad's read-only overview work.
It counts conversation records, not tasks or messages, and includes every known
status even when its count is zero:

```json
{
   "total": 0,
   "status_counts": {
      "queued": 0,
      "running": 0,
      "waiting_customer": 0,
      "waiting_admin": 0,
      "partially_completed": 0,
      "completed": 0,
      "failed": 0,
      "cancelled": 0
   }
}
```

`total` equals the sum of `status_counts`. `queued` has not started processing;
`running` is being processed; `waiting_customer` or `waiting_admin` is paused for
that decision; `partially_completed` has resolved some but not all intents;
`completed` means every intent has a documented final disposition, not that every
requested action succeeded; `failed` could not reach a valid final disposition;
and `cancelled` was stopped before completion. These meanings follow the shared
conversation contract. An unknown stored status is a data-contract error, not a
bucket to silently drop.

The pure W02 aggregator has no database, network, or authorization side effects.
As of 2026-11-17, B06 has added an authenticated, role-checked and business-scoped
`/api/v1/overview` route in `backend/api/operations.py`. That route currently uses
dynamic status buckets and does not call the W02 helper; the fixed zero-bucket
behavior above remains a standalone proposal pending owner review.

## Screen journeys

1. **Chat:** show the active conversation and persisted messages. For the shared
   complaint-plus-quote sample, show the support task and its evidence separately
   from the service-request clarification. If the catalog item is missing, ask
   for it rather than inventing a quote.
2. **Approval:** show the exact proposal terms, expiry and version. Keep customer
   confirmation separate from administrator approval, and show pending,
   rejected, expired and executed outcomes distinctly. `completed` does not mean
   every requested action succeeded.
3. **Trace:** follow the conversation/run/task identifiers and display task
   status, worker, safe summary and evidence source. A failed or missing worker
   result must remain visible as a failure or pending state, not a fabricated
   success.

## Low-fidelity screen layouts (W01-B)

These sketches show information hierarchy only. They are not rendered UI or an
API implementation.

### Chat

```text
+----------------------+---------------------------+----------------------+
| Conversations        | Active conversation       | Tasks and evidence   |
| [status] title       | Customer / status         | Task status          |
| [status] title       | Message history           | Safe summary         |
|                      | Clarification if needed   | Source IDs / excerpts|
|                      | Local draft       [Send]  | Waiting state        |
++----------------------+---------------------------+----------------------+
```

### Approval

```text
+----------------------+-----------------------------------------------+
| Approval queue       | Exact proposal, version, terms and expiry     |
| Pending              | Proposal payload and supporting evidence      |
| Expired              | Customer confirmation: accepted / pending     |
| Rejected             | Administrator decision: pending / recorded    |
|                      | Reject reason or approve/reject controls       |
++----------------------+-----------------------------------------------+
```

### Trace

```text
+----------------------+-----------------------------------------------+
| Runs and tasks       | Selected task details                         |
| Run status           | Timestamp / worker / task status               |
| Task status          | Safe result summary                            |
|                      | Evidence source IDs and excerpts               |
|                      | Failure or waiting reason, when present        |
++----------------------+-----------------------------------------------+
```

The approval layout keeps customer consent distinct from administrator
approval, both tied to the displayed proposal version. The trace layout shows
evidence and failure/waiting states, never hidden model reasoning or inferred
success.

## State and open integration questions

Loading, empty, permission-denied and service-error states need distinct UI
states. Empty data is not an error, and an authorization error must not be
relabelled as an empty list. Form selections and drafts are local state; saved
conversations, proposals, decisions and receipts are server state.

The backend now contains authentication, role enforcement and overview
aggregation. The frontend API client and its response mapping remain unimplemented.
The W02 fixed-bucket proposal is not yet used by the live route; align it with the
current dynamic `status_counts` response before treating it as the frontend
contract. Do not infer cookie/CSRF behavior or permission from this screen draft.
The current contracts also do not define a proposal-status enum or receipt-to-screen
mapping; those remain integration decisions, not frontend-only decisions.
