# Business Profile and Capability Registry Contract

Version: 1.0 — draft W01-A (2026-10-26)
Owner: Wasam (profile loading, capability registry, orchestration namespaces)
Consumers: Arif (policy values), Shizza (adapter IDs, catalog/resource references), Asad (display fields)

This document describes the validated in-memory BusinessProfile object that the backend
loads at startup from a JSON file. It is NOT the raw JSON file itself — the profile loader
(W02-A) validates the raw JSON and produces this object. Invalid profiles fail startup with
a clear error.

## Registered capabilities (code-registered, static list)

The following capability identifiers are the complete allowed set. A profile may enable any
subset. Any string not in this list is an unknown capability and causes startup failure.

| Capability ID | Description | Required adapter type |
|---|---|---|
| knowledge_answer | Retrieve guidance from the reviewed knowledge base | data |
| catalog_quote | Look up catalog items and request a deterministic quote | data |
| resource_booking | Retrieve availability and propose a booking slot | data |

Adding a new capability requires: a new adapter type + implementation + tests.
It cannot be done by adding a string to a profile JSON.

## Validated BusinessProfile fields

```python
# Pseudocode typed definition — not runnable yet (W02-A builds the Pydantic model)

class PolicyConfig:
    max_discount_pct: int          # 0–100; hard cap for the profile
    quote_expiry_minutes: int      # > 0
    approval_expiry_hours: int     # > 0

class AdapterConfig:
    data: str                      # must be a registered adapter ID (e.g. "sandbox_v1")
    execution: str                 # must be a registered adapter ID

class BusinessProfile:
    schema_version: int            # must equal SUPPORTED_SCHEMA_VERSION (currently 1)
    business_id: str               # set server-side; validated to match the loaded file
    display_name: str              # non-empty
    timezone: str                  # validated IANA timezone string
    currency: str                  # validated ISO 4217 code
    languages: list[str]           # non-empty; each a supported language code
    terminology: dict[str, str]    # optional labels; cannot change permissions
    capabilities: list[str]        # subset of REGISTERED_CAPABILITIES; non-empty
    adapters: AdapterConfig        # all referenced adapter IDs must be registered
    knowledge_source: str | None   # required when knowledge_answer is enabled
    catalog: str | None            # required when catalog_quote is enabled
    resources: str | None          # required when resource_booking is enabled; None is valid when booking is disabled
    policy: PolicyConfig
```

## Validation rules

| Rule | Failure | Checked by |
|---|---|---|
| schema_version == 1 | Startup error: unsupported schema version | Loader (W02-A) |
| Every capability in a registered set | Startup error: unknown capability `<id>` | Loader (W02-A) |
| knowledge_source present if knowledge_answer enabled | Startup error: knowledge_source required | Loader (W02-A) |
| catalog present if catalog_quote enabled | Startup error: catalog required | Loader (W02-A) |
| resources present if resource_booking enabled | Startup error: resources required | Loader (W02-A) |
| All adapter IDs in a registered set | Startup error: unknown adapter `<id>` | Loader (W02-A) |
| timezone is a valid IANA identifier | Startup error: invalid timezone | Loader (W02-A) |
| currency is a valid ISO 4217 code | Startup error: invalid currency | Loader (W02-A) |
| profile JSON does not contain executable code, SQL, URLs, module paths | Startup error: forbidden field content | Loader (W02-A) |

## Profile A / Profile B smoke test expectation

Run the same loader against both `examples/business-profiles/profile-a.json`
and `examples/business-profiles/profile-b.json` with no core-code changes.

| Check | Profile A (demo-a) | Profile B (demo-b) |
|---|---|---|
| Capabilities | knowledge_answer, catalog_quote, resource_booking | knowledge_answer, catalog_quote |
| resource_booking routed | Yes | Rejected — capability not enabled |
| Currency | PKR | USD |
| max_discount_pct | 5 | 0 |
| quote_expiry_minutes | 30 | 15 |

Profile B must raise a controlled error when the resource_booking tool is requested,
without calling any booking adapter.

## Adapter IDs registered for W01

| ID | Purpose |
|---|---|
| sandbox_v1 | Reads synthetic fixture data; records simulated mutations in the project DB |

A new adapter ID requires a typed adapter class + tests before it can be registered.
Credentials are separate environment variables, never embedded in a profile.

## Open points for teammates

- **Arif:** Please confirm the policy field names (`max_discount_pct`, `quote_expiry_minutes`,
  `approval_expiry_hours`) match what your quote/approval service will read. Raise in W01-B.
- **Shizza:** Please confirm `knowledge_source`, `catalog`, and `resources` reference IDs
  match what your data adapter will resolve. Raise in W01-B.
- **Asad:** `display_name`, `currency`, `timezone`, and `terminology` are the display fields
  your UI consumes. Confirm these are sufficient for the labels you need.
