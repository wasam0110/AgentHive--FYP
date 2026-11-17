# Persisted conversation integration

The B06 API stores conversations, messages and workflow runs before processing. A run is claimed with a database lease, and its request key/hash makes retries idempotent. The worker records traces and system messages, while proposal confirmation and administrator approval remain separate backend transitions. Ownership checks use the authenticated business and customer context rather than trusting IDs supplied by the client.

The integration also keeps profile behavior explicit: the ISP fixture is registered by key, and disabled capabilities produce denial rather than silently creating data. The complete approval service is used because the HTTP routes need consent, approval, refresh, replay and receipt behavior; a validation-only helper cannot authorize execution.

Verification:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/test_approvals.py tests/test_auth.py tests/test_profiles_rag.py tests/test_provider.py tests/test_workflow.py tests/test_reference_offers.py tests/test_service_context.py tests/unit/test_retrieval_service.py tests/unit/test_seed_workflow.py
```

Result on 2026-11-16: 49 passed. Ruff also passed for the exact integration paths. Provider calls were demo/mocked only.
