# Agent Hive

Agent Hive is an independent, configurable multi-agent customer-operations platform developed as an FYP at DHA Suffa University. The proposed system coordinates support, sales and resource scheduling, with evidence-backed responses, customer consent and backend-enforced human approval.

**Status: planning and repository setup. Application features are not implemented or tested yet.**

## Start here

- [Product requirements](docs/PRD.md)
- [Shared FYP-I plan and role allocation](docs/planning/FYP-I-plan.md)
- [Repository guidelines](AGENTS.md)
- [CI guide](docs/CI.md)
- [University formats and submission workflow](docs/university/README.md)
- [Submission checklist](docs/planning/submission-checklist.md)

## Responsibilities

| Owner | Modules |
|---|---|
| Wasam | Core backend/auth, conversations, RAG, intake and supervisor |
| Arif | Pricing, validation, consent/approval, safe execution, audit and deployment |
| Shizza | Domain agents, business reference data/read tools, seed data and academic coordination |
| Asad | Frontend, frontend testing/integration and read-only overview API |

Everyone designs, implements, tests and documents their own work. Shizza consolidates academic documents using evidence supplied by all members.

## Planned capabilities

Multiple intents per conversation; support retrieval with source evidence; deterministic quotes; appointment proposals; distinct customer consent/admin approval; controlled database changes; persisted traces and waiting state; a basic connected demo interface. Final A/B/C research evaluation and the complete dashboard remain full-release goals.

The demonstration uses synthetic data. It does not charge real customers, control external business systems or process actual refunds. See the PRD for full scope, safety requirements and acceptance tests.

## Progress

- [Wasam](Wasam-progress.md)
- [Arif](Arif-progress.md)
- [Shizza](shizza-progress.md)
- [Asad](Asad-progress.md)

All 24 planned sessions per person begin as Not started. Monday/Thursday dates are planning slots, not attendance. Use fixtures for independent development and record real integration separately.

## Timeline

Start 26 October 2026; lighter early-December sessions during mids; core integration target 7 January 2027; internal completion target 15 January. FYP-I finals are expected in the first week of February, with a two-week break. FYP-II starts in early March, with finals in early July. Confirm exact official submission/presentation dates and the supervisor's 50% milestone.

## Setup

```bash
git clone https://github.com/wasam0110/AgentHive--FYP.git
cd AgentHive--FYP
```

Agree shared schemas, fixtures and policy boundaries first. Application install/run commands will be documented when their implementations exist. Planned stack: Python/FastAPI, LangGraph, PostgreSQL, ChromaDB, Next.js/TypeScript and Docker Compose; compatible versions will be pinned at implementation time.

## CI

The initial workflow checks required starter documents, tracked-file hygiene and patch whitespace. It neither runs application tests nor scans file contents for secrets. Add meaningful backend, frontend and integration checks with the corresponding code. A local validation does not establish a passed GitHub Actions run.

## University documents

Report drafts/scaffolds are under docs/report. Original DOCX, XLSX and PDF formats are preserved under docs/university/originals. The dated Gantt task source is docs/planning/gantt-plan.csv; transfer/review it in the supplied workbook before submission. Markdown is working source, not a signed or formatted official submission.

## Contributions

Follow AGENTS.md, use a feature branch and make small reviewed changes. Record actual commands/results and update the relevant report section. Preserve accurate attribution and follow university disclosure requirements.

## Business adaptability

The core is not tied to an industry or named client. Configure knowledge sources, catalogs, resources, terminology and policies; use registered adapters for actions. New integrations require implementation and tests, not just document upload. One business per deployment is the initial operating model, not multi-tenant SaaS.

Read [the business configuration contract](docs/BUSINESS_CONFIGURATION.md). Two JSON design fixtures under examples/business-profiles define an adaptation smoke test; they are not runnable application configuration yet. FYP-I must demonstrate that both profiles work against the same core and that disabled capabilities are enforced by the backend.
