# Shizza FYP-I progress

**Scope:** Domain agents, reference data/read tools, seed fixtures and academic documentation coordination.
**Target:** 15 January 2027. One Tuesday session each week; unfinished work carries forward.
**Cadence:** One combined contribution session per Tuesday each week. The former A/B tasks are combined into the single weekly deliverable shown below.

[Weekly scopes and dependencies](docs/planning/WEEKLY_COMMIT_PLAN.md) | [Push checklist](docs/planning/PUSH_CHECKLIST.md)

Dates below are plans, not attendance or completion claims. Record one dated weekly entry for each actual session, with any unfinished work carried forward. Aim for one focused commit when ready.

| Week | Planned Tuesday | Deliverable | Status | Actual date | Evidence / PR / test |
|---|---|---|---|---|---|
| W01 | 2026-10-27 | Define generic customer/catalog/resource records and two synthetic profile datasets; Create report outline, submission inventory and supervisor questions | In progress | 2026-11-06 | Reviewed committed Profile A/B, business-profile contract, Chapter 4 outline, Chapter 1 review items and submission inventory on `shizza/w01-profile-review` (`f17a06d`). Profile/contract checks and `git diff --check` passed; seed/read adapters, owner review and supervisor confirmation remain pending. No application behavior is claimed. |
| W02 | 2026-11-03 | Implement generic customer/catalog/resource/status tables and profile-scoped seed fixtures; Provide read adapters plus reusable sample records and tests | Not started | — | — |
| W03 | 2026-11-10 | Build Support worker with a fake retrieval adapter; Test evidence references, missing status facts and escalation | Not started | — | — |
| W04 | 2026-11-17 | Build Sales worker calling the quote interface; Test valid service proposal and no invented price behavior | Not started | — | — |
| W05 | 2026-11-24 | Build Scheduling worker using availability interface; Test proposed slots and lack of premature booking confirmation | Not started | — | — |
| W06 | 2026-12-01 | Review literature sources and citations; light mids session; Organize actual meeting notes and report gaps; no invented meetings | Not started | — | — |
| W07 | 2026-12-08 | Draft feasibility estimates with labelled assumptions; light session; Review SDG evidence needs and update schedule assumptions | Not started | — | — |
| W08 | 2026-12-15 | Connect reusable workers to profile-scoped retrieval and read adapters; Verify structured proposals in shared contract tests | Not started | — | — |
| W09 | 2026-12-22 | Add limited English/Roman Urdu/Urdu scenario fixtures; Review uncertainty, conflicts and clarification responses | Not started | — | — |
| W10 | 2026-12-29 | Run worker suite for Profiles A/B, including disabled booking; Assemble Chapters 1–4 draft and trace claims to evidence | Not started | — | — |
| W11 | 2027-01-05 | Review full demo; fix domain/data defects; Complete report draft and checklist; request supervisor review | Not started | — | — |
| W12 | 2027-01-12 | Apply received feedback and reconcile report with actual build; Finalize report package, pending signatures list and demo evidence | Not started | — | — |

## Work log

- **6 November 2026 - W01 combined session:** Reviewed committed Profile A/B distinctions, the business-profile contract, Chapter 4 requirements, Chapter 1 review items and submission inventory at base `a3f1083`. A enables `resource_booking` while B does not, and their catalog/knowledge references differ. A clean documentation-only snapshot with `shizza-progress.md` overlaid passed the profile/report assertions using Python 3.14 and `git diff --check`; no application runtime tests were run. Seed/read adapters remain blocked on B02/B04, and owner/supervisor review remains pending. Branch `shizza/w01-profile-review` contains commit `f17a06d`; no PR was created.

**Planning:** On 30 October 2026, the former A/B schedule was combined into 12 Tuesday sessions. The archived schedule is retained for historical context and does not create additional current sessions or completion claims. [Previous schedule](docs/planning/archive/pre-tuesday-progress.md).

**Next:** Review W01 contracts and the dependencies for your first contribution.

For each session, add a short dated note: work/files changed, checks and results, mocked or live dependencies, learning/review, affected docs, and next step. After a push, add the real SHA and observed PR/CI status. Follow the push checklist for details.
