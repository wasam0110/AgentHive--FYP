# Policy, consent and receipt contracts

## Scope and user flow

This note explains Arif's pricing and proposal-validation work. Quote calculation and
proposal revalidation are implemented as standalone services; no HTTP endpoint,
customer-consent handler, admin-approval handler or executor is wired yet.

## User flow

1. A worker proposes an action using authoritative catalog data.
2. The policy gate checks profile capability, currency, discount limits and expiry.
3. The customer confirms the exact proposal version.
4. An authorized administrator approves that same version.
5. A controlled executor rechecks current data and either writes once or returns a
   canonical receipt.

`proposal_version` protects the exact terms, while a profile/policy fingerprint identifies
the configuration used to create them. A configuration change therefore requires
revalidation and, when terms change, fresh consent and approval.

## Important contract choices

- `quote(db, profile, item_id, quantity, discount_pct, slot_id)` reads catalog and slot
  records through its database input and returns canonical terms without writing data.
  It calculates with `Decimal` and rounds totals to cents using `ROUND_HALF_UP`.
- `validate(db, proposal, profile, version)` returns no value and raises an explicit
  HTTP error for malformed, closed, stale, expired or changed terms. It rechecks current
  profile, catalog price and booking state. It does **not** authenticate a user or
  authorize an action; its future caller must do that separately.
- `redact(value)` returns a recursively filtered copy for traces, preserving safe IDs
  while hiding common credentials and email addresses.
- Customer consent and administrator approval are separate append-only decisions.
- The current schema permits one receipt per proposal; request-level idempotency is not
  modeled or implemented.
- Future execution must recheck policy and authoritative data; an agent result cannot
  authorize a write. Transactions, consent, admin approval, and receipt replay are not
  implemented in this standalone slice.

The catalog is read through the supplied database session rather than accepting a price
from a worker. An alternative is to store prices as integer minor units; Decimal strings
match the existing contract and are easy to inspect, so no conversion layer is needed.
The current validator uses a fake adapter in its unit tests; an event-sourced history
could model every decision, but it is unnecessary for these focused checks.

## Verification

```powershell
python -m pytest -q tests/unit/test_quote_service.py
python -m ruff check backend/services/quotes.py backend/services/approvals.py backend/services/redaction.py tests/unit/test_quote_service.py
```

The fake adapter covers different profile prices/currencies, policy denials, malformed
data, stale terms, expiry, price changes, booking conflicts and redaction. These tests do
not establish B02 identity integration or consent/approval/execution safety.
