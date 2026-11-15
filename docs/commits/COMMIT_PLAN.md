# Dependency-aware import plan

Prepared at Wasam's request on **2026-10-30 (Asia/Karachi)**. The complete prototype is imported locally and remains uncommitted. No automatic staging, commit or push is authorized. This plan supersedes the ZIP's one-baseline recommendation and its cross-dependent owner staging commands.

See [Project origin](../PROJECT_ORIGIN.md) for the original generation and import record. Import, automated review/testing and any fixes have their actual dates recorded separately. Human member review, understanding, future sessions and supervisor approval remain pending. Do not change Git authors or backdate commits to simulate independent authorship.

Base: `1c35bb5e4c2ef4ab59d7bf5580e42a8b5d6a8c9c`. Preserve the historical W01-A and decision-log corrections. The obsolete root FIRST_COMMIT.md guide has been retired. Retired member instructions have been replaced by privately shared, ignored Tuesday prompts.

**Commit B01 first.** The shared schema and single migration chain belong to all four owners; Wasam coordinates them. B02 and B04 can follow independently after B01. B03 needs B02. B05a is a separately testable fixture-contract slice that needs only B01; the full B05 seed/read workflow needs B02, B04, and B05a. B06 joins those modules. B07 then connects the UI; B08 adds complete CI/deployment; B09 reconciles final documentation.

Exact paths are listed below and in `docs/commits/staging-manifests.json`; no directory globs are staging authorization. Documentation-update lists are handoff requirements: add only actual dated evidence and approved hunks when that work happens. Later additions to tests or docs must be added explicitly to the batch manifest and retested.

**Verification rule:** export the then-current committed HEAD and overlay only the proposed batch. Dependencies must already be committed in that HEAD. Never copy other pending batches, the working .env, installed source modules, or the integration conftest into that snapshot. Install dependencies from its lockfiles, clear PYTHONPATH, use disposable data, and save base SHA, source hashes, commands and results. Only that result can establish independent verification. The full imported tree passing proves integration only. B02-B05 and B06-B09 remain pending independent verification; B05a's candidate result is recorded below. B01 uses `scripts/verify_batch.py`; it refuses later batches rather than hiding missing prerequisites.

## B01 ? Shared validated configuration and SQL foundation

Owner: Wasam coordinates; all four review shared contracts. Dependencies: existing committed project only.

Exact files:

- `.gitignore`
- `docs/commits/COMMIT_PLAN.md`
- `alembic.ini`
- `backend/__init__.py`
- `backend/config.py`
- `backend/db/__init__.py`
- `backend/db/connection.py`
- `backend/db/migrations/env.py`
- `backend/db/migrations/script.py.mako`
- `backend/db/migrations/versions/1e58c02f5ad2_initial_schema.py`
- `backend/db/models.py`
- `backend/schemas/__init__.py`
- `backend/schemas/api.py`
- `docs/commits/staging-manifests.json`
- `docs/commits/verification.md`
- `docs/learning/shared-foundation.md`
- `pyproject.toml`
- `requirements.txt`
- `scripts/__init__.py`
- `scripts/check_repository.py`
- `scripts/verify_batch.py`
- `tests/unit/test_foundation.py`
- `docs/PROJECT_ORIGIN.md`
- `backend/db/migrations/versions/20261104_service_context.py`

Understand: Profile validation/fingerprints; typed schemas; session factories; foreign keys and uniqueness; one migration chain. Models declare storage, not authorized executors.

Checks: python scripts/verify_batch.py B01 <new external directory>; inspect batch-evidence.json; python scripts/check_repository.py; git diff --check

Update after actual work: Wasam-progress.md (new dated evidence hunk only); docs/learning/shared-foundation.md; docs/commits/verification.md.

Status: see docs/commits/verification.md; future work is not complete.

## B02 ? Identity and authorized data access

Owner: Wasam. Dependencies: B01.

Exact files:

- `backend/api/__init__.py`
- `backend/api/auth.py`
- `backend/services/__init__.py`
- `backend/services/data.py`
- `backend/services/security.py`
- `tests/unit/test_identity.py`

Understand: Opaque sessions, Argon2, CSRF/origin and role checks, business/customer scoping.

Checks: Direct identity smoke: pytest -q tests/unit/test_identity.py. Covers password rejection, hashed token persistence and admin-role denial. Full expiry/logout/CSRF/ownership safety tests run at B06.

Update after actual work: Wasam-progress.md; docs/API.md; docs/learning/FUNCTION_GUIDE.md; docs/report/04-planning-and-requirements.md.

Status: see docs/commits/verification.md; future work is not complete.

## B03 ? Deterministic quotes and controlled decisions

Owner: Arif. Dependencies: B01, B02.

Exact files:

- `backend/services/approvals.py`
- `backend/services/quotes.py`
- `backend/services/redaction.py`
- `tests/unit/test_quote_service.py`

Understand: Decimal prices, exact-version consent, admin authority, expiry, transaction rollback, replay receipts, redaction.

Checks: Direct price/redaction smoke: pytest -q tests/unit/test_quote_service.py. Full consent, expiry, stale approval, duplicate and concurrent execution safety tests run at B06; do not expose these services through HTTP before B06.

Update after actual work: Arif-progress.md; docs/DATABASE.md; docs/API.md; docs/learning/FUNCTION_GUIDE.md; docs/learning/policy-contracts.md; docs/commits/verification.md; docs/report/04-planning-and-requirements.md.

Status: see docs/commits/verification.md; future work is not complete.

## B04 ? Retrieval and explicit demo/provider adapter

Owner: Wasam; Shizza reviews knowledge fixtures. Dependencies: B01.

Exact files:

- `backend/agents/__init__.py`
- `backend/agents/provider.py`
- `backend/prompts/intake.txt`
- `backend/prompts/support.txt`
- `backend/rag/__init__.py`
- `backend/rag/knowledge/demo-a/appointments.md`
- `backend/rag/knowledge/demo-a/approval.md`
- `backend/rag/knowledge/demo-a/cancellation.md`
- `backend/rag/knowledge/demo-a/capabilities.md`
- `backend/rag/knowledge/demo-a/privacy.md`
- `backend/rag/knowledge/demo-a/quotes.md`
- `backend/rag/knowledge/demo-a/recovery.md`
- `backend/rag/knowledge/demo-a/support.md`
- `backend/rag/knowledge/demo-b/appointments.md`
- `backend/rag/knowledge/demo-b/approval.md`
- `backend/rag/knowledge/demo-b/cancellation.md`
- `backend/rag/knowledge/demo-b/capabilities.md`
- `backend/rag/knowledge/demo-b/privacy.md`
- `backend/rag/knowledge/demo-b/quotes.md`
- `backend/rag/knowledge/demo-b/recovery.md`
- `backend/rag/knowledge/demo-b/support.md`
- `backend/rag/retriever.py`
- `tests/unit/test_retrieval_service.py`

Understand: Lexical versus semantic retrieval, source hashes, no-evidence handling, mocked hosted HTTP and bounded retries.

Checks: Direct retrieval/intake smoke: pytest -q tests/unit/test_retrieval_service.py. Full mocked hosted-provider contract tests run at B06. No paid calls.

Update after actual work: Wasam-progress.md; docs/ARCHITECTURE.md; docs/learning/FUNCTION_GUIDE.md; docs/report/04-planning-and-requirements.md.

Status: see docs/commits/verification.md; future work is not complete.

## B05a ? Profile-scoped synthetic fixture contract

Owner: Shizza. Dependencies: B01.

This independently testable W02 slice validates the registered demo A/B seed-fixture data and profile references. It does not persist rows, implement read adapters, or complete B05; those parts remain gated on B02 and B04.

Exact files:

- `docs/BUSINESS_CONFIGURATION.md`
- `docs/commits/COMMIT_PLAN.md`
- `docs/commits/staging-manifests.json`
- `docs/commits/verification.md`
- `docs/VERIFICATION.md`
- `examples/seed-fixtures/demo-a.json`
- `examples/seed-fixtures/demo-b.json`
- `scripts/seed_fixtures.py`
- `shizza-progress.md`
- `tests/unit/test_seed_fixtures.py`

Understand: A code-owned allowlist selects fixture data; typed validation rejects malformed records and mismatched profile references before database writes. The slice has no database or retrieval side effects.

Checks: Export committed HEAD and overlay only these exact files; from the snapshot root run `python -m pytest -q tests/unit/test_seed_fixtures.py` and `ruff check scripts/seed_fixtures.py tests/unit/test_seed_fixtures.py`. In the working checkout, run `git diff --check` for tracked edits and `git diff --no-index --check` against an empty file for each new path. These checks do not verify database seeding, read tools, or workflow integration.

Update after actual work: shizza-progress.md; docs/BUSINESS_CONFIGURATION.md; docs/VERIFICATION.md; docs/commits/verification.md.

Status: see docs/commits/verification.md; this slice does not complete B05.

## B05 ? Synthetic seed, reference tools and read workflow

Owner: Shizza. Dependencies: B01, B02, B04, B05a.

Exact files:

- `backend/agents/workflow.py`
- `backend/tools/__init__.py`
- `backend/tools/reference.py`
- `scripts/seed.py`
- `tests/unit/test_seed_workflow.py`
- `backend/services/reference_offers.py`
- `examples/business-profiles/profile-isp.json`
- `examples/reference-offers/stormfiber-karachi.json`
- `examples/seed-fixtures/isp-pitch.json`
- `backend/rag/knowledge/isp-pitch/coverage.md`
- `backend/rag/knowledge/isp-pitch/ref-01.md`
- `backend/rag/knowledge/isp-pitch/ref-02.md`
- `backend/rag/knowledge/isp-pitch/ref-03.md`
- `backend/rag/knowledge/isp-pitch/ref-04.md`
- `backend/rag/knowledge/isp-pitch/ref-05.md`
- `backend/rag/knowledge/isp-pitch/ref-06.md`
- `backend/rag/knowledge/isp-pitch/ref-07.md`
- `backend/rag/knowledge/isp-pitch/ref-08.md`
- `backend/rag/knowledge/isp-pitch/ref-09.md`
- `backend/rag/knowledge/isp-pitch/ref-10.md`
- `backend/rag/knowledge/isp-pitch/ref-11.md`
- `backend/rag/knowledge/isp-pitch/ref-12.md`
- `backend/rag/knowledge/isp-pitch/ref-13.md`
- `backend/rag/knowledge/isp-pitch/ref-14.md`
- `backend/rag/knowledge/isp-pitch/ref-15.md`
- `backend/rag/knowledge/isp-pitch/ref-16.md`
- `backend/rag/knowledge/isp-pitch/ref-17.md`
- `backend/rag/knowledge/isp-pitch/ref-18.md`
- `backend/rag/knowledge/isp-pitch/ref-19.md`
- `backend/rag/knowledge/isp-pitch/ref-20.md`
- `backend/rag/knowledge/isp-pitch/ref-21.md`
- `backend/rag/knowledge/isp-pitch/ref-22.md`
- `backend/rag/knowledge/isp-pitch/ref-23.md`
- `backend/rag/knowledge/isp-pitch/ref-24.md`
- `backend/rag/knowledge/isp-pitch/ref-25.md`
- `backend/rag/knowledge/isp-pitch/ref-26.md`
- `backend/rag/knowledge/isp-pitch/ref-27.md`
- `backend/rag/knowledge/isp-pitch/ref-28.md`
- `backend/rag/knowledge/isp-pitch/ref-29.md`
- `backend/rag/knowledge/isp-pitch/ref-30.md`
- `backend/rag/knowledge/isp-pitch/ref-31.md`
- `backend/rag/knowledge/isp-pitch/ref-32.md`
- `backend/rag/knowledge/isp-pitch/ref-33.md`
- `backend/rag/knowledge/isp-pitch/ref-34.md`
- `backend/rag/knowledge/isp-pitch/ref-35.md`
- `backend/rag/knowledge/isp-pitch/ref-36.md`
- `backend/rag/knowledge/isp-pitch/ref-37.md`
- `backend/rag/knowledge/isp-pitch/ref-38.md`
- `backend/rag/knowledge/isp-pitch/ref-39.md`
- `backend/rag/knowledge/isp-pitch/ref-40.md`
- `backend/rag/knowledge/isp-pitch/ref-41.md`
- `backend/rag/knowledge/isp-pitch/ref-42.md`
- `backend/rag/knowledge/isp-pitch/ref-43.md`
- `backend/rag/knowledge/isp-pitch/ref-44.md`
- `backend/rag/knowledge/isp-pitch/ref-45.md`
- `backend/rag/knowledge/isp-pitch/ref-46.md`
- `backend/rag/knowledge/isp-pitch/ref-47.md`
- `backend/rag/knowledge/isp-pitch/support.md`
- `backend/services/service_context.py`

Understand: Seed preserves passwords/records, A/B isolated data, read tools never authorize writes, independent support/sales and dependent scheduling. Existing profile JSON files are already committed and unchanged.

Checks: Direct seed/read-workflow smoke: pytest -q tests/unit/test_seed_workflow.py; fresh isolated migrations/seeds for A/B. Full integration/partial-failure coverage runs at B06.

Update after actual work: shizza-progress.md; docs/BUSINESS_CONFIGURATION.md; docs/ARCHITECTURE.md; docs/learning/FUNCTION_GUIDE.md; docs/report/04-planning-and-requirements.md.

Status: see docs/commits/verification.md; future work is not complete.

## B06 ? Persisted end-to-end API and safety integration

Owner: Wasam integration lead; Arif and Asad review operations.py. Dependencies: B01, B02, B03, B04, B05.

Exact files:

- `backend/api/conversations.py`
- `backend/api/operations.py`
- `backend/main.py`
- `backend/services/jobs.py`
- `tests/conftest.py`
- `tests/test_approvals.py`
- `tests/test_auth.py`
- `tests/test_profiles_rag.py`
- `tests/test_provider.py`
- `tests/test_workflow.py`
- `tests/test_reference_offers.py`
- `tests/test_service_context.py`

Understand: SQL leases, idempotent enqueue/reclaim, REST recovery, consent/execution and overview routes. operations.py mixes read APIs with approval routes, so it must land here jointly, before the UI.

Checks: ruff check backend scripts tests; pytest -q; fresh migration/check/seed; health and restart. Test only committed prerequisites plus this batch; full imported-tree results are integration evidence only.

Update after actual work: Wasam-progress.md; Arif-progress.md (only actual review); Asad-progress.md (only actual review); docs/API.md; docs/ARCHITECTURE.md; docs/VERIFICATION.md; docs/report/04-planning-and-requirements.md.

Status: see docs/commits/verification.md; future work is not complete.

## B07 ? Connected operations console and browser journey

Owner: Asad. Dependencies: B06.

Exact files:

- `frontend/e2e/workspace.spec.ts`
- `frontend/eslint.config.mjs`
- `frontend/next-env.d.ts`
- `frontend/next.config.ts`
- `frontend/package-lock.json`
- `frontend/package.json`
- `frontend/playwright.config.ts`
- `frontend/src/app/globals.css`
- `frontend/src/app/icon.svg`
- `frontend/src/app/layout.tsx`
- `frontend/src/app/page.tsx`
- `frontend/src/components/approvals.tsx`
- `frontend/src/components/conversations.tsx`
- `frontend/src/components/inspector.tsx`
- `frontend/src/components/login.tsx`
- `frontend/src/components/overview.tsx`
- `frontend/src/components/proposal.tsx`
- `frontend/src/components/resources.tsx`
- `frontend/src/components/ui.tsx`
- `frontend/src/lib/api.ts`
- `frontend/src/lib/types.ts`
- `frontend/src/styles/base.css`
- `frontend/src/styles/conversations.css`
- `frontend/src/styles/login.css`
- `frontend/src/styles/overview.css`
- `frontend/src/styles/resources.css`
- `frontend/src/styles/responsive.css`
- `frontend/src/styles/shell.css`
- `frontend/tsconfig.json`
- `frontend/src/components/offers.tsx`
- `frontend/src/components/service-context.tsx`

Understand: React Query server state, cookie/CSRF client, loading/empty/error states, exact-offer dialogs, responsive/RTL layout; no invented evaluation scores. This connected screen set is one coherent UI batch.

Checks: npm --prefix frontend ci; lint; typecheck; build; Playwright desktop/mobile against fresh synthetic backend.

Update after actual work: Asad-progress.md; docs/DEMO_SCRIPT.md; docs/API.md; docs/VERIFICATION.md; docs/learning/FUNCTION_GUIDE.md; docs/report/04-planning-and-requirements.md.

Status: see docs/commits/verification.md; future work is not complete.

## B08 ? Deployment and full CI definition

Owner: Arif. Dependencies: B06, B07.

Exact files:

- `.dockerignore`
- `.env.example`
- `.github/workflows/ci.yml`
- `backend/Dockerfile`
- `docker-compose.yml`
- `frontend/Dockerfile`

Understand: Environment/secret separation, health checks, persistent volumes, SQLite versus PostgreSQL, CI credentials and browser setup.

Checks: complete backend/frontend/browser checks; docker compose config with temporary secrets; Docker/PostgreSQL migration, safety and backup/restore need actual runtime evidence. Do not label unrun CI as passed.

Update after actual work: Arif-progress.md; docs/CI.md; docs/RUNBOOK.md; docs/VERIFICATION.md; docs/report/03-feasibility-analysis.md.

Status: see docs/commits/verification.md; future work is not complete.

## B09 ? Reconciled prototype documentation and provenance

Owner: Shizza coordinates; each member supplies own evidence. Dependencies: B06, B07, B08.

Exact files:

- `AGENTS.md`
- `Arif-commits.md`
- `Arif-progress.md`
- `Asad-commits.md`
- `Asad-progress.md`
- `docs/planning/archive/package-manifest.json`
- `README.md`
- `Wasam-commits.md`
- `Wasam-progress.md`
- `backend/schemas/contracts/README.md`
- `docs/API.md`
- `docs/ARCHITECTURE.md`
- `docs/BUSINESS_CONFIGURATION.md`
- `docs/CI.md`
- `docs/DATABASE.md`
- `docs/DEMO_SCRIPT.md`
- `docs/FYP-II-HANDOVER.md`
- `docs/IMPLEMENTATION_STATUS.md`
- `docs/PRD.md`
- `docs/RUNBOOK.md`
- `docs/VERIFICATION.md`
- `docs/learning/DESIGN_CHOICES.md`
- `docs/learning/FUNCTION_GUIDE.md`
- `docs/learning/README.md`
- `docs/planning/FYP-I-plan.md`
- `docs/planning/PUSH_CHECKLIST.md`
- `docs/planning/WEEKLY_COMMIT_PLAN.md`
- `docs/planning/archive/pre-tuesday-progress.md`
- `docs/planning/decision-log.md`
- `docs/planning/gantt-plan.csv`
- `docs/planning/submission-checklist.md`
- `docs/planning/weekly-commits.json`
- `docs/report/01-introduction.md`
- `docs/report/02-literature-review.md`
- `docs/report/03-feasibility-analysis.md`
- `docs/report/04-planning-and-requirements.md`
- `docs/report/references.md`
- `docs/screenshots/README.md`
- `docs/screenshots/desktop-conversation.png`
- `docs/screenshots/desktop-overview.png`
- `docs/screenshots/mobile-conversation.png`
- `docs/screenshots/mobile-overview.png`
- `shizza-commits.md`
- `shizza-progress.md`
- `docs/ISP_PITCH.md`
- `docs/learning/visual-theme.md`
- `docs/planning/archive/progress-evidence-2026-10-31.md`
- `docs/learning/customer-service-context.md`

Understand: Generated origin, original-package hashes versus modified working tree, implementation limits, actual dates and pending academic acceptance. Existing progress edits are preserved separately; include only authorized session hunks.

Checks: check internal links/file inventory; reconcile every result with saved logs; repository hygiene and whitespace; no invented sources/signatures/attendance or completed future sessions.

Update after actual work: shizza-progress.md (actual coordination only); Wasam-progress.md; Arif-progress.md (actual work only); Asad-progress.md (actual work only); docs/report/01-introduction.md; docs/report/02-literature-review.md; docs/report/03-feasibility-analysis.md; docs/report/04-planning-and-requirements.md.

Status: see docs/commits/verification.md; future work is not complete.

## First proposed commit

`feat: add shared configuration and database foundation`

Only the B01 paths above. This establishes validated profile/request contracts and shared relational storage, with lint, focused tests and migration checks. It does not include application startup, workers, approval executors, UI, or the full CI replacement. The existing starter CI stays in the base until B08. No commit will be created until Wasam explicitly instructs it.

## Weekly Tuesday mapping - revised 2026-10-30

Each former A/B pair is now one Tuesday session, with 12 planned contributions per member. docs/planning/WEEKLY_COMMIT_PLAN.md lists all 48 scopes, files, dependency gates, checks and evidence requirements. These are review/edit scopes; B01-B09 remain exact source-integration groups. Do not split a coupled generated file just by labelling it an earlier week. A smaller executable slice needs explicit extraction/refactoring and clean snapshot verification. B01-B09 count within actual weekly work, not nine mandatory extra commits.

Follow docs/planning/PUSH_CHECKLIST.md before/after every authorized push. This scheduling request does not authorize staging, commits or pushes. B01 documentation changed, so old snapshot hashes are historical; rerun the current proposed batch before committing.

## ISP reference extension - 4 November 2026

B05 now includes registered fixture files, the read-only reference adapter, ISP profile and source-labelled knowledge/catalog data. B06 includes its authenticated endpoint and integration tests; B07 includes the offer browser. B09 documents the pitch. These dependencies are explicit in staging-manifests.json. Changed files invalidate earlier snapshot hashes. No new independent verification or publication is claimed.
