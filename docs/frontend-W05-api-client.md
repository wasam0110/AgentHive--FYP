# Asad W05: Frontend API Client Contract and Acceptance Cases

**Owner:** Asad
**Status:** Standalone design contract; no frontend client or browser journey is implemented.
**Baseline:** `main` at `599ba7c` (2026-11-24)

This contract binds the planned frontend to the REST routes currently present in
the backend. It does not add routes or treat proposed W01 shapes as live response
schemas. The accompanying
[`demo-journeys.json`](../examples/frontend/demo-journeys.json) contains
synthetic, scripted UI interactions; it is not a server event stream.

## Client rules

- Use `/api/v1` as the API prefix and JSON request/response bodies.
- Send browser requests with credentials so the `HttpOnly` `hive_session` cookie
  is included. Do not read, store, or copy that cookie in frontend code.
- `POST /api/v1/auth/login` returns a `csrf_token`; `GET /api/v1/auth/me`
  returns the current token. Send it as `X-CSRF-Token` on every authenticated
  mutation. The browser supplies `Origin`; the backend checks it against its
  configured frontend origin.
- Treat persisted REST responses as authoritative. There is no SSE/WebSocket
  contract. A `202` from message submission means the message/run was queued,
  not that workers completed. Recover by reloading conversation detail and
  trace; never infer completion from a local spinner or optimistic message.
- Keep unsent text in local state. On a send failure, retain the draft. For a
  timeout, retry the same body with the same `Idempotency-Key`; the key must be
  8–100 characters. Reusing it for a different body returns `409`. Do not retry
  consent, approval, or refresh blindly; reload the proposal first.
- Do not cache authenticated responses. Render backend `detail` errors without
  replacing them with empty data or success-shaped fallback states.
- The overview route returns dynamic `status_counts`, not the fixed W02 bucket
  proposal. Display missing known statuses as zero if desired, but preserve
  unknown statuses rather than dropping them.
- `POST /proposals/{id}/confirmation` can be used by a customer or by staff
  performing the simulator's customer step. Staff confirmation is recorded as
  `simulated_customer_consent`; label that clearly and never present it as a
  real customer authentication event. Administrator approval remains a separate
  request.
- Only display safe summaries and allowlisted evidence fields in traces. Do not
  expose arbitrary trace `details`, credentials, or hidden model reasoning.

## Current route contract

| Purpose | Route | Request / response contract and client behavior |
|---|---|---|
| Sign in | `POST /auth/login` | `{email, password}`; sets the session cookie and returns `{user, csrf_token}`. A failed login is `401`; rate limiting is `429`. |
| Restore session | `GET /auth/me` | Returns `{user, csrf_token}`. `401` means return to sign-in. |
| Sign out | `POST /auth/logout` | Authenticated, CSRF-protected; returns `{ok: true}` and clears the session. |
| Business display/config | `GET /profile` | Returns the profile plus `profile_hash`, `mode`, and `embedding_mode`. Configuration affects labels/currency/capability display, not authorization. |
| Seeded choices | `GET /reference-data` | Returns `{customers, catalog, slots}` for the active business. Customer sessions only see their own customer row. Disabled booking yields an empty `slots` list. |
| Overview | `GET /overview` | Staff/evaluator only. Returns `total`, `completed`, `pending`, dynamic `status_counts`, seven-day `series`, nullable `completion_rate`/`average_seconds`, `recent`, `updated_at`, and nullable `oldest_pending`. Empty data is a valid response. |
| Conversation list/create | `GET /conversations`, `POST /conversations` | List is an array of persisted records. Create accepts `{customer_id?, language?, connection_id?}` and returns a conversation record (`id`, `business_id`, `customer_id`, `status`, `connection_id`, `title`, `language`, timestamps). Staff customer selection is a simulator feature; customer identity is bound by the backend. |
| Conversation detail | `GET /conversations/{id}` | Returns the conversation record plus `messages`, `proposals`. Message records use `id`, `conversation_id`, `sender`, `content`, `created_at`; proposal records include `version`, `status`, `payload`, `evidence`, `expires_at`, `expired`, `decisions`, and nullable `receipt`. |
| Trace recovery | `GET /conversations/{id}/trace?after={sequence}` | Returns trace rows ordered by sequence (up to 500), with `sequence`, `run_id`, `agent`, `status`, `summary`, `details`, `created_at`. `after` is the last-seen sequence cursor; only rows with a greater sequence are returned. |
| Submit message | `POST /conversations/{id}/messages` | Requires `Idempotency-Key`; body `{content, item_id?, slot_id?, quantity?, discount_pct?}`. Returns `202 {run_id, replayed}`. `409` can indicate a pending run/proposal or key/body conflict; reload before taking another action. |
| Approval queue | `GET /approvals` | Operator/admin/evaluator only; returns up to 100 proposal records, each with an `expired` flag. |
| Customer/simulated consent | `POST /proposals/{id}/confirmation` | Body `{version, approved, reason?}`; returns a proposal record. Confirmation alone does not execute a write. |
| Admin decision | `POST /approvals/{id}/decision` | Admin only; body `{version, approved, reason?}`. A successful approval returns `{proposal, receipt, replayed}`; a rejection returns a null receipt. Rejection needs a reason. |
| Refresh changed/expired offer | `POST /proposals/{id}/refresh` | Body `{version, slot_id?}`; returns the new proposal record. A changed version requires fresh review and consent. |

`GET /conversations` and `GET /approvals` are capped at 100 records; trace
recovery is capped at 500. The current API has no general pagination contract.
Do not invent one in the client.

### Error mapping

The backend uses standard JSON errors with a `detail` field. Handle the status
code as well as the message:

| Status | UI behavior |
|---|---|
| `401` | Clear protected screen state and request sign-in; preserve a local message draft. |
| `403` | Show access denied. Do not recast it as empty data. |
| `404` | Show not found/unavailable without revealing another customer's record. |
| `409` | Reload the affected conversation/proposal and ask the user to review current state before retrying. |
| `413`, `422` | Keep form input and show the request validation/size error. |
| `429` | Show the backend retry guidance; do not loop login requests. |
| `5xx` or network failure | Show a recoverable service error; do not claim a message, consent, approval, or execution succeeded. |

## Frontend acceptance cases

The cases define testable client behavior; they are not claims of a rendered UI.
The checked-in backend tests cover some API properties, but no browser test suite
exists yet.

| ID | Given / when | Acceptance |
|---|---|---|
| W5-A01 | Sign in, reload, then call `/auth/me` | Session is restored from the cookie; a `401` clears protected UI state. Use the CSRF token returned by the response; token rotation is not implied. |
| W5-A02 | Use customer/operator/admin/evaluator sessions | UI may hide unavailable controls, but backend `403` remains authoritative; a customer cannot see staff overview/approval data. |
| W5-A03 | Load `/profile` and `/reference-data` | Show configured terminology/currency; do not offer booking when `slots` is empty or capability is disabled. |
| W5-A04 | Load overview with no records and with unknown status values | Empty values remain valid; null rates display as unavailable; unknown status buckets remain visible or are explicitly grouped as unknown. |
| W5-A05 | Create a conversation and reload the list/detail | Use the returned server `id`; persisted messages and proposal states survive reload. Never trust a client-selected customer identity for a customer-role session. |
| W5-A06 | Submit a message with an idempotency key | Keep the draft until server acceptance; display `202` as queued/processing, not completed. After timeout, same body/key can be retried without a duplicate. |
| W5-A07 | Recover after disconnect/restart | Reload detail and trace using REST; the sequence cursor does not skip newer trace rows and replayed message submission does not duplicate the run. |
| W5-A08 | Show a proposal and collect consent | Render exact server terms, expiry and version. Consent is distinct from admin approval; neither alone is displayed as an executed action. |
| W5-A09 | Approve, reject, or act on a stale/expired proposal | Only admin may approve. Rejection needs a reason and has no receipt. A stale/expired `409` reloads the proposal; no optimistic success or mutation is shown. |
| W5-A10 | Read a trace containing evidence or internal details | Show safe summary and allowlisted evidence source/excerpt; never render hidden reasoning or raw arbitrary details. |
| W5-A11 | Exercise the three scripted PRD journeys | Match the UI assertions in `examples/frontend/demo-journeys.json`; keep the mixed-language clarification case blocked until its backend behavior is defined. |

## Mock journey review and handoff

The fixtures cover the PRD's support-plus-quote, rejected/expired sensitive
request, and mixed-language clarification/recovery scenarios. The first two
describe API-supported states, using synthetic IDs and dynamically sourced
prices/slots. The third is explicitly target-only: current deterministic
`demo_intake` classifies intents but does not produce or persist a clarification
question/state. The client must not fake that response. Before marking that
journey integrated, Wasam must agree how clarification is represented in
persisted messages/conversation state and how a follow-up resumes processing.

The old `mock_conversation_detail` in the W04 plan is a conceptual sketch, not a
valid current API response: it uses different field names and includes `tasks`
that the live detail route does not return. Use this contract and the W05
fixtures for API-shaped mocks.

## Verification boundary

W05 delivers a reviewed API contract, acceptance cases, and synthetic UI
interaction fixtures only. There is no frontend source tree, API client,
rendered screen, live browser journey, or integration claim in this deliverable.
