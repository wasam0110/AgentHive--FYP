"""Real lexical retrieval with synthetic documents, without application startup."""

from backend.config import ROOT, Profile
from backend.rag.retriever import Retriever
from backend.agents.provider import demo_intake


def test_sources_no_evidence_and_demo_intents(tmp_path):
    profile = Profile.model_validate_json(
        (ROOT / "examples/business-profiles/profile-a.json").read_text(encoding="utf-8")
    )
    documents = tmp_path / "documents"
    documents.mkdir()
    (documents / "support.md").write_text("Synthetic support complaint guidance.", encoding="utf-8")
    retriever = Retriever(str(tmp_path / "index"), profile)
    assert retriever.ingest(documents) == 1
    results = retriever.search("support complaint")
    assert results and results[0]["source_id"] == "support:0"
    assert retriever.search("zzxyqzvxyz") == []
    intents = demo_intake("I need help and a quote")
    assert intents.support and intents.sales
