"""Sourced information must never become an executable monthly purchase."""
import asyncio
from dataclasses import replace
from decimal import Decimal
import json

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy import func, select
from backend.config import ROOT, Profile
from backend.db.models import CatalogItem, Proposal, Slot, User
from backend.services import reference_offers
from backend.services.jobs import process_one
from backend.services.quotes import quote
from scripts.seed import seed
from conftest import new_conversation, send




def test_reference_data_is_sourced_and_not_available_to_other_profiles(env, isp):
    assert env.client.get("/api/v1/reference-offers").status_code == 404
    with TestClient(isp.app) as anonymous:
        assert anonymous.get("/api/v1/reference-offers").status_code == 401
    response = isp.client.get("/api/v1/reference-offers")
    assert response.status_code == 200
    data = response.json()
    assert len(data["offers"]) == 47
    assert data["source_date"] == "2026-10-31" and data["checked_on"] == "2026-11-04"
    assert data["provider"] == "StormFiber" and "Not approved Alpha Max" in data["notice"]
    assert all(o["source_page"] in (1, 2) for o in data["offers"])
    blizzard = next(o for o in data["offers"] if o["name"] == "Blizzard")
    assert blizzard["base_speed_mbps"] == 30 and blizzard["bonus_speed_mbps"] == 10
    assert Decimal(blizzard["total"]) == Decimal("5028.00")
    promo = next(o for o in data["offers"] if o["name"] == "Triple Blitz Promo 2.0")
    assert promo["total"] == "17326.00" and promo["ongoing_monthly"] == "16777.00"
    assert "discrepancy" in promo["notes"]


def test_isp_seed_is_repeatable_and_does_not_mix_businesses(env, isp):
    with isp.factory() as db:
        original = db.scalar(select(User).where(User.role == "admin")).password_hash
    seed(isp.settings, isp.password)
    with isp.factory() as db:
        assert db.scalar(select(User).where(User.role == "admin")).password_hash == original
        assert db.scalar(select(func.count()).select_from(CatalogItem)) == 0
        assert db.scalar(select(func.count()).select_from(Slot)) == 0
    with pytest.raises(ValueError, match="separate database"):
        seed(replace(isp.settings, database_url=env.settings.database_url), isp.password)


def test_reference_enquiry_produces_evidence_but_no_proposal(isp):
    conv = new_conversation(isp)
    send(isp, conv, "Show me Blizzard monthly plans and prices")
    assert asyncio.run(process_one(isp.factory, isp.profile, isp.app.state.workflow))
    detail = isp.client.get(f"/api/v1/conversations/{conv}").json()
    assert detail["proposals"] == []
    text = detail["messages"][-1]["content"]
    assert "StormFiber" in text and "Not approved Alpha Max" in text
    assert "4940.00" in text or "5028.00" in text
    with isp.factory() as db:
        assert db.scalar(select(func.count()).select_from(Proposal)) == 0
        with pytest.raises(HTTPException) as exc:
            quote(db, isp.profile, "ref-01", 1, 0)
        assert exc.value.status_code == 422
    assert isp.client.get("/api/v1/reference-data").json()["catalog"] == []


def test_reference_loader_rejects_unknown_and_invalid_money(isp, tmp_path, monkeypatch):
    profile = isp.profile.model_copy(update={"reference_catalog": "../../.env"})
    with pytest.raises(ValueError, match="Unknown reference"):
        reference_offers.load_offers(profile)
    data = reference_offers.load_offers(isp.profile).model_dump(mode="json")
    data["offers"][0]["total"] = "-5.00"
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(data))
    monkeypatch.setitem(reference_offers.SOURCES, isp.profile.reference_catalog, path)
    with pytest.raises(ValidationError):
        reference_offers.load_offers(isp.profile)


def test_reference_capability_requires_reference():
    data = json.loads((ROOT / "examples/business-profiles/profile-isp.json").read_text())
    data["reference_catalog"] = None
    with pytest.raises(ValidationError, match="Missing reference"):
        Profile.model_validate(data)
