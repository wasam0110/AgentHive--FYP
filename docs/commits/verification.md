# Isolated batch verification

Actual import, automated review, modifications and verification: **2026-10-30 (Asia/Karachi)**. Automated checks; human review remains pending. See ../PROJECT_ORIGIN.md for the origin record.

## B01 ? shared foundation

Base committed project: `1c35bb5e4c2ef4ab59d7bf5580e42a8b5d6a8c9c`. The snapshot was constructed with `git archive HEAD`, then only the 22 exact B01 files from staging-manifests.json were copied. No Git index or commit was created. In particular backend/main.py, backend/services, backend/agents, scripts/seed.py, tests/conftest.py and frontend were absent; the old committed documents/contracts/profile examples and starter CI remained.

The existing project .venv supplied installed third-party dependencies from requirements.txt. There are no editable project installs; PYTHONPATH and database/model overrides were cleared. Module paths resolve to the snapshot. No working .env, private instruction, runtime database or unrelated uncommitted module was copied.

Command (run from the workspace with Python 3.12.10):

```powershell
.\.venv\Scripts\python.exe scripts/verify_batch.py B01 C:\Users\wasam\AppData\Local\AgentHive-imports\20261030-193137\snapshot-B01-final
```

| Check in snapshot | Observed result |
|---|---|
| `python -m ruff check backend scripts tests` | Passed |
| `python -m pytest -q tests/unit/test_foundation.py` | 8 passed |
| `python -m alembic upgrade head` | Passed on fresh SQLite |
| `python -m alembic check` | No new upgrade operations |

The initial snapshot also passed these checks. The final snapshot reruns after documentation/test-plan edits to bind evidence to the final B01 contents. Private `batch-evidence.json` within each snapshot records base SHA, every overlaid source hash, exact commands and output. Review the final evidence before committing; source edits invalidate this result and require a new snapshot.

This verifies the foundation's profile/schema/storage behavior only. It does not verify a runnable HTTP application, consent/execution services, frontend or PostgreSQL. Human review is pending and **no staging/commit/push is authorized**.

## Arif W01-A documentation candidate - 10 November 2026

The proposed documentation change is based on the committed B01 base and contains only
the policy matrix, proposal/decision/receipt contract additions, database responsibility
notes, learning note and Arif progress evidence. No B02 identity files or B03 service
files were copied from the reference source.

`python scripts/check_repository.py` and `git diff --check` passed. This is a
documentation-only check; it does not establish quote, approval, transaction, or receipt
runtime behavior. The candidate remains uncommitted pending human/team review.

## Arif W02/W03 quote and proposal-validation candidate - 12 November 2026

Base: committed `origin/main` at `98ee63e62a7b666793f4220064c12e819be30a6e` (B01 plus
the merged Shizza fixture-contract work). B02 identity files are still absent. Only
`backend/services/approvals.py`, `backend/services/quotes.py`,
`backend/services/redaction.py`, `tests/unit/test_quote_service.py`,
`Arif-progress.md`, `docs/DATABASE.md`, `docs/learning/policy-contracts.md`,
`docs/commits/COMMIT_PLAN.md`, `docs/commits/staging-manifests.json` and this evidence
file were overlaid. The code adds quote calculation, read-only proposal revalidation and
recursive trace redaction; it does not expose a route or implement consent, administrator
approval, execution or receipt creation.

The clean snapshot at `C:\Users\PC\AppData\Local\Temp\AgentHive-Arif-Nov12-98ee63e` was
exported from committed HEAD and overlaid only with the listed candidate code and
documentation files. Observed checks:

| Check | Result |
|---|---|
| `python scripts/check_repository.py` | Passed |
| `python -m pytest -q tests/unit/test_quote_service.py tests/unit/test_foundation.py` | 36 passed |
| `python -m ruff check backend/services/quotes.py backend/services/approvals.py backend/services/redaction.py tests/unit/test_quote_service.py` | Passed |
| `git diff --cached --check` | Passed |

This verifies the focused standalone quote and proposal-validation behavior, not the
complete B03 batch. The B03 dependency on committed B02 identity is still unmet; there
is no authenticated API wiring, customer-consent flow, administrator approval, execution
transaction, or receipt replay in this candidate.

The local `batch-evidence.json` in the snapshot records each overlaid file's SHA-256,
commands and observed results. Any source edit invalidates those hashes and requires a
fresh snapshot run.

## B02?B09

Not independently verified. Their prerequisites have not been committed. The complete imported application passed 49 backend tests, frontend checks and two browser journeys, but that does not satisfy the independent batch rule. First commit the approved prerequisites, then export that committed base and overlay only the next batch's exact files, run its listed checks and record results with actual dates. No future work is complete.

## Tuesday planning edits - 2026-10-30

COMMIT_PLAN.md and staging-manifests.json changed for the weekly Tuesday plan. The earlier eight-test snapshot remains historical evidence, but its hashes do not describe the current B01. A fresh B01 snapshot is required before calling the current batch independently verified or committing it. Weekly entries are plans; no later batch has gained independent verification.

## Commit-title documentation change - 2026-10-31

The proposed B01 commit title in COMMIT_PLAN.md changed to `feat: add shared configuration and database foundation`. Earlier snapshot results remain historical evidence, but their COMMIT_PLAN.md hash no longer matches. Rebuild the exact B01 snapshot before committing; this documentation edit does not establish a new runtime result.

## Private prompt cleanup - 2026-10-31

.gitignore changed to exclude docs/prompts/. Previous B01 snapshot hashes remain stale; rerun the exact current foundation snapshot before claiming independent verification or committing. Private prompt files are not part of any proposed application batch.

## Repository cleanup - 2026-10-31

B01 now includes docs/PROJECT_ORIGIN.md. Its manifest and documentation changed; previous snapshot hashes are historical only. Run a fresh exact-batch snapshot before committing. B09 no longer includes the duplicate HTML handover. B07 drops the unused Prettier development dependency; its independent verification remains pending committed prerequisites.


## ISP extension - 4 November 2026

Profile capability/schema, fixture loading, workflow, API, UI and staging manifests changed. All prior exact-snapshot hashes remain historical. The current B01 needs a fresh snapshot, and B02-B09 remain pending committed prerequisites and independent verification. Full working-tree test results belong in VERIFICATION.md.

## 4 November 2026 - customer-context foundation

B01 was retested as committed HEAD plus only its exact manifest: lint, eight foundation tests, fresh SQLite migration and metadata comparison passed. The final snapshot after documentation updates is C:/Users/wasam/AppData/Local/AgentHive-imports/20261104-customer-context-B01-final; batch-evidence.json records commands, base SHA and file hashes. Compare current bytes to those hashes before any commit. No other uncommitted modules are copied. B02-B09 remain pending independent checks after their dependencies are committed; full-tree integration success does not substitute for them.

## 4 November 2026 - folder cleanup snapshot

The earlier customer-context B01 hashes are superseded by documentation/manifest cleanup. Current snapshot location: C:/Users/wasam/AppData/Local/AgentHive-imports/20261104-cleanup-B01. Read its batch-evidence.json for actual results and current hashes; later batches still need their committed prerequisites and independent checks.

## Wasam W02 publication candidate - 4 November 2026

Base: 433a3c1c1a0559ce14957cf55302b1b52eb46541 (current origin/main). Candidate: the exact B01 manifest files plus only the dated foundation additions to Wasam-progress.md and docs/report/04-planning-and-requirements.md. No other uncommitted modules or prior local progress rewrites are included. Snapshot: C:/Users/wasam/AppData/Local/AgentHive-imports/20261104-w02-candidate-check. Its publication-evidence.json records the full candidate path/hash list and actual command results. Run lint, eight foundation tests, fresh SQLite migration/metadata comparison, hygiene and whitespace checks before publication. Remote starter CI checks hygiene only; application CI and PostgreSQL remain later work.

Observed local results (4 November 2026): Ruff passed; eight foundation tests passed; fresh SQLite upgrade and Alembic metadata check passed. No application modules outside B01 were present. Remote CI remains unobserved; PostgreSQL and HTTP integration are outside this candidate.

## Shizza W02 fixture-contract candidate (B05a) - 11 November 2026

Base: committed `main` at `0f3b4ab87b831e650941df5dc94d900983246d82`. The snapshot was created with `git archive HEAD` and only the B05a candidate paths were overlaid. The source-only snapshot is `C:\Users\mhamz\AppData\Local\AgentHive-verify\20261111-B05a-final`; its virtual environment and `batch-evidence.json` are outside the snapshot. The evidence JSON records the complete path/hash list, environment, commands, and outputs.

Python 3.14.0; isolated virtual environment with the pinned test dependencies from requirements.txt (`pytest==9.2.0`, `pydantic==2.14.1`, `pycountry==26.2.16`, `python-dotenv==1.2.4`, `ruff==0.17.3`, `tzdata==2026.6`). `PYTHONPATH`, `DATABASE_URL`, `BUSINESS_PROFILE`, and `CHROMA_PATH` were cleared. Import resolution confirmed `backend` came from the snapshot.

| Check | Result |
|---|---|
| `python -m pytest -q tests/unit/test_seed_fixtures.py` | Passed: 6 tests |
| `ruff check scripts/seed_fixtures.py tests/unit/test_seed_fixtures.py` | Passed |
| `git diff --check` for tracked edits; `git diff --no-index --check` against empty input for each new path | Passed; no whitespace diagnostics |

The initial test attempt exposed missing timezone data in the minimal environment, not a source failure. Installing the pinned `tzdata==2026.6` dependency and rerunning produced the result above. No database or retrieval integration ran; B02 and B04 are not committed on `main`, and full B05 remains pending. Candidate is not staged, committed, or pushed; human review is pending. Evidence JSON: `C:\Users\mhamz\AppData\Local\AgentHive-verify\20261111-B05a-final-evidence.json`.

## Asad W01 design candidate - 15 November 2026

- Base: committed `main`, `36ffdbceab3f5d076aa3e61dadd5b103c3af2b12`.
- Snapshot: `/Users/apple/Desktop/doc/AgentHive-FYP-w01-authorized-snapshot`; exported with `git archive HEAD`, then only `Asad-progress.md`, `docs/API.md`, `docs/report/04-planning-and-requirements.md`, `docs/VERIFICATION.md` and this evidence file were overlaid.
- Environment: macOS; Git 2.39.2; Node.js 26.13.0; Python 3.9.6. Python 3.12, Node.js 24 and `tsc` were unavailable. No dependencies were installed.
- Checks from the snapshot root: an inline Node assertion check parsed `backend/schemas/contracts/sample_payloads.json` and checked the conversation/message link, waiting-customer task, evidence source, proposal version, separate confirmation/approval flags, screen contract fields, design-only label, Chapter 4 subsection and relative link. All assertions passed. `git diff --check` and a trailing-whitespace scan of the new API document also passed.
- Retry note: the first assertion script failed on a typo in its expected wording (`not a frontend-only decisions`); correcting the assertion to match the document produced a pass with no source changes.
- Candidate paths: `Asad-progress.md`, `docs/API.md`, `docs/report/04-planning-and-requirements.md`, `docs/VERIFICATION.md`, `docs/commits/verification.md`.
- Candidate SHA-256 (design/progress payload; evidence files are excluded to avoid self-referential checksums):
  - `Asad-progress.md`: `e56ccccf1d8f5a0f021c2e05770894f1416121feac74e4e402ef7797de092a87`
  - `docs/API.md`: `0e0b21ef249d4219e573184f606786c93df5005f8540be59574473c767f49617`
  - `docs/report/04-planning-and-requirements.md`: `64df9e31ed0ea3ab0aa6d34b4cb38b42f567782ece4597a4238e4959bd2b68d9`
- Dependency evidence: B01 (`081b1be`) and B05a (`b0cf68a`) are ancestors of base. B03 code is also present, but the planned B02 authentication prerequisite is absent; B04, full B05, B06 and B07 are absent. Do not treat the presence of B03 as proof that B02 is satisfied.
- Limits: this is a design/fixture-document check, not an API, frontend typecheck, browser, authorization or end-to-end result. W01-only publication was authorized after review; commit/push is pending. W01 remains in progress because the frontend type contract is deferred to B07.

## W03/B06 dependency review - 2026-11-16

The conversation/API candidate was checked after B03 quote validation and B05 fixture-contract work became available on `main`. Test collection stopped before execution with:

```text
ModuleNotFoundError: No module named 'backend.services.service_context'
```

`backend.services.service_context` is part of the uncommitted B04/prototype scope. Therefore W03 conversation persistence, history reload and cross-customer denial remain blocked; no B06 runtime result or integration completion is claimed. The candidate files remain preserved in the local `pre-B06 prototype worktree 2026-11-16` stash for a later exact-batch verification.

## B04 retrieval/provider verification - 2026-11-16

- Restored exact B04 retrieval/provider files from the preserved prototype stash; no B05 or B06 source was restored.
- `.\.venv\Scripts\python.exe -m pytest -q tests/unit/test_retrieval_service.py`: **passed, 1 test**.
- Ruff on `backend/agents`, `backend/rag` and `tests/unit/test_retrieval_service.py`: **passed**.
- This is focused B04 evidence only. It does not establish B05 seed/read integration or B06 conversation/API, ownership, restart or safety behavior.

## B05 seed/read workflow verification - 2026-11-16

- Restored the planned B05 seed/read workflow after B04 was committed.
- `.\.venv\Scripts\python.exe -m pytest -q tests/unit/test_seed_workflow.py`: **passed, 1 test**.
- Ruff on the exact B05 source/test paths: **passed**.
- The test verifies repeatable profile-B seeding retains the original password hash, does not create disabled booking slots, and denies scheduling while allowing the seeded sales result.
- This is focused B05 evidence only. B06 HTTP conversation, ownership, restart, queue and approval safety checks remain pending.

## B06 persisted API and safety verification - 2026-11-16

- Restored the planned conversation/API, worker, operations and integration-test paths after B04 and B05 were committed.
- Fixed the coupled approval API gap required by the B06 routes (`confirm`, `decide`, `refresh`) and added explicit `isp-pitch` fixture registration for the profile-scoped integration fixture.
- Aligned the quote validation error wording with the API contract: invalid discounts report that they are outside policy limits.
- Focused command:
  `.\.venv\Scripts\python.exe -m pytest -q tests/test_approvals.py tests/test_auth.py tests/test_profiles_rag.py tests/test_provider.py tests/test_workflow.py tests/test_reference_offers.py tests/test_service_context.py tests/unit/test_retrieval_service.py tests/unit/test_seed_workflow.py`
- Result: **49 passed**.
- Ruff passed for the exact B06 integration paths and coupled approval/fixture files.
- Coverage includes conversation history, customer/business ownership, authentication/CSRF/expiry, queue idempotency and recovery, profile isolation, provider behavior, consent/approval/receipt replay and duplicate-booking safety. Provider behavior is demo/mocked; no paid model call was used.
