# Wasam FYP-I progress

**Scope:** Core backend, authentication foundation, conversations, orchestration and RAG.
**Target:** 15 January 2027. One Tuesday session each week; unfinished work carries forward.
**Cadence:** One combined contribution session per Tuesday each week. The former A/B tasks are combined into the single weekly deliverable shown below.

[Weekly scopes and dependencies](docs/planning/WEEKLY_COMMIT_PLAN.md) | [Push checklist](docs/planning/PUSH_CHECKLIST.md)

Dates below are plans, not attendance or completion claims. Record one dated weekly entry for each actual session, with any unfinished work carried forward. Aim for one focused commit when ready.

| Week | Planned Tuesday | Deliverable | Status | Actual date | Evidence / PR / test |
|---|---|---|---|---|---|
| W01 | 2026-10-27 | Define request/task/result schemas plus business-profile and capability contracts; Review shared sample payloads and first end-to-end scenario | Verified on branch (review pending) | 2026-11-17 | B01 foundation contracts and validation rechecked with `tests/unit/test_foundation.py`; full W01-W03 verification passed 92 tests and Ruff. Teammate/human contract review remains a separate pending review item, not an implementation failure. |
| W02 | 2026-11-03 | Create FastAPI skeleton and typed profile validation with unknown-capability rejection; Add backend lint/tests and authenticated demo identity foundation | Verified on branch (review pending) | 2026-11-17 | B01/B02 checks rechecked: foundation, identity and fixture-contract tests passed; B02 provides opaque hashed sessions, Argon2 verification, CSRF/origin checks, role checks and business/customer scoping. Teammate/human review remains pending. |
| W03 | 2026-11-10 | Implement conversation/message persistence; Verify history reload and denied cross-customer access | Verified and pushed (review pending) | 2026-11-17 | B04/B05/B06 checks passed, including history/ownership, auth/CSRF, queue/idempotency, approval/receipt, profile isolation, provider and restart/recovery checks. Full W01-W03 verification passed 92 tests and Ruff. |
| W04 | 2026-11-17 | Build reviewed-document chunking and ingestion; Verify profile-scoped retrieval, source IDs and no-evidence behavior | Verified on branch (push pending) | 2026-11-17 | Added deterministic chunking and optional reviewed-document front matter with language, ISO review date, audience and review status metadata. Verified profile-scoped collections, stable source IDs and unrelated-query no-evidence behavior: focused retrieval/profile tests passed (11 tests); full backend suite passed 93 tests; Ruff passed. |
| W05 | 2026-11-24 | Implement intake with structured intent output; Run supervisor with fake workers and dependency-aware routing | Not started | — | — |
| W06 | 2026-12-01 | Review state schemas and Chapter 1 draft; light mids session; Document worker/RAG interfaces and test one invalid payload; light session | Not started | — | — |
| W07 | 2026-12-08 | Review RAG evidence and failure cases; light mids session; Update architecture notes and fix a small test; light session | Not started | — | — |
| W08 | 2026-12-15 | Connect domain workers through adapters; Verify support-plus-quote routing and independent task overlap | Not started | — | — |
| W09 | 2026-12-22 | Persist customer/admin waiting states; Connect approval result and resume without losing completed tasks | Not started | — | — |
| W10 | 2026-12-29 | Connect authorized execution receipts to final response; Run real backend journey and verify restart/duplicate-request behavior | Not started | — | — |
| W11 | 2027-01-05 | Support frontend integration and fix contract defects; Freeze backend scope; verify same core with Profiles A/B and disabled booking | Not started | — | — |
| W12 | 2027-01-12 | Run fresh-setup integration and finalize Chapter 1 material; Rehearse explanation of graph/RAG; fix only release-blocking defects | Not started | — | — |

## Work log

- **27 October 2026 ? W01-A:** Defined profile, capability, task and conversation contracts with sample payloads. Design and Git hygiene checks only; integrations were mocked. Teammate contract review remains pending. [Original session record](docs/planning/archive/progress-evidence-2026-10-31.md).
- **30 October 2026 ? Local prototype setup:** Imported the prototype, configured the environment and prepared dependency-based commit batches. Checks passed: 49 backend tests, lint, frontend types/build, SQLite migration/seed and two browser journeys. Demo agents and mocked provider calls were used; PostgreSQL, Docker and real providers remain unverified. [Test evidence](docs/VERIFICATION.md).
- **30 October 2026 ? Planning:** Combined the schedule into 12 Tuesdays per member; checked all 48 weekly entries against the Gantt plan. No future session was completed.
- **31 October 2026 ? Workflow cleanup:** Prepared four private Tuesday prompts, retired the old member instructions and updated onboarding. Checked ignore rules, weekly rows and repository hygiene. Shortened these progress files; earlier evidence remains in the archive. No application tests were rerun for these documentation edits.

- **31 October 2026 - Repository cleanup:** Removed the duplicate HTML handover and unused formatter; simplified documentation and centralized the origin record. Frontend lint/types/build, dependency consistency and schedule checks passed. [Details](docs/VERIFICATION.md).

- **31 October 2026 - Team package preparation:** Selected the non-ignored project files and checked private-file exclusions and local credential values. Prepared separate private prompt copies and a reference-package setup guide. No application changes or publication.

- **31 October 2026 - Visual refinement:** Requested a softer 60/30/10 palette and clearer typography. Updated shared frontend styles and self-hosted fonts; adjusted inspector sizing for mobile. Frontend lint/types/build passed. Design rationale: [visual theme](docs/learning/visual-theme.md). Asad review and independent batch verification remain pending.

- **4 November 2026 - W02 combined session:** Prepared the ISP pitch demo (Alpha Max branding, Karachi reference offers, isolated fixtures and read-only enquiry support), then added the customer-aware demo with account-linked context, area incidents, durable ticket responses, scoped reads and connection isolation tests. The backend suite passed 59 tests, including the earlier 54-test ISP checkpoint; desktop/mobile offer and enquiry checks passed. Also consolidated onboarding, archived the original ZIP manifest and prepared the private teammate handoff guide. Client approval, human code review, teammate completion and publication remain pending; no additional weekly session is inferred. [Evidence](docs/VERIFICATION.md), [implementation guide](docs/ISP_PITCH.md), and [customer-context guide](docs/learning/customer-service-context.md).
- **16 November 2026 - W02 B02 follow-up:** Reviewed the identity and authorized-data-access batch on the integrated B01 base. The focused identity smoke passed; no HTTP integration, expiry/logout, full CSRF, or cross-customer safety claim is made until B06. The imported prototype remains separate from this exact B02 scope.
- **16 November 2026 - W03 dependency review:** Reviewed the conversation persistence/API candidate against the newly merged B03/B05 base. The focused integration attempt failed during test collection because `backend.services.service_context` belongs to the still-uncommitted B04/prototype scope. The B06 candidate files remain preserved in the `pre-B06 prototype worktree 2026-11-16` stash; no W03 source commit was created.
- **16 November 2026 - W03 B04 prerequisite:** Restored only the planned B04 retrieval/provider files from the preserved prototype stash. The focused retrieval/intake test passed (`1 passed`) and Ruff passed for the exact B04 source/test paths. This verifies the prerequisite only; conversation persistence, history reload and cross-customer denial remain B06 work.
- **16 November 2026 - W03 B05 prerequisite:** Restored the planned B05 seed/read workflow after B04 was committed. The profile-B repeatability and booking-denial test passed (`1 passed`) and Ruff passed for the exact B05 source/test paths. B06 is now the remaining W03 integration batch; no conversation/API completion is claimed yet.
- **16 November 2026 - W03 B06 integration:** Restored the exact persisted conversation/API and safety batch after B04 and B05 were committed. Integration exposed and fixed two coupled contract gaps: the B06 worker required the complete consent/approval/refresh implementation, and the ISP profile needed explicit `isp-pitch` fixture registration. The quote error wording was aligned with the API test contract. The relevant B06 suite passed (`49 passed`) and Ruff passed; provider calls remained mocked/demo-only and no paid model call was made.
- **17 November 2026 - W01-W03 completion verification:** Re-ran the foundation, identity, fixture-contract, quote-validation, retrieval, seed/read, conversation, authentication, provider, workflow, service-context and approval suites together. Result: `92 passed`; Ruff passed across the affected backend, scripts and tests. The approval validator now rejects closed proposals and malformed versions, payloads and expiry values while preserving the B06 consent/approval flow.
- **17 November 2026 - W04 reviewed-document ingestion:** Added deterministic fixed-offset chunking and optional document front matter. Each chunk now records source ID, source hash/version, language, review date, audience and review status; unannotated legacy demo documents are explicitly marked `unreviewed`. Verified separate profile namespaces, stable source IDs and no-evidence behavior with 11 focused tests. Full backend regression passed (`93 passed`) and Ruff passed. No hosted or paid model call was used.

**Next:** Review and merge the W04 branch, then continue with the next planned Wasam task. Human review remains pending.

[Project background](docs/PROJECT_ORIGIN.md).

For each session, add a short dated note: work/files changed, checks and results, mocked or live dependencies, learning/review, affected docs, and next step. After a push, add the real SHA and observed PR/CI status. Follow the push checklist for details.

## W02 push evidence - 4 November 2026

- Published B01 on branch wasam/w02-foundation; SHA 081b1bebce1c5d9852d1350ec47e4a47b3028d59. Remote branch SHA verified after push; confirmation recorded at 2026-11-04T22:48:07+05:00 (Asia/Karachi).
- Based on current main 433a3c1c1a0559ce14957cf55302b1b52eb46541. Exact scope: 24 B01 files plus dated additions to Wasam-progress.md and Chapter 4; no other local progress rewrites or imported modules included.
- Independent candidate checks passed: Ruff, eight foundation tests, fresh SQLite migration and metadata comparison; staged hygiene and whitespace passed. Snapshot: C:/Users/wasam/AppData/Local/AgentHive-imports/20261104-w02-candidate-check/publication-evidence.json.
- No PR created or merge performed. GitHub Actions API initially returned no push workflow run for this SHA; remote CI not yet observed. Human review remains pending. W02 is in progress; B02 identity is the next prerequisite task after the foundation reaches the agreed integration base.
- This post-push entry remains local for the next reviewed contribution; no evidence-only follow-up commit is created.

## Documentation cleanup - 4 November 2026

Moved the shared commit plan to docs/commits/COMMIT_PLAN.md and removed the obsolete FIRST_COMMIT.md guide. Updated active plan references and the staging manifest. Documentation/manifest checks and whitespace validation passed; application behavior is unchanged, so runtime tests were not rerun.

- **4 November 2026 - Cleanup push:** Published 80e1c664858d3671946967037e072d9f4f9a1736 on wasam/docs-cleanup; remote SHA confirmed at 2026-11-04T22:54:29+05:00. Plan moved to docs/commits/COMMIT_PLAN.md, obsolete FIRST_COMMIT.md removed. Link/manifest/hygiene/whitespace checks passed. New PR/merge and remote CI not yet observed. Post-push evidence retained locally for the next normal contribution.
