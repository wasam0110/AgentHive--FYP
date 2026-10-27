# Wasam FYP-I progress

Owner: Wasam

Module: Core backend, authentication foundation, conversations, orchestration and RAG.

Target: 15 January 2027. This is a plan; no implementation or attendance is asserted.

Statuses: Not started → In progress → Standalone verified → Integration pending → Integrated and verified. Use Blocked with a reason when independent work is not possible. Document tasks may use Reviewed after an identified reviewer confirms them. Do not infer progress from dates.

| Session | Planned date | Deliverable | Status | Actual date | Evidence / PR / test | Dependency / next handoff |
|---|---|---|---|---|---|---|
| W01-A | 2026-10-26 | Define request/task/result schemas plus business-profile and capability contracts | In progress | 2026-10-27 | backend/schemas/contracts/ — business_profile.md, task_contracts.md, conversation_contracts.md, sample_payloads.json, README.md — branch: w01a-schema-contracts | Arif: confirm policy field names (W01-B). Shizza: confirm adapter/catalog/resource ref IDs (W01-B). Asad: confirm conversation status fields for Overview (W01-B). |
| W01-B | 2026-10-29 | Review shared sample payloads and first end-to-end scenario | Not started | — | — | Use shared contracts; record live handoff when applicable |
| W02-A | 2026-11-02 | Create FastAPI skeleton and typed profile validation with unknown-capability rejection | Not started | — | — | Use shared contracts; record live handoff when applicable |
| W02-B | 2026-11-05 | Add backend lint/tests and authenticated demo identity foundation | Not started | — | — | Use shared contracts; record live handoff when applicable |
| W03-A | 2026-11-09 | Implement conversation/message persistence | Not started | — | — | Use shared contracts; record live handoff when applicable |
| W03-B | 2026-11-12 | Verify history reload and denied cross-customer access | Not started | — | — | Use shared contracts; record live handoff when applicable |
| W04-A | 2026-11-16 | Build reviewed-document chunking and ingestion | Not started | — | — | Use shared contracts; record live handoff when applicable |
| W04-B | 2026-11-19 | Verify profile-scoped retrieval, source IDs and no-evidence behavior | Not started | — | — | Use shared contracts; record live handoff when applicable |
| W05-A | 2026-11-23 | Implement intake with structured intent output | Not started | — | — | Use shared contracts; record live handoff when applicable |
| W05-B | 2026-11-26 | Run supervisor with fake workers and dependency-aware routing | Not started | — | — | Use shared contracts; record live handoff when applicable |
| W06-A | 2026-11-30 | Review state schemas and Chapter 1 draft; light mids session | Not started | — | — | Use shared contracts; record live handoff when applicable |
| W06-B | 2026-12-03 | Document worker/RAG interfaces and test one invalid payload; light session | Not started | — | — | Use shared contracts; record live handoff when applicable |
| W07-A | 2026-12-07 | Review RAG evidence and failure cases; light mids session | Not started | — | — | Use shared contracts; record live handoff when applicable |
| W07-B | 2026-12-10 | Update architecture notes and fix a small test; light session | Not started | — | — | Use shared contracts; record live handoff when applicable |
| W08-A | 2026-12-14 | Connect domain workers through adapters | Not started | — | — | Use shared contracts; record live handoff when applicable |
| W08-B | 2026-12-17 | Verify support-plus-quote routing and independent task overlap | Not started | — | — | Use shared contracts; record live handoff when applicable |
| W09-A | 2026-12-21 | Persist customer/admin waiting states | Not started | — | — | Use shared contracts; record live handoff when applicable |
| W09-B | 2026-12-24 | Connect approval result and resume without losing completed tasks | Not started | — | — | Use shared contracts; record live handoff when applicable |
| W10-A | 2026-12-28 | Connect authorized execution receipts to final response | Not started | — | — | Use shared contracts; record live handoff when applicable |
| W10-B | 2026-12-31 | Run real backend journey and verify restart/duplicate-request behavior | Not started | — | — | Use shared contracts; record live handoff when applicable |
| W11-A | 2027-01-04 | Support frontend integration and fix contract defects | Not started | — | — | Use shared contracts; record live handoff when applicable |
| W11-B | 2027-01-07 | Freeze backend scope; verify same core with Profiles A/B and disabled booking | Not started | — | — | Use shared contracts; record live handoff when applicable |
| W12-A | 2027-01-11 | Run fresh-setup integration and finalize Chapter 1 material | Not started | — | — | Use shared contracts; record live handoff when applicable |
| W12-B | 2027-01-14 | Rehearse explanation of graph/RAG; fix only release-blocking defects | Not started | — | — | Use shared contracts; record live handoff when applicable |

## Session evidence log

Append entries rather than overwriting prior evidence:

### W01-A — 2026-10-27

- Session and actual date: W01-A — 2026-10-27
- Implemented or reviewed: Defined BusinessProfile + capability registry contract, IntakeOutput/TaskDefinition/WorkerResult/ActionProposal/TaskStatus contracts, ConversationRecord/MessageRecord/RunRecord contracts, shared sample payloads JSON.
- Files / commit / PR: backend/schemas/contracts/README.md, business_profile.md, task_contracts.md, conversation_contracts.md, sample_payloads.json — docs/learning/schema-contracts.md — docs/planning/gantt-plan.csv (Wasam-W04-B fix) — docs/planning/decision-log.md (new row) — branch w01a-schema-contracts
- Commands run and observed results: Design-only session. No runtime commands claimed. CI hygiene checks run before commit (git ls-files and git diff --cached --check).
- Mocked dependencies versus real integrations: ALL integrations are mocked at this stage. Arif's quote service (unit_price, total, expiry) → placeholder strings in sample_payloads.json. Shizza's worker implementations → agreed WorkerResult shape not yet built. Asad's UI → agreed ConversationRecord/TaskStatusRecord field names; no screen built yet.
- What I can explain: The five contract shapes and why each field exists, the dependency rules table, why amounts use Decimal strings, why capabilities are code-registered not profile-defined, why customer_id is never trusted from a message body.
- Report sections updated: None this session (design output only; Shizza will pull technical facts into Ch. 4 after review).
- Blocker, owner and next action: No blocker. Pending teammate confirmation of open points listed in each contract file. Next: W01-B (2026-10-29) — review shared sample payloads and first end-to-end scenario with team.
- Reviewer and review date, if actually reviewed: Pending

## Final handoff

- Standalone verification: Not started.
- Live integration verification: Not started.
- Documentation reviewed: Not started.
- Known limitations: Not yet assessed.
