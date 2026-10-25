# Agent Hive FYP-I shared plan

Internal completion target: 15 January 2027. Feature integration target: 7 January; final week is for defects, documentation and rehearsal.

## Shared FYP-I finish line

By 15 January 2027, demonstrate a synthetic customer support request plus quote through intake, support/RAG, sales quote, scheduling proposal, explicit customer consent, authorized admin approval, controlled database execution, and a truthful combined response. A basic chat, approval screen and trace inspector must show the real backend journey. Complete reviewable report Chapters 1–4. Supervisor confirmation of the required 50% milestone is pending; do not label this plan officially approved.

The full five-screen dashboard, extensive benchmark/holdout evaluation, broader recovery/load coverage and final report Chapters 5–7 remain FYP-II work. Basic safety is mandatory for any FYP-I mutation: no approval bypass, no duplicate execution, no double-booking, no fake success. If those checks fail, keep that action proposal-only and report the incomplete milestone.

## Adaptability requirement

Read docs/BUSINESS_CONFIGURATION.md. Build against generic customer, catalog item, resource, quote, request and booking concepts. Validate two synthetic profiles without core-code changes; profile B disables booking. Use isolated fixture data and no named client. Configuration enables implemented capabilities only; unsupported actions require new adapters and tests.

## Independent development and integration

Agree contracts in Week 1. Use shared fixtures and replaceable adapters so a missing teammate module does not stop local work. Never implement a second authoritative pricing or approval engine. Mark mocked versus live behavior explicitly. A standalone test passing is not an integrated completion.

Session A builds a focused deliverable. Session B verifies it, reviews a teammate handoff, and updates progress/report evidence. If a dependency is late, use its agreed mock and continue the next independent task; record the pending live integration. Propose contract changes before changing consumers. Required supervisor meetings are separate from these work sessions.

Use Monday and Thursday as movable planning dates in Asia/Karachi, not recorded attendance. Reserve approximately 3–4 focused hours per session as an initial estimate, then re-estimate after Week 1. Early-December sessions are lighter pending the actual exam timetable. If effort exceeds capacity, reduce optional scope with supervisor agreement rather than claim completion.

## Ownership

| Owner | Scope |
|---|---|
| Wasam | Core backend, authentication foundation, conversations, orchestration and RAG |
| Arif | Pricing, validation, consent, approvals, controlled execution, audit and deployment |
| Asad | Frontend dashboard/simulator and read-only operations overview API |
| Shizza | Domain agents, reference data/read tools, seed fixtures and academic documentation coordination |

## Contracts and repository ownership

Wasam coordinates task/result/state contracts and conversation/auth tables. Arif owns proposal/quote/approval/receipt contracts and related mutation tables. Shizza owns customers/catalog items/service-status/resource reference tables, domain outputs and academic editing. Asad owns UI fixtures and overview response. All review contracts before implementation. Coordinate migration revision chains before merging.

Create shared sample payloads and tests in Week 1. Reusable fixtures are tracked; private instructions are not. Do not require personal instruction files to build the system. Every contributor supplies their own technical explanations, sources and evidence; Shizza consolidates the report and checks consistency rather than fabricating missing work.

## Weekly integration checkpoints

| Week | Dates | Shared checkpoint |
|---|---|---|
| W01 | 2026-10-26 / 2026-10-29 | Contracts and fixtures agreed |
| W02 | 2026-11-02 / 2026-11-05 | Backend skeleton, reference data, quote tests and screen contract |
| W03 | 2026-11-09 / 2026-11-12 | Conversation/read APIs, support worker and overview standalone |
| W04 | 2026-11-16 / 2026-11-19 | RAG, sales proposals and versioned approval records |
| W05 | 2026-11-23 / 2026-11-26 | Independent routing, scheduling proposals and denial tests |
| W06 | 2026-11-30 / 2026-12-03 | Light mids work: review documented interfaces |
| W07 | 2026-12-07 / 2026-12-10 | Light mids work: refine documentation and failure scenarios |
| W08 | 2026-12-14 / 2026-12-17 | Real workers/data/RAG connect; executor tested separately |
| W09 | 2026-12-21 / 2026-12-24 | Consent/approval/resumption connect; frontend API fixtures verified |
| W10 | 2026-12-28 / 2026-12-31 | Real API journey and deployment work; frontend foundation connects |
| W11 | 2027-01-04 / 2027-01-07 | Real frontend journey, safety checks and feature freeze |
| W12 | 2027-01-11 / 2027-01-14 | Clean setup, report review, failure demo and final rehearsal |

## Acceptance on 15 January

- A real seeded complaint-plus-quote request traverses the connected backend and UI.
- Price/availability come from stored data; support findings reference source evidence.
- Consent and approval are separate; rejected/expired/stale proposals cannot execute.
- A repeated execution request causes one mutation; competing slots cannot double-book.
- Conversation and pending approval survive a basic restart check.
- Chapters 1–4 are reviewable, with missing sources/estimates clearly flagged.
- Setup instructions work on another member's machine; actual test evidence is linked.
- Supervisor scope acceptance and official submission dates are recorded if received; otherwise remain pending.

## Contingency

If behind, first defer optional UI polish, extensive language coverage and nonessential analytics. Do not remove authorization, quote validation or duplicate prevention to hit a date. At each Thursday review, estimate remaining work and propose a scope adjustment if necessary. Record official feedback and update all affected schedules together. January 15 is an internal target, not a university submission date.
