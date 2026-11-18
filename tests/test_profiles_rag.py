import asyncio
import json
from dataclasses import replace
import pytest
from pydantic import ValidationError
from backend.config import Profile, ROOT
from backend.agents.provider import Provider, demo_intake
from backend.agents.workflow import Workflow
from backend.db.connection import connect
from backend.db.models import Base
from backend.rag.retriever import Retriever
from backend.services.redaction import redact
from scripts.seed import seed


class FakeRetriever:
    def __init__(self, refs):
        self.refs = refs

    def search(self, _query):
        return [dict(ref) for ref in self.refs]


def run_support(env, retriever):
    workflow = Workflow(env.profile, Provider(env.settings), retriever, env.factory)
    state = {
        "content": "My connection is not working",
        "_customer_id": f"{env.profile.business_id}-customer-1",
    }
    result = asyncio.run(workflow.run(state, "en"))
    return next(item for item in result["results"] if item["worker"] == "support")


def test_profile_unknown_capability_and_missing_reference_rejected(env):
    data = env.profile.model_dump()
    data["capabilities"] = ["run_arbitrary_sql"]
    with pytest.raises(ValidationError):
        Profile.model_validate(data)
    data = env.profile.model_dump()
    data["catalog"] = None
    with pytest.raises(ValidationError):
        Profile.model_validate(data)


def test_invalid_fixture_reference_fails_before_seed(env, tmp_path):
    data = env.profile.model_dump()
    data["catalog"] = "unknown"
    path = tmp_path / "invalid.json"
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="references"):
        seed(replace(env.settings, profile_path=str(path)), env.password)


def test_profile_b_disables_booking_without_core_edits(env, tmp_path):
    settings = replace(
        env.settings,
        database_url=f"sqlite:///{tmp_path}/b.db",
        profile_path=str(ROOT / "examples/business-profiles/profile-b.json"),
    )
    engine, factory = connect(settings.database_url)
    Base.metadata.create_all(engine)
    seed(settings, env.password)
    profile = settings.profile()
    workflow = Workflow(profile, Provider(settings), Retriever(settings.chroma_path, profile), factory)
    result = asyncio.run(
        workflow.run({"content": "I need a quote and an appointment", "item_id": "demo-b-item-1"}, "en")
    )
    assert profile.currency == "USD" and profile.policy.max_discount_pct == 0
    assert next(r for r in result["results"] if r["worker"] == "scheduling")["status"] == "denied"
    assert "USD 25.00" in next(r for r in result["results"] if r["worker"] == "sales")["summary"]
    engine.dispose()


@pytest.mark.parametrize(
    "text,language",
    [
        ("I need help and a quote", "en"),
        ("Mujhe madad chahiye aur qeemat batayein", "roman-ur"),
        ("مجھے مدد اور قیمت چاہیے", "ur"),
    ],
)
def test_defined_multilingual_intents(text, language):
    result = demo_intake(text)
    assert result.support and result.sales and result.language == language


def test_retrieval_keeps_sources_and_returns_no_unrelated_evidence(env):
    refs = env.app.state.retriever.search("help complaint support")
    assert refs and all(ref["source_id"] and ref["excerpt"] for ref in refs)
    assert env.app.state.retriever.search("zzxyqzvxyz") == []


def test_support_worker_cites_fake_retrieval_evidence(env):
    evidence = {
        "source_type": "rag_chunk",
        "source_id": "support-fixture:0",
        "excerpt": "Synthetic guidance: restart the device before retrying.",
    }

    result = run_support(env, FakeRetriever([evidence]))

    assert result["status"] == "completed"
    assert evidence in result["evidence"]
    assert "Synthetic guidance: restart the device before retrying." in result["summary"]
    assert "Sources: support-fixture:0" in result["summary"]


def test_support_worker_escalates_when_retrieval_has_no_guidance(env):
    result = run_support(env, FakeRetriever([]))

    assert result["status"] == "completed"
    assert result["evidence"] == []
    assert "I could not find supporting guidance." in result["summary"]
    assert "an operator can help." in result["summary"]


def test_trace_redaction_preserves_nonsecret_evidence():
    clean = redact(
        {"token": "abc", "text": "api_key=abcdef person@example.test Bearer xyz", "source_id": "quotes:0"}
    )
    assert clean["token"] == "[redacted]"
    assert (
        "abcdef" not in clean["text"] and "example.test" not in clean["text"] and "xyz" not in clean["text"]
    )
    assert clean["source_id"] == "quotes:0"


def test_seed_adds_future_days_without_duplicate_overlapping_slots(env, monkeypatch):
    from datetime import datetime, timedelta
    from importlib import import_module
    from sqlalchemy import select, func
    from backend.db.models import Slot, User

    module = import_module("scripts.seed")
    with env.factory() as db:
        original_hash = db.scalar(select(User).where(User.role == "admin")).password_hash
        assert db.scalar(select(func.count()).select_from(Slot)) == 8

    class Tomorrow(datetime):
        @classmethod
        def now(cls, tz=None):
            return datetime.now(tz) + timedelta(days=1)

    monkeypatch.setattr(module, "datetime", Tomorrow)
    seed(env.settings, env.password)
    with env.factory() as db:
        assert db.scalar(select(func.count()).select_from(Slot)) == 10
        assert db.scalar(select(User).where(User.role == "admin")).password_hash == original_hash
