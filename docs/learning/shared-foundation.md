# Shared foundation learning note

Imported and checked on 2026-10-30 (Asia/Karachi). Team review is pending; see ../PROJECT_ORIGIN.md for background.

The first batch validates configuration and defines SQL records; it does not start the application or execute customer actions. The shared migration stays together because its foreign keys link all owners' records. Splitting that migration into four independent histories would create avoidable conflicts. The pinned requirements describe the delivered prototype; later modules use the same environment.

| Function or group | Inputs, outputs and effects | Choice and alternative | Check |
|---|---|---|---|
| Policy, Adapters, Profile.check_profile | JSON fields become validated models; rejects unknown capabilities/adapters and missing references | Pydantic rejects malformed input; unchecked dictionaries would defer errors | Valid A/B and invalid capability/reference/currency/policy cases |
| Profile.fingerprint | Profile content becomes a SHA-256 string; no write | Detects content changes; schema version alone misses policy edits | Changed discount changes fingerprint |
| Settings.from_env / profile | Environment and optional local .env become settings/profile; reads files | Explicit hosted credentials fail when missing; no fallback keys | Full application startup; focused batch tests cover profile loading |
| connect / configure | SQL URL returns engine and session factory; SQLite directory/PRAGMA side effects | Separate sessions prevent shared transactions; one global Session is unsafe | Foreign-key rejection and persisted run test |
| uid / now | Generate UUID and UTC timestamp values | Avoid central ID allocation and naive local timestamps | Model persistence test |
| Models and initial migration | Business/user/session, customer/catalog/slot, conversation/message/run/trace, proposal/decision/receipt/request/booking/ticket tables | Relational keys and unique constraints enforce relationships; JSON stores bounded workflow payloads, not all data | Migration upgrade/check and duplicate run rejection; receipt uniqueness inspection |
| API schemas | Validate request/intake objects with forbidden extra fields | Typed allowlist prevents arbitrary worker instructions becoming accepted fields | Unknown execute_sql rejected |
| profile_data and foundation tests | Synthetic profile and temporary SQLite state; assertions only | Real database constraints are checked without full app fixtures | pytest tests/unit/test_foundation.py |
| verify_batch.main | Batch ID and new external directory; exports HEAD, copies only exact files, runs checks, writes hashes/output | A clean archive avoids working-tree import leakage; ordinary pytest in the imported tree cannot prove batch isolation | B01 isolated execution recorded in docs/commits/verification.md |

Before committing, explain why a proposal table does not itself grant execution permission, why a changed profile needs renewed review, and why successful schema tests do not prove the future HTTP flow. No meaningful alternative is needed for empty package __init__ files.

Run `python scripts/verify_batch.py B01 <new-directory-outside-repository>` using the project Python environment. The helper never stages, commits or copies .env. Later batches deliberately remain gated until their prerequisites are committed and their tests are scoped to that committed base.

## Later focused service tests

`test_login_stores_only_hashed_session_and_rejects_wrong_password` uses a temporary real SQL database and synthetic account to check Argon2 login, hashed token persistence, failed credentials and denied admin authority. `test_authoritative_price_discount_and_disabled_booking` verifies a database price with Decimal arithmetic and rejects invalid quantity, discount, catalog and slot inputs; it also checks secret redaction. `test_sources_no_evidence_and_demo_intents` builds a real temporary lexical index and checks source identity, unrelated-query refusal and deterministic intake. `test_profile_b_seeding_is_repeatable_and_booking_is_denied` seeds twice, checks retained password/no slots, then runs the read workflow with booking disabled. These tests return no production data; they create only temporary synthetic files/records. Real isolated databases/indexes were preferred over mocks for these boundaries; hosted provider calls remain mocked in the imported suite. All four passed in the full-tree 49-test run. They are assigned to B02-B05, not B01; their clean batch runs remain pending.
