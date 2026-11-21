# Asad's Week 4 Frontend Component Plan & Mock Response Fixtures (W04-A & W04-B)

**Owner:** Asad
**Module:** Frontend dashboard/simulator and read-only operations overview
**Status:** Completed & Documented

---

## 1. Frontend Component Plan (W04-A)

The frontend architecture maps cleanly to the backend REST API endpoints and conversation/task states. The layout follows a responsive 3-pane simulator shell (or mobile tabbed view):

1. **Overview & Conversation List (`conversations.tsx`)**
   - Displays total counts and status breakdown (`queued`, `running`, `waiting_customer`, `waiting_admin`, `completed`, `failed`, `cancelled`).
   - Lists active customer threads with business scoping (`demo-a`, `demo-b`, `isp-pitch`).
2. **Active Chat Simulator (`chat.tsx` / `conversations.tsx`)**
   - Message history scroll container.
   - Sender differentiation (`customer`, `agent`, `system`).
   - Local draft input box with a distinct **[Send]** action that clearly separates local draft state from server confirmation.
3. **Approval Queue & Detail Modal (`approvals.tsx` / `proposal.tsx`)**
   - Lists pending proposals bound to exact `proposal_version`.
   - Separates **Customer Consent** (accepted/pending) from **Admin Approval** (approved/rejected/pending).
   - Exposes clear action buttons (`Approve`, `Reject`) with mandatory reason input for rejections.
4. **Task Trace & Inspector (`inspector.tsx`)**
   - Displays task execution status, assigned worker (`support`, `sales`, etc.), safe summary, and source-labeled evidence (`source_id`, excerpt).

---

## 2. Mock Response Fixtures (W04-A)

Mock payloads aligned with `backend/schemas/contracts/sample_payloads.json`:

```json
{
  "mock_conversation_detail": {
    "conversation_id": "conv-001",
    "customer_id": "cust-001",
    "business_id": "demo-a",
    "status": "waiting_customer",
    "language_preference": "en",
    "created_at": "2026-11-19T10:00:00Z",
    "updated_at": "2026-11-19T10:05:00Z",
    "messages": [
      {
        "message_id": "msg-001",
        "sender": "customer",
        "content": "I have a complaint about my last service and need a quote.",
        "created_at": "2026-11-19T10:00:01Z"
      },
      {
        "message_id": "msg-002",
        "sender": "agent",
        "content": "We are reviewing your complaint and preparing your quote.",
        "created_at": "2026-11-19T10:00:05Z"
      }
    ],
    "tasks": [
      {
        "task_id": "task-001",
        "intent_type": "support_complaint",
        "assigned_worker": "support",
        "status": "completed",
        "summary": "Outage recorded under ticket SR-2026-11.",
        "evidence": [
          {
            "source_id": "sr-2026-11",
            "source_type": "status_record",
            "excerpt": "Known outage, resolving within 24h."
          }
        ]
      }
    ],
    "proposals": [
      {
        "proposal_id": "prop-001",
        "proposal_version": 1,
        "action_type": "service_request",
        "status": "pending_customer_consent",
        "payload": {
          "catalog_item_id": "item-abc",
          "price": "45.00"
        },
        "expires_at": "2026-11-20T10:00:00Z"
      }
    ]
  }
}
```

---

## 3. Waiting, Error, Loading & Approval Behavior (W04-B)

### A. Loading States
- **Trigger:** When fetching conversation lists, posting messages, or triggering task runs.
- **UI Behavior:** Disable submit buttons, render skeleton loader or spinner on active chat / overview counts, and display non-blocking "Loading..." banner.

### B. Error Handling
- **Trigger:** 401 Unauthorized, 403 Forbidden (cross-customer or role denial), 422 Unprocessable Entity (malformed payload), or 500 server errors.
- **UI Behavior:**
  - Render an inline error banner with the exact error message returned by the backend.
  - Prevent optimistic updates: if a message send fails, keep the message in the local draft box so the user does not lose input.

### C. Waiting States
- **Triggers:** `waiting_customer` or `waiting_admin`.
- **UI Behavior:**
  - Display a prominent badge/status indicator on the conversation.
  - If `waiting_customer`, highlight the action required by the customer (e.g., answering clarification).
  - If `waiting_admin`, show pending approval controls for staff/admin roles.

### D. Approval-Confirmation Flow
- **Version Binding:** Every approval/consent request explicitly references `proposal_id` and `proposal_version`. If a proposal is updated on the backend, any prior consent form becomes stale and prompts the user to review the new version.
- **Distinct Decisions:** Customer consent and admin approval are handled in separate UI panels. Executing an action is blocked until both required consents/approvals are successfully recorded and valid (not expired).
