# Arif FYP-I progress

**Scope:** Pricing, validation, consent, approvals, controlled execution, audit and deployment.
**Target:** 15 January 2027. One Tuesday session each week; unfinished work carries forward.
**Cadence:** One combined contribution session per Tuesday each week. The former A/B tasks are combined into the single weekly deliverable shown below.

[Weekly scopes and dependencies](docs/planning/WEEKLY_COMMIT_PLAN.md) | [Push checklist](docs/planning/PUSH_CHECKLIST.md)

Dates below are plans, not attendance or completion claims. Record one dated weekly entry for each actual session, with any unfinished work carried forward. Aim for one focused commit when ready.

| Week | Planned Tuesday | Deliverable | Status | Actual date | Evidence / PR / test |
|---|---|---|---|---|---|
| W01 | 2026-10-27 | Define profile-driven policy matrix and approval/consent requirements; Agree proposal/receipt contracts and safety examples | In progress | 2026-11-10 | W01-A policy/approval/receipt contract review completed on `arif/w01-policy-contracts` (`bec19b4`); repository and whitespace checks passed. W01-B and human/team review remain pending; no runtime behavior claimed. |
| W02 | 2026-11-03 | Implement Decimal quote service using configured catalog/currency/policy; Test price differences, invalid discounts and missing catalog values | Not started | — | — |
| W03 | 2026-11-10 | Implement proposal validation with fake data adapter; Test denied, stale and malformed proposals | Not started | — | — |
| W04 | 2026-11-17 | Add proposal/confirmation/approval data models and migrations; Verify approval is bound to exact proposal version | Not started | — | — |
| W05 | 2026-11-24 | Implement approve/reject service with authorized actor checks; Test missing consent, unauthorized approver and expired proposals | Not started | — | — |
| W06 | 2026-12-01 | Review policy documentation; light mids session; Prepare deployment environment inventory; light session | Not started | — | — |
| W07 | 2026-12-08 | Review safety test cases; light mids session; Draft Docker/health-check requirements without inventing services | Not started | — | — |
| W08 | 2026-12-15 | Implement transactional service request and booking executor; Test duplicate execution and competing booking requests | Not started | — | — |
| W09 | 2026-12-22 | Connect live data revalidation and workflow adapter; Verify changed prices/slots invalidate stale consent/approval | Not started | — | — |
| W10 | 2026-12-29 | Complete Compose with explicit profile selection and isolated demo setup; Run API/auth/worker smoke checks for Profiles A/B without core edits | Not started | — | — |
| W11 | 2027-01-05 | Test recovery at execution boundaries and inspect receipts; Freeze backend execution; record deployment and safety evidence | Not started | — | — |
| W12 | 2027-01-12 | Verify setup from clean checkout and documented commands; Rehearse approval failure demo; finalize deployment handoff | Not started | — | — |

## Work log

- **10 November 2026 - W01 combined session:** Reviewed the policy matrix, consent/approval/receipt contracts and proposal storage boundaries on `arif/w01-policy-contracts`. `python scripts/check_repository.py` and `git diff --check` passed for the documentation change. Proposal, decision, mutation and receipt services remain unimplemented; B02 identity and B03 integration prerequisites remain pending. Published commit `bec19b4bc57ba1798e18b147a6e794a8dbb2a685`; publication evidence commit `a4adbc9` was also pushed. No PR was created and human/team review remains pending.

**Planning:** On 30 October 2026, the former A/B schedule was combined into 12 Tuesday sessions. The archived schedule is retained for historical context and does not create additional current sessions or completion claims. [Previous schedule](docs/planning/archive/pre-tuesday-progress.md).

**Next:** Review W01 contracts and the dependencies for your first contribution.

For each session, add a short dated note: work/files changed, checks and results, mocked or live dependencies, learning/review, affected docs, and next step. After a push, add the real SHA and observed PR/CI status. Follow the push checklist for details.
