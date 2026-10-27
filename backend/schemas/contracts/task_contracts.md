# Request / Task / Result Contracts

Version: 1.0 — draft W01-A (2026-10-26)
Owner: Wasam (orchestration, state contracts)
Consumers: Arif (ActionProposal, policy gate inputs), Shizza (WorkerResult, worker implementations),
           Asad (TaskStatus for UI display)

All amounts use Python Decimal, not float. All timestamps are UTC ISO-8601 strings.

---

## IntakeOutput — produced by the Intake agent (W05-A)

```python
class Intent:
    intent_type: str          # one of: "support_complaint", "catalog_enquiry",
                              #         "service_request", "resource_appointment",
                              #         "discount_request", "refund_cancellation",
                              #         "unclear"
    confidence: str           # "high" | "medium" | "low"  (diagnostic only, not authorization)
    entities: dict            # extracted entities specific to this intent type
    missing_fields: list[str] # fields needed before this intent can proceed

class IntakeOutput:
    conversation_id: str
    run_id: str
    raw_message: str          # original customer message — treat as untrusted
    language_detected: str    # e.g. "en", "ur", "roman-ur"
    intents: list[Intent]     # one or more; at least one always present
    clarification_needed: bool
    clarification_question: str | None  # set when clarification_needed is True
```

## TaskDefinition — produced by the Supervisor (W05-B)

```python
class TaskDefinition:
    task_id: str              # server-assigned UUID
    run_id: str
    conversation_id: str
    intent_type: str          # matches an Intent.intent_type from IntakeOutput
    assigned_worker: str      # one of: "support", "sales", "scheduling"
    dependencies: list[str]   # task_ids that must complete first
    input_payload: dict       # validated, typed input for the assigned worker
    created_at: str           # UTC ISO-8601
```

## Dependency rules (agreed W01-A)

| Task type | May run in parallel with | Must wait for |
|---|---|---|
| support_complaint | catalog_enquiry, catalog_quote | — |
| catalog_enquiry | support_complaint | — |
| catalog_quote | support_complaint | catalog_enquiry (if both present) |
| resource_appointment | support_complaint | catalog_quote (if service eligibility required) |
| discount_request | support_complaint | catalog_quote |

These rules are enforced in deterministic Supervisor code, not by an LLM.

---

## WorkerResult — returned by any domain worker (Shizza implements)

```python
class EvidenceRef:
    source_id: str            # chunk ID or DB record ID
    source_type: str          # "rag_chunk" | "db_record" | "status_record"
    excerpt: str | None       # brief verbatim excerpt (not fabricated)

class WorkerResult:
    task_id: str
    worker: str               # "support" | "sales" | "scheduling"
    status: str               # "completed" | "needs_clarification" | "escalate" | "failed"
    summary: str              # human-readable outcome (safe to show in UI trace)
    evidence: list[EvidenceRef]
    proposed_action: "ActionProposal | None"  # None for read-only outcomes
    clarification_question: str | None
    error_detail: str | None  # set only when status == "failed"; not shown to customer
```

---

## ActionProposal — the typed mutation intent (Arif validates, Wasam orchestrates)

```python
class ActionType(str, Enum):
    SERVICE_REQUEST   = "service_request"
    RESOURCE_BOOKING  = "resource_appointment"
    DISCOUNT          = "discount_request"
    TICKET            = "support_ticket"
    REFUND_CASE       = "refund_cancellation_case"

class ServiceRequestPayload:
    catalog_item_id: str
    quantity: int
    unit_price_decimal: str   # Decimal serialized as string to preserve precision
    discount_pct: int
    total_decimal: str
    currency: str
    quote_valid_until: str    # UTC ISO-8601

class ResourceBookingPayload:
    resource_id: str
    proposed_slot_start: str  # UTC ISO-8601
    proposed_slot_end: str    # UTC ISO-8601

class ActionProposal:
    proposal_id: str          # server-assigned UUID
    proposal_version: int     # increment on any change; used for consent/approval binding
    action_type: ActionType
    conversation_id: str
    run_id: str
    payload: ServiceRequestPayload | ResourceBookingPayload | dict
                              # typed per action_type; dict is a temporary placeholder only
    requires_customer_confirmation: bool
    requires_admin_approval: bool
    policy_version: str       # version of the policy used to generate this proposal
    profile_version: int      # schema_version from the active BusinessProfile
    created_at: str           # UTC ISO-8601
    expires_at: str           # UTC ISO-8601; derived from policy config
```

## Invariants on ActionProposal (enforced by Arif's policy gate)

- `proposal_version` must be incremented any time payload, price, slot, or expiry changes.
- Customer confirmation and admin approval must both reference the same `proposal_id` + `proposal_version`.
- A changed price or slot invalidates existing confirmation and approval — a new version is issued.
- Read-only intents (FAQ, catalog enquiry) produce no ActionProposal.
- `resource_booking` requires `resource_booking` to be in the active profile's capabilities.
  If not present, the Supervisor must return a denial before creating a TaskDefinition for it.

---

## TaskStatus — persisted status for each task in a run (Asad reads for UI)

```python
class TaskStatus(str, Enum):
    QUEUED              = "queued"
    RUNNING             = "running"
    COMPLETED           = "completed"
    NEEDS_CLARIFICATION = "needs_clarification"
    FAILED              = "failed"
    CANCELLED           = "cancelled"
    WAITING_CUSTOMER    = "waiting_customer"
    WAITING_ADMIN       = "waiting_admin"

class TaskStatusRecord:
    task_id: str
    run_id: str
    conversation_id: str
    intent_type: str
    assigned_worker: str
    status: TaskStatus
    proposal_id: str | None   # set when a proposal exists
    updated_at: str           # UTC ISO-8601
```

---

## Sample payloads (for use as shared test fixtures)

### Sample IntakeOutput — support + service request
```json
{
  "conversation_id": "conv-001",
  "run_id": "run-001",
  "raw_message": "I have a complaint about my last service and I also want to get a quote for a new one",
  "language_detected": "en",
  "intents": [
    {
      "intent_type": "support_complaint",
      "confidence": "high",
      "entities": {"complaint_topic": "last service"},
      "missing_fields": []
    },
    {
      "intent_type": "service_request",
      "confidence": "high",
      "entities": {"catalog_item_hint": "new service"},
      "missing_fields": ["catalog_item_id"]
    }
  ],
  "clarification_needed": true,
  "clarification_question": "Which service would you like a quote for?"
}
```

### Sample WorkerResult — support worker (no proposal)
```json
{
  "task_id": "task-001",
  "worker": "support",
  "status": "completed",
  "summary": "Service outage reported; known issue referenced in status record SR-2026-11.",
  "evidence": [
    {"source_id": "sr-2026-11", "source_type": "status_record", "excerpt": "Known outage, resolution estimate: 24h"}
  ],
  "proposed_action": null,
  "clarification_question": null,
  "error_detail": null
}
```

### Sample ActionProposal — service request (partial; amounts are illustrative only)
```json
{
  "proposal_id": "prop-001",
  "proposal_version": 1,
  "action_type": "service_request",
  "conversation_id": "conv-001",
  "run_id": "run-001",
  "payload": {
    "catalog_item_id": "item-abc",
    "quantity": 1,
    "unit_price_decimal": "5000.00",
    "discount_pct": 0,
    "total_decimal": "5000.00",
    "currency": "PKR",
    "quote_valid_until": "2026-10-26T12:30:00Z"
  },
  "requires_customer_confirmation": true,
  "requires_admin_approval": true,
  "policy_version": "v1",
  "profile_version": 1,
  "created_at": "2026-10-26T12:00:00Z",
  "expires_at": "2026-10-26T12:30:00Z"
}
```

**Note:** Prices in sample payloads are illustrative placeholders only.
Real prices must come from the authoritative catalog database (Arif's quote service).
Never use sample payload amounts as defaults in production code.

---

## Mocked vs live integrations at W01-A

| Integration | Status | Fake adapter |
|---|---|---|
| Arif's quote service (produces unit_price_decimal, total_decimal) | Mocked — not yet built | Sample payload above shows the expected shape; real prices come from Arif's W02-A |
| Shizza's worker implementations | Mocked — not yet built | WorkerResult sample above is the agreed return shape |
| Asad's UI consumption of TaskStatusRecord | Not yet built | Field names above are the agreed contract; Asad confirms in W01-B |
