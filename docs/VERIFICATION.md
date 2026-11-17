# Verification record

## Shizza W02 fixture-contract candidate (B05a) - 11 November 2026

- Base: committed `main` `0f3b4ab87b831e650941df5dc94d900983246d82`.
- Snapshot: `C:\Users\mhamz\AppData\Local\AgentHive-verify\20261111-B05a-final`; committed HEAD exported with `git archive`, then only B05a manifest paths overlaid. The isolated virtual environment and evidence JSON are outside this source snapshot.
- Environment: Python 3.14.0; isolated venv with pinned test dependencies from requirements.txt. `PYTHONPATH`, `DATABASE_URL`, `BUSINESS_PROFILE`, and `CHROMA_PATH` were cleared. Import check confirmed `backend` resolved inside the snapshot.
- Results: `python -m pytest -q tests/unit/test_seed_fixtures.py` passed (6 tests); Ruff passed for the new module and tests; `git diff --check` passed for tracked edits and `git diff --no-index --check` passed against empty input for each new file, with no whitespace diagnostics.
- Setup note: the first minimal-environment run lacked `tzdata`; installing the pinned `tzdata==2026.6` dependency and rerunning passed without source changes.
- Limitations: this verifies profile-to-fixture validation only. It does not seed a database, test reference read adapters, or establish workflow integration. B02/B04 are absent from committed `main`; full B05 remains pending.
- Candidate SHA-256 values and captured command output: `C:\Users\mhamz\AppData\Local\AgentHive-verify\20261111-B05a-final-evidence.json`.

## Asad W01 design candidate - 15 November 2026

- Base: committed `main` at `36ffdbceab3f5d076aa3e61dadd5b103c3af2b12`.
- Scope: W01 journey/profile fields and chat, approval and trace screen design in `docs/API.md` and Chapter 4. No frontend or API implementation was added.
- Snapshot: clean `git archive HEAD` snapshot at `/Users/apple/Desktop/doc/AgentHive-FYP-w01-authorized-snapshot`, with only the candidate documentation/progress/evidence paths overlaid.
- Checks: Node assertions against the committed shared sample and W01 documents passed; `git diff --check` and trailing-whitespace checks passed.
- Limits: documentation/fixture contract validation only. No TypeScript, backend, frontend, browser or live API test ran. The host has Node 26.13.0 and Python 3.9.6, not the handoff's Node 24/Python 3.12. B06/B07 are not integrated.
- First assertion attempt: one inline assertion used incorrect expected wording and failed; the corrected assertion passed without source changes.
- Full isolated snapshot details and candidate hashes: `docs/commits/verification.md`. At candidate-verification time, publication was pending; see the dated follow-up below for the actual merge result.

## Asad W01 publication follow-up - 15 November 2026

The W01 documentation candidate was committed as `364248a0c4ec097f0220413f066b97d7b384e7f3` on `asad/w01-screen-contract`. [PR #7](https://github.com/wasam0110/AgentHive--FYP/pull/7) was merged to `main` at `cb4a4b277bb452dadff06cef34cbfaa30f6ef601` on 2026-11-15.

GitHub push run `43750137494` and pull-request run `43750314776` both succeeded. Each ran only `Starter checks (no application tests yet)`, which checks required starter files, tracked-file hygiene and patch whitespace. These results do not add application-test coverage to the design-only snapshot checks above. No formal GitHub review is recorded; human review and student understanding remain pending.

## Asad W02 overview-count candidate - 15 November 2026

- Base: committed `main` at `cb4a4b277bb452dadff06cef34cbfaa30f6ef601`.
- Scope: proposed count-only response/status definitions in `docs/API.md`, plus a pure conversation-status aggregator and synthetic unit tests. No endpoint, database query, authentication or frontend integration was added.
- Snapshot: `/tmp/AgentHive-FYP-w02-snapshot`, a detached worktree at the committed base with the W02 helper/test and final `docs/API.md` overlaid; the API document includes the W01 screen-layout addendum.
- Environment and result: Python 3.9.6 workspace venv; standard-library `unittest` only. `python -m unittest discover -s tests/unit -p 'test_overview.py'` passed (3 tests) from the snapshot root.
- Limits: pytest, Ruff, full application tests, API/auth integration and browser checks were not run. The B06 overview design/review gate remains pending; this result verifies only the independent helper and count contract.

## Asad W01 layout addendum - 17 November 2026

- Scope: added low-fidelity text layouts for chat, approval and trace to `docs/API.md`; no frontend code or screenshots were added.
- Check: Node assertions confirmed all three layouts, the local draft/send area, exact-version approval details, evidence IDs, and separation of customer consent from administrator approval; the same assertions passed in the combined clean snapshot.
- Status and limits: this addendum is local on `asad/w02-overview-counts`, not part of merged PR #7; human review remains pending.

## Asad W01/W02 revalidation on updated main - 17 November 2026

- Base: current `origin/main` at `0303cf15a509f7ff9ca6831967a54d0a40d4c084`.
- Snapshot: `/tmp/AgentHive-FYP-w01-w02-pr-snapshot`, a detached worktree at that base with only the W01/W02 candidate files overlaid.
- Checks: W02 standard-library `unittest` passed (3 tests); Node assertions verified the W01 layouts, parsed the W02 response JSON, matched its eight status keys to the helper, and confirmed the current-main integration note; `git diff --check` and new-file trailing-whitespace checks passed.
- Limits: no pytest/Ruff, database/API test, or browser journey ran. The current B06 route exists but does not call the helper or emit all known zero-count buckets. CI remains starter-only.
- SHA-256: `backend/services/overview.py` `76f41b9597135c58f55c63b152823ab511534610f274416a8479f343f461eeff`; `tests/unit/test_overview.py` `a66b05d290df5667d1c99476fb1dd01eea960b1c7eff318d8da7201ee10784e3`; `docs/API.md` `204f955cc0b1597f03f051f7f7934e7935e145681424a307eef82ca6f2640585`.

## Asad W03 overview route test candidate - 17 November 2026

- Base: merged `origin/main` at `1bce284da8517ad9ba3892c25d0088e742f31021`, with only `tests/test_auth.py` overlaid in `/tmp/AgentHive-FYP-w03-merged-snapshot`.
- Reviewed current B06 `/api/v1/overview`: authenticated, role-restricted to operator/admin/evaluator, and filtered by the caller's business. The route implementation was not changed by Asad.
- Checks: `python -m pytest -q tests/test_auth.py` passed (10 tests) under Python 3.12; `ruff check tests/test_auth.py` passed.
- Added coverage: customer denial, empty aggregates, and counts across queued/waiting/completed conversations. Existing auth/CSRF/ownership tests also passed.
- Limits: no UI/browser journey ran. The route's business filter was reviewed but not explicitly asserted as a cross-business case in this W03 addition. The current route uses dynamic status buckets and does not call the W02 helper.
- SHA-256: `tests/test_auth.py` `76b6bfa434e04c70187ef028402466fcf9566b823396712b710fd60f2de51fea`.

## Asad W03 publication follow-up - 17 November 2026

- Commit `e94d2b04b2df8b46065286cd270504d4e45dc858` was pushed to `asad/w03-overview-tests`; [PR #10](https://github.com/wasam0110/AgentHive--FYP/pull/10) is open against `main`.
- GitHub reports the PR check passed. The repository workflow is `Starter checks (no application tests yet)`, so this does not replace the local Python 3.12 pytest/Ruff results above.
- Human review and merge are pending; no merge is claimed.
