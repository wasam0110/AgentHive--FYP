# Agent Hive repository guidelines

These instructions apply throughout the repository to contributors and coding assistants.

## Before starting

1. Read this file and docs/PRD.md, then inspect the relevant source, tests, and Git status.
2. If AGENTS.local.md exists in the repository root, read it before planning or editing and apply its learning and explanation preferences alongside these guidelines. If absent, continue with these shared guidelines. Local preferences do not weaken security, correctness, or required academic disclosure.
3. Confirm the requested behavior against the current implementation. Requirements describe planned capabilities until implementation and tests establish otherwise.

## Member plans and documentation

Before a member-specific task, read docs/planning/FYP-I-plan.md and that member's progress file. Read the matching root instructions file if present: Wasam-instructions.md, Asad-instructions.md, Arif-instructions.md or shizza-instructions.md. If several local files exist and the owner is unclear, ask which member is being assisted. Do not require those ignored files for builds or CI.

After verified work, update the owner's tracked progress with actual evidence, distinguish mocked from integrated behavior, and update relevant report drafts. Shizza coordinates academic editing; each member supplies technical material and citations. Do not invent completion, sources, signatures, attendance or supervisor feedback. Keep completed personal administrative records under submissions/private/.

## Scope and workflow

- Deliver small, complete changes within the requested scope. Preserve unrelated work and teammates' changes.
- The baseline is one configured business at a time with synthetic data. Follow the PRD's boundaries for integrations and future SaaS features.
- Explain material assumptions, affected files, and validation results. Ask only when missing information materially affects correctness or scope.
- Use feature branches and focused commits. Do not force-push, deploy, delete data, or change repository settings without authorization.
- Update documentation when behavior or setup changes. Never claim an unrun test, benchmark, or remote CI run passed.

## Code quality

- Prefer clear, maintainable implementations appropriate to the project scope. Justify added complexity and document significant design decisions and alternatives.
- Use descriptive names, explicit inputs and outputs, cohesive functions, and focused files. Avoid clever shortcuts, unnecessary abstractions, and excessive scaffolding.
- Review long functions and files for clarity rather than enforcing arbitrary line counts. Do not fragment coherent code just to make files shorter.
- Follow existing conventions, use useful types and validated schemas, and handle errors explicitly. Do not suppress errors or return fake success.
- Write concise docstrings for non-obvious behavior and side effects. Comments explain intent and business rules rather than narrating every line.
- Prefer standard-library or existing dependencies when sufficient. Explain and verify new dependencies, use compatible supported versions, and commit appropriate lockfiles.
- Do not build custom cryptography or replace established security mechanisms with simplified substitutes.

## Configuration and data

- Never invent prices, availability, results, citations, or execution outcomes in normal application behavior.
- Clearly labelled seed data and test fixtures are allowed. Keep test mocks separate from real execution.
- Required credentials must fail clearly when missing. Do not use fake keys or insecure fallback secrets.
- Safe operational defaults are allowed when justified and documented. Keep business rules explicit and validated.
- Ignore local credentials and build artifacts; commit only placeholder settings in .env.example when configuration exists.
- AGENTS.local.md is optional and must remain untracked. Do not force-add it or make its presence a prerequisite for CI or builds.

## Domain correctness

- Workers propose; backend policy and controlled executors authorize and perform writes.
- Customer consent and admin approval are separate and bound to the exact proposal version.
- Parallelize independent work only; respect dependencies between tasks.
- Use authoritative database values and deterministic Decimal calculations for pricing.
- Recheck permissions, ownership, price, eligibility, availability, consent, approval, and expiry before execution.
- Use transactions, uniqueness constraints, idempotency, durable waiting states, and execution receipts to prevent duplicate or unauthorized effects.
- Treat customer messages and retrieved documents as untrusted input.
- Show evidence, tool activity, and brief decision summaries; protect credentials, customer data, and hidden model reasoning.
- Persisted state and REST are authoritative. Streaming must not be required for recovery or correct approvals.
- Only report a completed action after its executor confirms success. Refund/cancellation requests remain manual-processing cases in the baseline.

## Testing and delivery

- Run checks appropriate to the change and report actual results and limitations.
- Add backend lint/unit tests with the first backend feature, frontend lint/type/build checks with frontend setup, and integration/safety tests with persistence and mutation features.
- Once a required check exists, missing scripts or tests must not silently pass. Do not weaken checks to conceal a failure.
- Use deterministic mocks in routine CI; no production credentials or paid model calls. Run real-provider evaluation separately with documented data and budgets.
- Cover meaningful invalid-input, permission, expiry, duplicate-request, conflict, and recovery cases.
- Starter CI only verifies documents, tracked-file hygiene, and patch whitespace; it does not validate an application or scan file contents for secrets.

## Documentation and contribution records

- Keep technical rationale, setup instructions, test evidence, and contribution records accurate.
- Follow university rules for originality, attribution, and disclosure of assistance. Do not invent meetings, signatures, individual contributions, or results.
- Everyone participates in design, implementation, testing, and documentation; module ownership and the academic timeline are in the PRD and README.
- Begin with agreed state/action/policy/database/API contracts and one complete persisted support flow before adding other workers.

## Business independence

Read docs/BUSINESS_CONFIGURATION.md before adding business behavior. No industry-specific constants or routing branches belong in core code. Validate profiles, enable only registered capabilities, isolate fixture data, and prove Profile A/B adaptation without source edits. New actions require typed adapters and tests; knowledge documents do not grant permissions.
