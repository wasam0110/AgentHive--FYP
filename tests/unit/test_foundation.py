"""Foundation checks that do not import the application or integration fixtures."""

import json

import pytest
from pydantic import ValidationError
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError

from backend.config import ROOT, Profile
from backend.db.connection import connect
from backend.db.models import Base, Business, Customer, Conversation, Run
from backend.schemas.api import Intake


def profile_data():
    return json.loads((ROOT / "examples/business-profiles/profile-a.json").read_text(encoding="utf-8"))


def test_profiles_have_distinct_policy_and_capabilities():
    a = Profile.model_validate(profile_data())
    b = Profile.model_validate_json(
        (ROOT / "examples/business-profiles/profile-b.json").read_text(encoding="utf-8")
    )
    assert a.currency == "PKR" and b.currency == "USD"
    assert "resource_booking" in a.capabilities and "resource_booking" not in b.capabilities
    changed = profile_data()
    changed["policy"]["max_discount_pct"] = 4
    assert Profile.model_validate(changed).fingerprint != a.fingerprint


@pytest.mark.parametrize("change", [
    {"capabilities": ["execute_sql"]},
    {"catalog": None},
    {"adapters": {"data": "unregistered", "execution": "sandbox_v1"}},
    {"currency": "ZZZ"},
    {"policy": {"max_discount_pct": 101, "quote_expiry_minutes": 30,
                "approval_expiry_hours": 48}},
])
def test_invalid_profile_rejected(change):
    data = profile_data()
    data.update(change)
    with pytest.raises(ValidationError):
        Profile.model_validate(data)


def test_worker_schema_rejects_write_instructions():
    with pytest.raises(ValidationError):
        Intake.model_validate({"support": True, "execute_sql": "DELETE FROM users"})


def test_persisted_run_key_is_unique_and_foreign_keys_are_enforced(tmp_path):
    engine, factory = connect(f"sqlite:///{tmp_path / 'foundation.db'}")
    try:
        Base.metadata.create_all(engine)
        with factory.begin() as db:
            db.add(Business(id="demo-a", fingerprint="test"))
            db.add(Customer(id="customer", business_id="demo-a", name="Synthetic", email="x@example.test"))
        with factory.begin() as db:
            db.add(Conversation(id="conversation", business_id="demo-a", customer_id="customer"))
        with factory.begin() as db:
            db.add(Run(id="run", conversation_id="conversation", request_key="key",
                       request_hash="hash", input={}))
        with pytest.raises(IntegrityError), factory.begin() as db:
            db.add(Run(conversation_id="conversation", request_key="key", request_hash="hash", input={}))
        with pytest.raises(IntegrityError), factory.begin() as db:
            db.add(Conversation(business_id="demo-a", customer_id="missing"))
        with factory() as db:
            assert db.get(Run, "run").request_hash == "hash"
        unique = inspect(engine).get_unique_constraints("receipts")
        assert any(c["column_names"] == ["proposal_id"] for c in unique)
    finally:
        engine.dispose()
