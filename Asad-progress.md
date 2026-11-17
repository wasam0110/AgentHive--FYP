# Asad FYP-I progress

Owner: Asad

Module: Frontend dashboard/simulator and read-only operations overview API.

Target: 15 January 2027. This is a plan; no implementation or attendance is asserted.

Statuses: Not started → In progress → Standalone verified → Integration pending → Integrated and verified. Use Blocked with a reason when independent work is not possible. Document tasks may use Reviewed after an identified reviewer confirms them. Do not infer progress from dates.

| Session | Planned date | Deliverable | Status | Actual date | Evidence / PR / test | Dependency / next handoff |
|---|---|---|---|---|---|---|
| W01-A | 2026-10-26 | List generic user journeys and profile/capability fields needed by screens | Standalone verified | 2026-11-15 | Design contract and Chapter 4 update passed isolated sample assertions and whitespace checks; merged by PR #7 (`cb4a4b2`) | B01 is committed; human review/understanding pending; UI types remain future work |
| W01-B | 2026-10-29 | Sketch chat, approval and trace screens against shared samples | Standalone verified | 2026-11-17 | Initial contract merged by PR #7 (`cb4a4b2`); text layouts and evidence pushed in `8494e86` on `asad/w02-overview-counts`; no rendered UI | PR not opened; human review/understanding pending |
| W02-A | 2026-11-02 | Define overview count response and status meanings | Standalone verified | 2026-11-15 | Count response JSON and eight meanings checked against helper; published in `8494e86`; current B06 route uses dynamic buckets, so exact response alignment needs owner review | Review current route with Wasam; helper is not integrated |
| W02-B | 2026-11-05 | Write small aggregation function with synthetic fixture tests | Standalone verified | 2026-11-15 | Pure status aggregator; 3 focused tests passed on `cb4a4b2` and reran on current main `0303cf1`; published in `8494e86` | Helper is not called by current B06 route; ask Wasam before wiring it in |
| W03-A | 2026-11-09 | Implement protected read-only overview endpoint | Integrated and verified | 2026-11-17 | B06 route is on main; implementation is Wasam's. Asad verified access/count behavior without changing the shared endpoint | Review count-contract alignment before frontend integration |
| W03-B | 2026-11-12 | Test counts, empty data and denied access using agreed backend adapter | Standalone verified | 2026-11-17 | 10 tests in `tests/test_auth.py` passed in a clean Python 3.12 snapshot; Ruff passed | Tests are local on `asad/w03-overview-tests`; commit/PR review still needed |
| W04-A | 2026-11-16 | Prepare frontend component plan and mock response fixtures | Not started | — | — | Use shared contracts; record live handoff when applicable |
| W04-B | 2026-11-19 | Define waiting/error/loading and approval-confirmation behavior | Not started | — | — | Use shared contracts; record live handoff when applicable |
| W05-A | 2026-11-23 | Specify API client contract and frontend acceptance cases | Not started | — | — | Use shared contracts; record live handoff when applicable |
| W05-B | 2026-11-26 | Review mock events for each supported demo journey | Not started | — | — | Use shared contracts; record live handoff when applicable |
| W06-A | 2026-11-30 | Review Chapter 4 interface requirements; light mids session | Not started | — | — | Use shared contracts; record live handoff when applicable |
| W06-B | 2026-12-03 | Check accessible labels and Urdu layout requirements; light session | Not started | — | — | Use shared contracts; record live handoff when applicable |
| W07-A | 2026-12-07 | Review screen flow and sample API data; light mids session | Not started | — | — | Use shared contracts; record live handoff when applicable |
| W07-B | 2026-12-10 | Resolve documented contract questions and small overview defects | Not started | — | — | Use shared contracts; record live handoff when applicable |
| W08-A | 2026-12-14 | Finalize configurable labels, currency/timezone and capability-aware mock screens | Not started | — | — | Use shared contracts; record live handoff when applicable |
| W08-B | 2026-12-17 | Verify overview endpoint against available real data models | Not started | — | — | Use shared contracts; record live handoff when applicable |
| W09-A | 2026-12-21 | Verify backend APIs match frontend fixtures | Not started | — | — | Use shared contracts; record live handoff when applicable |
| W09-B | 2026-12-24 | Prepare concise AI implementation brief and frontend test plan | Not started | — | — | Use shared contracts; record live handoff when applicable |
| W10-A | 2026-12-28 | Generate/build frontend foundation and demo chat using AI assistance | Not started | — | — | Use shared contracts; record live handoff when applicable |
| W10-B | 2026-12-31 | Connect API client, login/session flow and conversation display | Not started | — | — | Use shared contracts; record live handoff when applicable |
| W11-A | 2027-01-04 | Build approval and basic inspector screens; connect real APIs | Not started | — | — | Use shared contracts; record live handoff when applicable |
| W11-B | 2027-01-07 | Verify consent, approvals, REST recovery and capability-aware UI; add frontend CI | Not started | — | — | Use shared contracts; record live handoff when applicable |
| W12-A | 2027-01-11 | Run user journeys from clean setup and correct UI defects | Not started | — | — | Use shared contracts; record live handoff when applicable |
| W12-B | 2027-01-14 | Rehearse complete demo and supply verified Chapter 4 screenshots | Not started | — | — | Use shared contracts; record live handoff when applicable |

## Session evidence log

Append entries rather than overwriting prior evidence:

### 2026-11-15 - W01 design contract merged; standalone verified

- Implemented or reviewed: mapped generic chat, approval and trace journeys to the committed conversation, task, proposal and profile contracts; distinguished server state from local form state and recorded role/data boundaries.
- Files / commit / PR: the initial `docs/API.md` contract, Chapter 4 update and evidence were committed as `364248a0c4ec097f0220413f066b97d7b384e7f3`; [PR #7](https://github.com/wasam0110/AgentHive--FYP/pull/7) merged to `main` at `cb4a4b277bb452dadff06cef34cbfaa30f6ef601` on 2026-11-15. The later layout addendum and refreshed W01/W02 evidence were pushed in `8494e866734b5d53309b16f770dd9ed53d8ae76d` on `asad/w02-overview-counts`; a new PR has not been opened.
- Commands run and observed results: from the isolated candidate snapshot, Node assertions against `sample_payloads.json`, the screen contract and its report link passed; `git diff --check` and the new-file trailing-whitespace check passed. The first inline assertion had a wording typo; the corrected assertion passed without source changes. GitHub push and pull-request CI both passed the "Starter checks (no application tests yet)" job; this job checks required starter files, tracked-file hygiene and patch whitespace only.
- Mocked dependencies versus real integrations: design and committed synthetic sample only; no API, frontend, authentication or browser journey ran.
- W01 outcome and limits: the initial journeys and screen/data contract are merged. The separate low-fidelity layout addendum is recorded below. This remains design documentation only; no frontend, API, authentication or browser journey was implemented or tested.
- What to review/understand: proposal versions bind consent and approval; the UI presents backend state without treating local choices as authorization. Student review/understanding is pending.
- Report sections updated: Chapter 4 interface journey contract.
- Blocker, owner and next action: At the time of this entry, B06/B07 integration was not on `main`. B06 is now present on `origin/main`; its authenticated overview endpoint does not use this W02 helper. Review that route with Wasam before proposing integration. B07/frontend remains separate.
- Reviewer and review date: no GitHub review recorded; human review and student teach-back remain pending.

### 2026-11-15 - W02 overview count candidate

- Implemented or reviewed: defined a count-only overview response and meanings for the eight shared conversation statuses. Added a pure helper that returns all status buckets, including zeros, and rejects an unknown status.
- Files / branch / commit: `backend/services/overview.py`, `tests/unit/test_overview.py`, `docs/API.md`, `Asad-progress.md`, `docs/VERIFICATION.md`, and `docs/commits/verification.md`; pushed in commit `8494e866734b5d53309b16f770dd9ed53d8ae76d` on `asad/w02-overview-counts`; PR not opened.
- Commands run and observed results: `python -m unittest discover -s tests/unit -p 'test_overview.py'` passed 3 tests in a clean snapshot based on `cb4a4b277bb452dadff06cef34cbfaa30f6ef601`. The first run from the parent directory could not import `backend`; rerunning from the repository root and then the clean snapshot passed.
- Mocked dependencies versus real integrations: synthetic status strings only; no database, endpoint, authentication or frontend integration is included.
- W02 outcome and limits: the count contract/helper are standalone-verified. `origin/main` now contains an authenticated, business-scoped `/api/v1/overview` route from B06, but it uses dynamic status buckets and does not call this helper. The zero-bucket contract is therefore not integrated.
- What to review/understand: the function counts conversation records, not tasks; all eight status keys remain present at zero; unknown stored status raises `ValueError` instead of disappearing from totals. Student review/understanding is pending.
- Report sections updated: none; the API contract was updated.
- Blocker, owner and next action: ask Wasam to review whether the fixed zero-bucket contract should replace or supplement the existing B06 aggregation. Do not duplicate or silently alter the shared route. Full application dependencies and pytest/Ruff are unavailable in the configured Python 3.9.6 environment; only the standard-library focused test ran.
- Reviewer and review date: pending.

### 2026-11-17 - W01 layout addendum

- Implemented or reviewed: added low-fidelity text layouts for chat, approval and trace, preserving exact-version decisions, separate customer/admin consent, evidence sources, and failure/waiting states.
- Files / branch / commit: `docs/API.md` and `Asad-progress.md`; pushed in commit `8494e866734b5d53309b16f770dd9ed53d8ae76d` on `asad/w02-overview-counts`; PR not opened.
- Commands run and observed results: layout assertions and tracked/new-file whitespace checks passed in the combined clean snapshot based on `origin/main` `0303cf15a509f7ff9ca6831967a54d0a40d4c084`. Revalidation details are recorded in `docs/commits/verification.md`.
- Mocked dependencies versus real integrations: documentation only; no rendered UI, API, or browser flow.
- What to review/understand: these are text wireframes that define information hierarchy, not screenshots or implemented screens. Human review remains pending.
- Report sections updated: none; `docs/API.md` contains the layouts.
- Blocker, owner and next action: request human review; keep the B07 implementation separate.
- Reviewer and review date: pending.

### 2026-11-17 - Current-main W02 integration review

- Reviewed `origin/main` at `0303cf15a509f7ff9ca6831967a54d0a40d4c084`: `backend/api/operations.py` exposes an authenticated, role-checked, business-scoped `/api/v1/overview` route.
- The route returns `total`, dynamic `status_counts`, and additional operational values. It currently uses `Counter` directly and does not call `backend/services/overview.py`; the W02 helper's fixed zero buckets and unknown-status rejection remain standalone only.
- Next handoff: ask Wasam to review this difference before changing the shared route. No route integration or application test is claimed in this contribution.

### 2026-11-17 - W03 overview route test candidate

- Implemented or reviewed: inspected the B06 `/api/v1/overview` route on main. It authenticates the user, permits operator/admin/evaluator roles, and filters conversations by `user.business_id`. The route implementation is Wasam's B06 work; Asad did not change it.
- Files / branch / commit: added customer-denial, empty-aggregate, and conversation-status count tests in `tests/test_auth.py` on `asad/w03-overview-tests`; W03 changes remain local and uncommitted.
- Commands run and observed results: in a clean snapshot based on merged `origin/main` `1bce284da8517ad9ba3892c25d0088e742f31021`, with only `tests/test_auth.py` overlaid, `python -m pytest -q tests/test_auth.py` passed (10 tests) under Python 3.12; `ruff check tests/test_auth.py` passed.
- Mocked dependencies versus real integrations: synthetic records, SQLite and FastAPI TestClient; no external model or live business service.
- W03 outcome and limits: empty results, counts for queued/waiting/completed conversations, and customer-role denial are verified. The endpoint still uses dynamic status buckets and does not call the W02 fixed-bucket helper; cross-business isolation is implemented by the query filter but not specifically asserted in this added test slice.
- What to review/understand: route role checks authorize staff roles, while the query independently scopes records to the authenticated user's business. The added tests exercise response counts and customer denial.
- Blocker, owner and next action: request Wasam's review before integrating the fixed W02 response shape. W03 tests are not yet pushed.
- Reviewer and review date: pending.

- Session and actual date:
- Implemented or reviewed:
- Files / commit / PR:
- Commands run and observed results:
- Mocked dependencies versus real integrations:
- What I can explain:
- Report sections updated:
- Blocker, owner and next action:
- Reviewer and review date, if actually reviewed:

## Final handoff

- Standalone verification: W01 design/sample assertions and local layout assertions passed; W02 aggregation tests passed in a clean snapshot; no application tests were run.
- Live integration verification: Not started.
- Documentation reviewed: Human/team review pending.
- Known limitations: W01 layout addendum and W02 changes are merged by PR #9. W01 remains design-only. W02 helper is not wired to the main overview route. W03 route tests pass in an isolated Python 3.12 snapshot but remain uncommitted/unpushed. Human/owner review and frontend/browser verification remain pending.
