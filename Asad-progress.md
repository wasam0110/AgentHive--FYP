# Asad FYP-I progress

Owner: Asad

Module: Frontend dashboard/simulator and read-only operations overview API.

Target: 15 January 2027. This is a plan; no implementation or attendance is asserted.

Statuses: Not started → In progress → Standalone verified → Integration pending → Integrated and verified. Use Blocked with a reason when independent work is not possible. Document tasks may use Reviewed after an identified reviewer confirms them. Do not infer progress from dates.

| Session | Planned date | Deliverable | Status | Actual date | Evidence / PR / test | Dependency / next handoff |
|---|---|---|---|---|---|---|
| W01-A | 2026-10-26 | List generic user journeys and profile/capability fields needed by screens | In progress | 2026-11-15 | W01 design candidate in docs/API.md and Chapter 4; sample assertions and whitespace checks passed in a clean snapshot; not published | B01 is committed; review candidate; frontend types deferred to B07 |
| W01-B | 2026-10-29 | Sketch chat, approval and trace screens against shared samples | In progress | 2026-11-15 | W01 design candidate in docs/API.md and Chapter 4; sample assertions and whitespace checks passed in a clean snapshot; not published | B01 is committed; review candidate; frontend types deferred to B07 |
| W02-A | 2026-11-02 | Define overview count response and status meanings | Not started | — | — | Use shared contracts; record live handoff when applicable |
| W02-B | 2026-11-05 | Write small aggregation function with synthetic fixture tests | Not started | — | — | Use shared contracts; record live handoff when applicable |
| W03-A | 2026-11-09 | Implement protected read-only overview endpoint | Not started | — | — | Use shared contracts; record live handoff when applicable |
| W03-B | 2026-11-12 | Test counts, empty data and denied access using agreed backend adapter | Not started | — | — | Use shared contracts; record live handoff when applicable |
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

### 2026-11-15 - W01 design candidate (publication pending)

- Implemented or reviewed: mapped generic chat, approval and trace journeys to the committed conversation, task, proposal and profile contracts; distinguished server state from local form state and recorded role/data boundaries.
- Files / commit / PR: `docs/API.md`, `docs/report/04-planning-and-requirements.md`, `Asad-progress.md`; W01-only publication authorized, commit and push pending.
- Commands run and observed results: from a clean snapshot, Node assertions against `sample_payloads.json`, the screen contract and its report link passed; `git diff --check` and the new-file trailing-whitespace check passed. A first inline assertion had a wording typo and failed; the corrected assertion passed without source changes.
- Mocked dependencies versus real integrations: design and committed synthetic sample only; no API, frontend, authentication or browser journey ran.
- What I can explain: proposal versions bind consent and approval; the UI presents backend state without treating local choices as authorization. Student review/understanding is pending.
- Report sections updated: Chapter 4 interface journey contract.
- Blocker, owner and next action: B06/B07 API and frontend integration are not present on `main`; retain `frontend/src/lib/types.ts` for B07 and do not claim a live journey. W02 overview implementation awaits B06. Verify the planned B03-to-B02 dependency with Arif/Wasam: B03 and B05a commits are on `main`, but B02 auth, B04 and full B05 are not.
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

- Standalone verification: Not started.
- Live integration verification: Not started.
- Documentation reviewed: Not started.
- Known limitations: Not yet assessed.
