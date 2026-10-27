# Conversation and Message Contracts

Version: 1.0 — draft W01-A (2026-10-26)
Owner: Wasam (conversation persistence, auth, orchestration)
Consumers: Asad (conversation status for Overview and Chat screens),
           Arif (conversation_id + run_id on proposals/receipts),
           Shizza (customer_id binding for workers)

All timestamps are UTC ISO-8601 strings.

---

## ConversationStatus

```python
class ConversationStatus(str, Enum):
    QUEUED             = "queued"
    RUNNING            = "running"
    WAITING_CUSTOMER   = "waiting_customer"
    WAITING_ADMIN      = "waiting_admin"
    PARTIALLY_COMPLETED = "partially_completed"
    COMPLETED          = "completed"
    FAILED             = "failed"
    CANCELLED          = "cancelled"
```

`COMPLETED` may include a rejected request if every intent has a documented final resolution.
It must not imply every requested action was performed.

---

## Conversation record (database shape)

```python
class ConversationRecord:
    conversation_id: str      # server-assigned UUID
    customer_id: str          # server-validated; never trusted from a customer message
    business_id: str          # from active BusinessProfile; set server-side
    status: ConversationStatus
    language_preference: str  # updated by Intake from language_detected
    created_at: str           # UTC ISO-8601
    updated_at: str           # UTC ISO-8601
```

---

## Message record (database shape)

```python
class MessageSender(str, Enum):
    CUSTOMER  = "customer"
    SYSTEM    = "system"    # backend-composed response
    OPERATOR  = "operator"  # human operator custom response

class MessageRecord:
    message_id: str           # server-assigned UUID
    conversation_id: str      # foreign key → ConversationRecord
    customer_id: str          # denormalized for access-check queries
    sender: MessageSender
    content: str              # raw text; treated as untrusted for customer messages
    language: str             # detected or set at creation
    created_at: str           # UTC ISO-8601
```

---

## Run record (one run per message processing cycle)

```python
class RunRecord:
    run_id: str               # server-assigned UUID
    conversation_id: str      # foreign key → ConversationRecord
    status: ConversationStatus  # mirrors conversation status while active
    graph_step_count: int     # incremented each step; hard limit 12 (PRD default)
    retry_count: int          # transient model/tool retries; max 2 (PRD default)
    created_at: str           # UTC ISO-8601
    completed_at: str | None
```

---

## Access rules

| Rule | Enforced by |
|---|---|
| A customer may only read messages where customer_id matches their authenticated identity | Backend endpoint (W02-A / W03-A) |
| An operator/admin may read any conversation in the active business | Backend endpoint with role check |
| customer_id in a request body is ignored; identity comes from the authenticated session | Auth middleware (W02-B) |
| A conversation cannot change business_id after creation | DB constraint + loader |

---

## API endpoints that consume these shapes (reference — implemented in W02-A / W03-A)

| Endpoint | Shape returned |
|---|---|
| POST /api/v1/conversations | ConversationRecord (created) |
| POST /api/v1/conversations/{id}/messages | MessageRecord (created) + run_id |
| GET /api/v1/conversations/{id} | ConversationRecord + list[MessageRecord] + list[TaskStatusRecord] |

These endpoint signatures are the agreed contract. Do not implement them yet — that is W02-A.

---

## Open points for teammates

- **Asad:** The Overview screen needs `status` and `updated_at` from ConversationRecord,
  plus a count of conversations per status bucket. Confirm this is sufficient for W02-A's
  overview endpoint or raise in W01-B.
- **Arif:** Proposals must include `conversation_id` and `run_id` from RunRecord.
  The shape above is the agreed source; confirm in W01-B.
- **Shizza:** Workers receive `customer_id` (validated) and `conversation_id` as part of
  TaskDefinition.input_payload. Confirm this covers what your workers need to scope DB queries.
