# Business configuration contract

Draft specification, not an implemented loader. Agent Hive uses a reusable core plus validated profiles and allowlisted adapters. No industry or named client is assumed.

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

examples/business-profiles/profile-a.json enables support, quote and booking. profile-b.json enables support and quote; booking must fail as unsupported. They intentionally use different policy values and currency. Each fixture references its own synthetic catalog and knowledge fixture to be created during implementation. Missing referenced data must fail setup clearly. No fixtures contain credentials or real client data.

Acceptance: configure each separately without editing core code; verify catalog/evidence identity, locale/branding, discount enforcement, disabled tools, invalid-profile rejection and profile version on proposals. These examples are not runnable until the loader and adapters exist.

## Ownership

Wasam: typed profile loading, capability registry, orchestration and RAG namespaces. Shizza: generic data/read adapters, synthetic catalogs/articles and reusable workers. Arif: policy validation, deterministic quotes, execution adapter and deployment selection. Asad: configured UI labels, currency/time display and hiding unavailable controls while handling backend denial.
