"""Standalone checks for profile-scoped synthetic seed fixtures."""

import pytest
from pydantic import ValidationError

from backend.config import Profile, ROOT
from scripts.seed_fixtures import SeedFixture, SeedItem, load_fixture


@pytest.mark.parametrize("profile_name,knowledge,resource", [
    ("profile-a.json", "demo-a", "demo-a-resources"),
    ("profile-b.json", "demo-b", None),
])
def test_seed_fixture_matches_profile_references(profile_name, knowledge, resource):
    profile = Profile.model_validate_json(
        (ROOT / "examples/business-profiles" / profile_name).read_text(encoding="utf-8")
    )

    fixture = load_fixture(profile)

    assert fixture.knowledge_directory == knowledge
    assert fixture.catalog_reference == profile.catalog
    assert fixture.resource_reference == resource == profile.resources
    assert fixture.customers
    assert fixture.items


def test_unregistered_knowledge_reference_is_rejected():
    profile = Profile.model_validate_json(
        (ROOT / "examples/business-profiles/profile-a.json").read_text(encoding="utf-8")
    ).model_copy(update={"knowledge_source": "../outside"})

    with pytest.raises(ValueError, match="No sandbox dataset registered"):
        load_fixture(profile)


def test_catalog_reference_mismatch_is_rejected():
    profile = Profile.model_validate_json(
        (ROOT / "examples/business-profiles/profile-a.json").read_text(encoding="utf-8")
    ).model_copy(update={"catalog": "unregistered-catalog"})

    with pytest.raises(ValueError, match="references do not match"):
        load_fixture(profile)


def test_seed_fixture_rejects_connection_for_unknown_customer():
    with pytest.raises(ValidationError, match="unknown fixture customer"):
        SeedFixture.model_validate({
            "knowledge_directory": "demo-a",
            "catalog_reference": "demo-a-catalog",
            "resource_reference": "demo-a-resources",
            "customers": ["Amina Khan"],
            "resource_label": "Specialist",
            "items": [],
            "connections": [{
                "customer": 2,
                "label": "Synthetic connection",
                "city": "Lahore",
                "area": "Model Town",
                "address": "Synthetic address",
                "plan": "Synthetic plan",
                "account_status": "active",
            }],
        })


def test_seed_item_price_requires_two_decimal_places():
    with pytest.raises(ValidationError):
        SeedItem.model_validate({
            "name": "Synthetic item",
            "description": "Fixture-only item",
            "price": "25",
        })
