# Business configuration contract

Profile validation is implemented in `backend/config.py`; the standalone seed-fixture contract is implemented in `scripts/seed_fixtures.py`. Database seeding, read adapters, and workflow wiring remain pending. Agent Hive uses a reusable core plus validated profiles and allowlisted adapters. No industry or named client is assumed.

## Proposed fields

| Field | Meaning / validation |
|---|---|
| schema_version | Supported version; reject unknown versions |
| business_id | Stable server-selected identifier, not supplied by a customer message |
| display_name | Configurable business name |
| timezone / currency | Validate supported identifiers; never silently convert amounts |
| languages | Explicitly supported response languages |
| terminology | User-facing labels; cannot change permissions |
| capabilities | Subset of code-registered capabilities |
| adapters | IDs from a static registry, not paths to arbitrary code |
| knowledge_source / catalog / resources | References resolved by permitted adapters |
| policy | Explicit discount cap, quote and approval expiry; typed values with units |

## Policy and approval matrix

The active profile supplies policy values; it does not grant permissions by itself.
The backend policy gate must apply these checks in order before an action can execute:

| Action state or input | Required condition | Result when the condition is false |
|---|---|---|
| Quote creation | Catalog item exists, is active, and uses the profile currency | Reject the proposal |
| Discount | `0 <= discount_pct <= policy.max_discount_pct` | Reject the proposal |
| Customer confirmation | Customer confirms the exact `proposal_id` and `proposal_version` before `quote_expiry_minutes` elapses | Keep the action awaiting consent |
| Administrator approval | An authorized administrator approves the same proposal version after customer confirmation and before `approval_expiry_hours` elapses | Keep the action awaiting approval or reject it |
| Revalidation | Current profile fingerprint, price, eligibility, availability and expiry match the proposal | Require a new proposal version and new consent |
| Execution | All preceding checks pass and the idempotency key has no committed receipt | Allow one controlled mutation |

Customer consent and administrator approval are separate decisions. Neither an LLM
response, silence, or a stale decision can substitute for either decision. A policy or
profile change changes the fingerprint used for revalidation; it must not rewrite older
records or retroactively make an approval valid.

## Boundaries

Business profile configuration changes supported behavior within implemented capabilities. A new integration or action requires a typed adapter, tests, authorization checks and deployment approval. RAG documents cannot grant tools or override policy. Configuration is not a programming language.

Keep customer, conversation, proposal and receipt identity stable. Pin profile/policy versions on proposals. Changing business identity requires a separate isolated deployment/test environment, not relabelling existing records. Profile changes are an administrator maintenance task in FYP-I; no live profile editor is required.

## First two synthetic fixtures

`examples/business-profiles/profile-a.json` enables support, quote, and booking; `profile-b.json` enables support and quote, with booking disabled. They intentionally use different policy values and currencies. `scripts/seed_fixtures.py` maps only the registered knowledge references to `examples/seed-fixtures/demo-a.json` and `demo-b.json`, validates their catalog/resource references, and rejects unknown references before a seeding caller can write records. The fixtures contain fictional sample customers and catalog entries, not credentials or client data.

This standalone contract does not create database rows, ingest knowledge documents, or provide read adapters. Those remain part of the dependency-gated seed/read workflow. Full acceptance still requires isolated A/B seeding, catalog/evidence identity, locale/branding, discount enforcement, disabled-tool behavior, and proposal profile-version checks.

## Ownership

Wasam: typed profile loading, capability registry, orchestration and RAG namespaces. Shizza: generic data/read adapters, synthetic catalogs/articles and reusable workers. Arif: policy validation, deterministic quotes, execution adapter and deployment selection. Asad: configured UI labels, currency/time display and hiding unavailable controls while handling backend denial.
