"""Profile B seed/workflow boundary without HTTP app or mutation executors."""

import asyncio

from sqlalchemy import func, select

from backend.config import ROOT, Settings
from backend.db.connection import connect
from backend.db.models import Base, Slot, User
from backend.agents.provider import Provider
from backend.agents.workflow import Workflow
from backend.rag.retriever import Retriever
from scripts.seed import seed


def test_profile_b_seeding_is_repeatable_and_booking_is_denied(tmp_path):
    settings = Settings(f"sqlite:///{tmp_path / 'b.db'}",
                        str(ROOT / "examples/business-profiles/profile-b.json"),
                        str(tmp_path / "index"), "demo", "http://localhost:3000",
                        False, "", "", "", "lexical", False)
    engine, factory = connect(settings.database_url)
    try:
        Base.metadata.create_all(engine)
        seed(settings, "synthetic-test-password")
        with factory() as db:
            original = db.scalar(select(User).where(User.role == "admin")).password_hash
        seed(settings, "different-test-password")
        with factory() as db:
            assert db.scalar(select(User).where(User.role == "admin")).password_hash == original
            assert db.scalar(select(func.count()).select_from(Slot)) == 0
        profile = settings.profile()
        workflow = Workflow(profile, Provider(settings),
                            Retriever(settings.chroma_path, profile), factory)
        result = asyncio.run(workflow.run({"content": "I need a quote and an appointment",
                                           "item_id": "demo-b-item-1"}, "en"))
        assert next(x for x in result["results"] if x["worker"] == "scheduling")["status"] == "denied"
        assert "USD 25.00" in next(x for x in result["results"] if x["worker"] == "sales")["summary"]
    finally:
        engine.dispose()
