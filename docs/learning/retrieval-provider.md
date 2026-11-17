# Retrieval and provider foundation

The B04 foundation keeps knowledge retrieval and model access behind explicit, testable boundaries. `Retriever` stores deterministic lexical or optional semantic embeddings, preserves source IDs and document hashes, and returns no evidence when a query has no meaningful shared token. `demo_intake` provides deterministic offline intent extraction, while `Provider` uses the hosted model only in hosted mode and raises an explicit error after bounded transient retries instead of returning fake success.

The lexical path is the default because it is deterministic and requires no paid provider call. Semantic embeddings remain an explicit alternative for environments that support them. The provider boundary is separate from retrieval so the application can test source evidence and offline behavior without network access.

Verification:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/unit/test_retrieval_service.py
ruff check backend/agents backend/rag tests/unit/test_retrieval_service.py
```

Both checks passed for the B04 candidate on 2026-11-16. These checks do not prove the B05 read workflow or B06 conversation integration.
