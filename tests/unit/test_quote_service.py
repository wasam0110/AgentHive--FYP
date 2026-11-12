"""Quote and proposal validation tests with an explicit fake catalog adapter."""

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from backend.config import ROOT, Profile
from backend.db.models import Booking, CatalogItem, Slot
from backend.services.approvals import validate
from backend.services.quotes import quote
from backend.services.redaction import redact


class FakeDataAdapter:
    def __init__(self, profile, *, price="2500.00", active=True, business_id=None, booked=False):
        self.item = CatalogItem(
            id="synthetic-item",
            business_id=business_id or profile.business_id,
            name="Synthetic consultation",
            description="Test fixture",
            price=price,
            active=active,
        )
        self.slot = None
        self.booked = booked

    def get(self, model, record_id):
        if model is CatalogItem and record_id == self.item.id:
            return self.item
        if model is Slot and self.slot is not None and record_id == self.slot.id:
            return self.slot
        return None

    def scalar(self, statement):
        return Booking(slot_id="synthetic-slot") if self.booked else None


@pytest.fixture
def profile():
    path = ROOT / "examples" / "business-profiles" / "profile-a.json"
    return Profile.model_validate_json(path.read_text(encoding="utf-8"))


def valid_terms(db, profile):
    return quote(db, profile, "synthetic-item", 1, 0)


def make_proposal(db, profile, *, payload=None, expires_at=None, profile_hash=None):
    return SimpleNamespace(
        version=1,
        status="awaiting_customer",
        payload=valid_terms(db, profile) if payload is None else payload,
        expires_at=expires_at or (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat(),
        profile_hash=profile.fingerprint if profile_hash is None else profile_hash,
    )


def test_quote_uses_catalog_price_currency_and_decimal_rounding(profile):
    db = FakeDataAdapter(profile, price="2500.00")

    result = quote(db, profile, "synthetic-item", 2, 5)

    assert result["unit_price"] == "2500.00"
    assert result["total"] == "4750.00"
    assert result["currency"] == "PKR"


def test_quote_uses_each_profile_catalog_price_and_currency(profile):
    profile_b_path = ROOT / "examples" / "business-profiles" / "profile-b.json"
    profile_b = Profile.model_validate_json(profile_b_path.read_text(encoding="utf-8"))
    quote_a = quote(FakeDataAdapter(profile, price="2500.00"), profile, "synthetic-item", 1, 0)
    quote_b = quote(FakeDataAdapter(profile_b, price="19.99"), profile_b, "synthetic-item", 1, 0)

    assert (quote_a["total"], quote_a["currency"]) == ("2500.00", "PKR")
    assert (quote_b["total"], quote_b["currency"]) == ("19.99", "USD")


def test_quote_rounds_half_up_to_currency_minor_unit(profile):
    db = FakeDataAdapter(profile, price="0.05")

    assert quote(db, profile, "synthetic-item", 1, 5)["total"] == "0.05"


@pytest.mark.parametrize("quantity,discount", [(0, 0), (101, 0), (True, 0), (1, -1), (1, 6), (1, True)])
def test_quote_rejects_invalid_quantity_or_discount(profile, quantity, discount):
    with pytest.raises(HTTPException) as error:
        quote(FakeDataAdapter(profile), profile, "synthetic-item", quantity, discount)

    assert error.value.status_code == 422


@pytest.mark.parametrize("price", ["", None, 12.5, "not-a-price", "NaN", "Infinity", "-1.00", "12.345"])
def test_quote_rejects_malformed_or_non_money_catalog_values(profile, price):
    with pytest.raises(HTTPException) as error:
        quote(FakeDataAdapter(profile, price=price), profile, "synthetic-item", 1, 0)

    assert error.value.status_code == 422


def test_quote_rejects_missing_inactive_and_cross_business_items(profile):
    cases = [
        (FakeDataAdapter(profile), "missing-item"),
        (FakeDataAdapter(profile, active=False), "synthetic-item"),
        (FakeDataAdapter(profile, business_id="other-business"), "synthetic-item"),
    ]

    for db, item_id in cases:
        with pytest.raises(HTTPException) as error:
            quote(db, profile, item_id, 1, 0)
        assert error.value.status_code == 422


def test_quote_rejects_discount_without_catalog_item(profile):
    with pytest.raises(HTTPException, match="requires a catalog item"):
        quote(FakeDataAdapter(profile), profile, None, 1, 1)


def test_profile_without_booking_capability_cannot_quote_a_slot(profile):
    profile_b_path = ROOT / "examples" / "business-profiles" / "profile-b.json"
    profile_b = Profile.model_validate_json(profile_b_path.read_text(encoding="utf-8"))
    db = FakeDataAdapter(profile_b)
    db.slot = Slot(
        id="synthetic-slot",
        business_id=profile_b.business_id,
        resource="Synthetic resource",
        starts_at=(datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(),
        ends_at=(datetime.now(timezone.utc) + timedelta(hours=2)).isoformat(),
        active=True,
    )

    with pytest.raises(HTTPException) as error:
        quote(db, profile_b, None, 1, 0, "synthetic-slot")

    assert error.value.status_code == 422


def test_proposal_validation_accepts_current_terms(profile):
    db = FakeDataAdapter(profile)
    proposal = make_proposal(db, profile)

    assert validate(db, proposal, profile, 1) is None


def test_proposal_validation_rejects_stale_version(profile):
    db = FakeDataAdapter(profile)
    proposal = make_proposal(db, profile)

    with pytest.raises(HTTPException) as error:
        validate(db, proposal, profile, 2)

    assert error.value.status_code == 409


def test_proposal_validation_rejects_closed_proposal(profile):
    db = FakeDataAdapter(profile)
    proposal = make_proposal(db, profile)
    proposal.status = "rejected"

    with pytest.raises(HTTPException) as error:
        validate(db, proposal, profile, 1)

    assert error.value.status_code == 409


def test_proposal_validation_denies_terms_over_profile_discount_limit(profile):
    db = FakeDataAdapter(profile)
    denied_terms = quote(db, profile, "synthetic-item", 1, 5)
    denied_terms["discount_pct"] = 6
    proposal = make_proposal(db, profile, payload=denied_terms)

    with pytest.raises(HTTPException) as error:
        validate(db, proposal, profile, 1)

    assert error.value.status_code == 422


def test_proposal_validation_rejects_malformed_version_and_payload(profile):
    db = FakeDataAdapter(profile)
    proposal = make_proposal(db, profile)

    with pytest.raises(HTTPException) as invalid_version:
        validate(db, proposal, profile, True)
    assert invalid_version.value.status_code == 422

    malformed = dict(proposal.payload)
    del malformed["total"]
    with pytest.raises(HTTPException) as invalid_payload:
        validate(db, make_proposal(db, profile, payload=malformed), profile, 1)
    assert invalid_payload.value.status_code == 422

    with pytest.raises(HTTPException) as missing_proposal:
        validate(db, object(), profile, 1)
    assert missing_proposal.value.status_code == 422

    proposal.status = None
    with pytest.raises(HTTPException) as missing_status:
        validate(db, proposal, profile, 1)
    assert missing_status.value.status_code == 422


def test_proposal_validation_rejects_expired_or_malformed_expiry(profile):
    db = FakeDataAdapter(profile)
    expired = (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()

    with pytest.raises(HTTPException) as error:
        validate(db, make_proposal(db, profile, expires_at=expired), profile, 1)
    assert error.value.status_code == 409

    with pytest.raises(HTTPException) as malformed:
        validate(db, make_proposal(db, profile, expires_at="not-a-timestamp"), profile, 1)
    assert malformed.value.status_code == 422


def test_proposal_validation_rejects_policy_price_and_booking_changes(profile):
    db = FakeDataAdapter(profile)
    proposal = make_proposal(db, profile)

    changed_profile = profile.model_copy(update={"display_name": "Changed synthetic profile"})
    with pytest.raises(HTTPException) as changed_policy:
        validate(db, proposal, changed_profile, 1)
    assert changed_policy.value.status_code == 409

    db.item.price = "3000.00"
    with pytest.raises(HTTPException) as changed_price:
        validate(db, proposal, profile, 1)
    assert changed_price.value.status_code == 409

    db.item.price = "2500.00"
    starts_at = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
    ends_at = (datetime.now(timezone.utc) + timedelta(hours=2)).isoformat()
    db.slot = Slot(
        id="synthetic-slot",
        business_id=profile.business_id,
        resource="Synthetic resource",
        starts_at=starts_at,
        ends_at=ends_at,
        active=True,
    )
    proposal = make_proposal(
        db, profile, payload=quote(db, profile, None, 1, 0, "synthetic-slot")
    )
    db.booked = True
    with pytest.raises(HTTPException) as booked:
        validate(db, proposal, profile, 1)
    assert booked.value.status_code == 409


def test_redaction_handles_nested_credentials_and_preserves_safe_evidence():
    message = "Bearer " + "demo-token" + " password" + "=" + "demo-value"
    message += " owner " + "person@" + "example.test"
    value = {
        "message": message,
        "nested": [{"token": "secret", "access_token": "demo-token", "source_id": "quote:synthetic"}],
    }

    assert redact(value) == {
        "message": "******" + " password" + "=[redacted] owner [email]",
        "nested": [
            {"token": "[redacted]", "access_token": "[redacted]", "source_id": "quote:synthetic"}
        ],
    }
