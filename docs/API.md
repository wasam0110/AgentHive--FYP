# Frontend/API screen contract

**Status:** W01 design draft; not an implemented API or frontend.

This draft maps the committed shared contracts to Asad's chat, approval and trace
screens. Its source of truth is `backend/schemas/contracts/`; the sample amounts
in those files are illustrative and must never become production defaults. The
committed `main` baseline has no API router or frontend client yet.

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

## State and open integration questions

Loading, empty, permission-denied and service-error states need distinct UI
states. Empty data is not an error, and an authorization error must not be
relabelled as an empty list. Form selections and drafts are local state; saved
conversations, proposals, decisions and receipts are server state.

The shared conversation contract describes proposed conversation routes, but
authentication, role enforcement, overview aggregation, response envelopes and
the frontend API client still need agreement and implementation. Do not infer
cookie/CSRF behavior, route availability or permission from this screen draft.
The current contracts define task statuses and decision values, but not a
proposal-status enum or receipt-to-screen mapping. Those are integration gates,
not frontend-only decisions.
