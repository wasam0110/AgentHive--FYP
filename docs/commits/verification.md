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
