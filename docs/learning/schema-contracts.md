# Learning note: Schema contracts — W01-A

## What was built

Five typed contract documents under `backend/schemas/contracts/` defining the shapes that
flow through the Agent Hive orchestration pipeline. These are design documents, not running
Pydantic models — those come in W02-A.

## User flow these contracts govern

1. Customer sends a message → Intake produces **IntakeOutput** (intents + entities).
2. Supervisor reads IntakeOutput → creates **TaskDefinition** per intent, applying **dependency rules**.
3. Workers execute tasks → return **WorkerResult** (evidence + optional **ActionProposal**).
4. Policy gate validates ActionProposal → sets `requires_customer_confirmation` and `requires_admin_approval`.
5. Customer confirms; admin approves → Executor runs → receipt stored.
6. All of the above is anchored to a **ConversationRecord** and **RunRecord**.

## Important functions / design choices

### Why Decimal strings for amounts (not float)?
Python `float` uses binary floating point: `0.1 + 0.2` is `0.30000000000000004`, not `0.3`.
For money (PKR quotes, etc.), rounding errors like this are unacceptable.
Python's `Decimal` type does exact decimal arithmetic. But JSON has no Decimal type, so we
serialize it as a string `"5000.00"` — the consumer reads it with `Decimal("5000.00")`.
Alternative: store as an integer in the smallest currency unit (e.g. paisa). Not chosen
because the PRD requires explicit decimal display in quotes; paisa conversion would be an
extra step prone to off-by-one errors at display time.

### Why are capability IDs code-registered, not profile-defined?
If a profile could define arbitrary capability IDs, an attacker or misconfiguration could
name a capability that the code doesn't know about, leading to either silent no-ops or
crashes. By keeping a static `REGISTERED_CAPABILITIES` set in the loader, adding a new
capability requires a code change + tests — not just a JSON edit. This is documented in
`BUSINESS_CONFIGURATION.md`.

### Why is customer_id never trusted from a message body?
The PRD (Section 4) says: "Customer IDs and future tenant IDs supplied in a message are
untrusted." A customer could send `{"customer_id": "admin-001"}` in their message.
The backend always takes customer_id from the authenticated session, not from message content.

### proposal_version increment rule
Every change to payload, price, slot, or expiry must increment `proposal_version`.
Consent and approval both record which version they apply to. If the version on an approval
doesn't match the current proposal, the approval is rejected. This prevents approving a
changed proposal without re-review — a core safety requirement from the PRD.

## Key alternative considered

**Flat event log instead of typed proposal versions:** record every change as an append-only
event, derive current state by replaying. Chosen approach (versioned record) is simpler to
query and reason about at FYP scale, and the PRD already specifies proposal_id + version + hash.

## How to verify (once W02-A is built)

```powershell
# From repo root, after W02-A:
python -m pytest tests/unit/test_business_profile_loader.py -v
python -m pytest tests/unit/test_task_contracts.py -v
```

At W01-A: no tests exist yet. Verify by reading the contracts with teammates in W01-B
and confirming no open points remain unresolved.
