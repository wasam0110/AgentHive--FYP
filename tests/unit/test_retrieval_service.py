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


def test_reviewed_document_metadata_and_profile_namespace(tmp_path):
    profile_a = Profile.model_validate_json(
        (ROOT / "examples/business-profiles/profile-a.json").read_text(encoding="utf-8")
    )
    profile_b = Profile.model_validate_json(
        (ROOT / "examples/business-profiles/profile-b.json").read_text(encoding="utf-8")
    )
    documents_a = tmp_path / "documents-a"
    documents_b = tmp_path / "documents-b"
    documents_a.mkdir()
    documents_b.mkdir()
    front_matter = (
        "---\n"
        "language: en\n"
        "review_date: 2026-11-17\n"
        "audience: customer\n"
        "review_status: reviewed\n"
        "---\n"
    )
    (documents_a / "support.md").write_text(
        front_matter + "Reviewed support guidance for profile A.", encoding="utf-8"
    )
    (documents_b / "support.md").write_text(
        "Different business guidance only.", encoding="utf-8"
    )
    retriever_a = Retriever(str(tmp_path / "index"), profile_a)
    retriever_b = Retriever(str(tmp_path / "index"), profile_b)
    assert retriever_a.ingest(documents_a) == 1
    assert retriever_b.ingest(documents_b) == 1

    result = retriever_a.search("reviewed support guidance")
    assert result[0]["source_id"] == "support:0"
    assert result[0]["source"] == "support.md"
    assert result[0]["score"] > 0
    metadata = retriever_a.collection.get()["metadatas"][0]
    assert metadata["language"] == "en"
    assert metadata["review_date"] == "2026-11-17"
    assert metadata["audience"] == "customer"
    assert metadata["review_status"] == "reviewed"
    assert retriever_b.search("reviewed profile A") == []
