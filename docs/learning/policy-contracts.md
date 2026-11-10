# Policy, consent and receipt contracts

## W01-A scope

This note explains the policy boundary reviewed for Arif's pricing and controlled-action
work. The current change is documentation and contract design; it does not implement a
quote service, approval endpoint or executor.

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

- Money crosses the contract as decimal strings and is calculated with `Decimal`, not
  binary floating point.
- Customer consent and administrator approval are separate append-only decisions.
- Replays use a unique idempotency key and return the existing execution receipt.
- An executor rechecks policy and authoritative data; an agent result cannot authorize a
  write.

An event-sourced history could derive current state by replaying every event, but the
versioned proposal plus append-only decisions are easier to inspect for this FYP scope.

## Verification

The isolated check for this documentation-only contribution is `python
scripts/check_repository.py` plus `git diff --check`. No runtime approval or quote test is
claimed because the B02 identity prerequisite and B03 services are not committed on the
base branch.
