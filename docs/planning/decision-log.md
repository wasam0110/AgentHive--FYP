# Decision log

| Date | Decision | Basis / status | Affected work |
|---|---|---|---|
| 2026-10-25 | Use revised four-member allocation | User agreed; academic supervisor approval pending | All owner plans |
| 2026-10-25 | Internal completion target 2027-01-15 | User requested; not an official submission date | FYP-I schedule |
| 2026-10-25 | Build frontend after backend contracts; design earlier | User requested | Asad schedule |

Append future decisions with their actual source and date. Do not invent supervisor endorsement.

| 2026-10-25 | Business-independent core with configuration/adapters; no named industry/client | User requested; supersedes domain-specific scope | PRD v2, all schedules, fixtures and report drafts |
| 2026-10-26 | Schema contracts v1.0 agreed: BusinessProfile, IntakeOutput, TaskDefinition, WorkerResult, ActionProposal, ConversationRecord, MessageRecord, RunRecord. Capability IDs are code-registered; profiles select from a static list. Amounts use Decimal strings. customer_id always server-validated, never from message body. | Wasam design session W01-A; pending teammate confirmation in W01-B. No supervisor endorsement. | backend/schemas/contracts/ |
