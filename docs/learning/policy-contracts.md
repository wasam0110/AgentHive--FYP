# Policy, consent and receipt contracts

## Scope and user flow

This note explains Arif's pricing and proposal-validation work. The 12 November quote
and validation candidate was standalone. The committed synthetic application was verified
on 18 November and rechecked on 24 November with authenticated consent/approval routes,
version-bound decisions, sandbox execution and receipt replay. This does not establish a
production business integration.

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
  authorize an action; the integrated confirmation/approval handlers perform those
  separate checks before proceeding.
- `redact(value)` returns a recursively filtered copy for traces, preserving safe IDs
  while hiding common credentials and email addresses.
- Customer consent and administrator approval are separate append-only decisions. The
  integrated tests verify that admin approval cannot precede consent and must match the
  current proposal version. Refresh increments the version, making earlier consent
  unusable; the refreshed proposal requires a new customer decision.
- The current schema permits one receipt per proposal; request-level idempotency is not
  modeled as a separate receipt field. Repeated approval returns the proposal's canonical
  receipt; message submission has its own idempotency key.
- The sandbox executor rechecks policy and authoritative data and stores the simulated
  mutation and receipt in its transaction. It does not charge real payments.

The catalog is read through the supplied database session rather than accepting a price
from a worker. An alternative is to store prices as integer minor units; Decimal strings
match the existing contract and are easy to inspect, so no conversion layer is needed.
Focused quote tests use a fake adapter for deterministic edge cases, while the
integration suite exercises the synthetic SQLite/API flow. PostgreSQL remains unverified.

## Verification

```powershell
python -m pytest -q tests/unit/test_quote_service.py
python -m ruff check backend/services/quotes.py backend/services/approvals.py backend/services/redaction.py tests/unit/test_quote_service.py
```

The fake adapter covers different profile prices/currencies, policy denials, malformed
data, stale terms, expiry, price changes, booking conflicts and redaction. The integration
suite additionally covers authentication, consent, approval, execution and receipt replay
against synthetic SQLite fixtures; it does not establish PostgreSQL or production safety.
