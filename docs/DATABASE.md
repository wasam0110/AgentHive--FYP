# Database guide

This document defines the storage responsibilities for the proposal and controlled
execution flow. It is a contract for the later models and migration; it does not claim
that those tables or executors are implemented in the current foundation.

| Record | Purpose | Required safety boundary |
|---|---|---|
| `proposals` | Store the exact action terms, `proposal_version`, profile/policy fingerprints and expiry | A changed price, slot, payload or expiry creates a new version |
| `decisions` | Append customer-consent and administrator-approval decisions | Each decision records the proposal ID, exact version, actor and decision time |
| `service_requests` / `bookings` | Store the controlled business mutation | Writes occur in one transaction after final permission, price, availability and expiry checks |
| `receipts` | Store the canonical result of an execution | A unique proposal/idempotency key returns the existing receipt on replay |

Amounts are represented as decimal strings at the contract boundary and calculated with
`Decimal`; binary floating-point values are not authoritative for money. Proposal records
retain the profile and policy versions used to produce them, so a later configuration
change triggers revalidation instead of silently changing historical terms.

The executor must not trust a decision merely because it exists. It rechecks ownership,
authorized role, exact proposal version, customer consent, administrator approval,
current price, eligibility, availability and expiry inside the transaction boundary.
Unique constraints on the proposal/idempotency key and bookable slot prevent duplicate
effects and competing bookings from both committing.

The current B01 foundation provides shared configuration and relational primitives only.
Proposal, decision, mutation and receipt models belong to the later Arif service batch and
must be added through the coordinated migration chain.
