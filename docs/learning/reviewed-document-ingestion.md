# Reviewed-document ingestion

Week 4 ingestion removes optional document front matter before chunking and stores the document metadata with every chunk. A reviewed document can declare `language`, `review_date`, `audience` and `review_status: reviewed`; reviewed documents must include an ISO review date. Documents without front matter remain usable for the existing demo index but are explicitly marked `unreviewed` rather than being presented as reviewed.

`chunk_text` uses fixed character offsets and bounded chunks, so rebuilding an index produces stable chunk IDs such as `support:0`. `Retriever` keeps one Chroma collection per business profile and embedding mode, preventing profile A evidence from being returned for profile B. Search still returns an empty list for unrelated queries instead of inventing evidence.

Verification:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/unit/test_retrieval_service.py tests/test_profiles_rag.py
ruff check backend/rag/retriever.py tests/unit/test_retrieval_service.py tests/test_profiles_rag.py
```

The focused Week 4 checks cover reviewed metadata, stable source IDs, profile namespaces and no-evidence behavior.
