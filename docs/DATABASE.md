# Database guide

This document describes storage responsibilities for the proposal and controlled
execution flow. B01 already defines relational records for proposals, decisions, requests,
bookings and receipts; those models do not themselves implement an authorized executor.

| Record | Purpose | Required safety boundary |
|---|---|---|
| `proposals` | Store the exact action terms, `proposal_version`, profile/policy fingerprints and expiry | A changed price, slot, payload or expiry creates a new version |
| `decisions` | Append customer-consent and administrator-approval decisions | Each decision records the proposal ID, exact version, actor and decision time |
| `service_requests` / `bookings` | Store the controlled business mutation | Writes occur in one transaction after final permission, price, availability and expiry checks |
| `receipts` | Store the canonical result of an execution | The current schema permits one receipt per proposal; request-level idempotency is not yet modeled |

Amounts are represented as decimal strings at the contract boundary and calculated with
`Decimal`; binary floating-point values are not authoritative for money. Proposal records
retain the profile and policy versions used to produce them, so a later configuration
change triggers revalidation instead of silently changing historical terms.

The executor must not trust a decision merely because it exists. It rechecks ownership,
authorized role, exact proposal version, customer consent, administrator approval,
current price, eligibility, availability and expiry inside the transaction boundary.
Unique proposal constraints prevent duplicate service requests, and a unique slot
constraint prevents competing bookings from both committing. A separate request-level
idempotency key is not yet represented in the schema.

The current B01 schema includes these record shapes, but quote calculation and proposal
revalidation are standalone service logic only. Consent, administrator decisions,
transactional execution and receipt replay still require the later dependency-gated
integration work.
