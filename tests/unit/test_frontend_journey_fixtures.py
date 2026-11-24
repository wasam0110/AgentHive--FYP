"""Keep Asad's synthetic frontend journey fixtures aligned with W05 scope."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_frontend_fixtures_cover_prd_journeys_and_label_live_gaps():
    fixtures = json.loads(
        (ROOT / "examples/frontend/demo-journeys.json").read_text(encoding="utf-8")
    )

    journeys = {journey["id"]: journey for journey in fixtures["journeys"]}
    assert set(journeys) == {
        "support-plus-quote",
        "sensitive-request-rejected-or-expired",
        "mixed-language-clarification-and-recovery",
    }
    assert fixtures["classification"].startswith("synthetic mock")
    assert journeys["mixed-language-clarification-and-recovery"]["implementation_status"] == (
        "target-only-backend-gap"
    )
    assert "does not persist a clarification question" in journeys[
        "mixed-language-clarification-and-recovery"
    ]["blocker"]


def test_mutating_mock_interactions_use_current_safe_request_contract():
    fixtures = json.loads(
        (ROOT / "examples/frontend/demo-journeys.json").read_text(encoding="utf-8")
    )

    interactions = []
    for journey in fixtures["journeys"]:
        interactions.extend(journey.get("interactions", []))
        interactions.extend(journey.get("target_interactions", []))
        for branch in journey.get("branches", []):
            interactions.extend(branch["interactions"])

    for interaction in interactions:
        request = interaction["request"]
        assert request["method"] in {"GET", "POST"}
        assert request["path"].startswith("/api/v1/")
        if request["method"] == "POST" and request["path"].endswith("/messages"):
            assert request["headers"]["Idempotency-Key"]
        if request["path"].endswith("/decision") or request["path"].endswith("/confirmation"):
            assert request["body"]["version"]
