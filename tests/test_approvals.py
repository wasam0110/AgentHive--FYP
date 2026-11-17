from concurrent.futures import ThreadPoolExecutor
from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError, OperationalError
from backend.db.models import Booking, CatalogItem, Decision, Proposal, Receipt, ServiceRequest
from backend.schemas.api import ProposalDecision
from backend.services import approvals
from conftest import approve, consent, proposal


def count(env, model):
    with env.factory() as db:
        return db.scalar(select(func.count()).select_from(model))


def test_quote_consent_approval_and_receipt_replay(env):
    p = proposal(env, booking=True)
    assert p["payload"]["total"] == "2375.00"
    assert approve(env, p).status_code == 409
    assert count(env, ServiceRequest) == 0
    assert consent(env, p).status_code == 200
    result = approve(env, p)
    assert result.status_code == 200, result.text
    assert result.json()["receipt"]["payload"]["simulated"] is True
    assert approve(env, p).json()["receipt"]["id"] == result.json()["receipt"]["id"]
    assert count(env, ServiceRequest) == count(env, Booking) == count(env, Receipt) == 1
    assert count(env, Decision) == 2


def test_operator_cannot_approve(env):
    p = proposal(env)
    consent(env, p)
    assert approve(env, p, client=env.login("operator")).status_code == 403
    assert count(env, ServiceRequest) == 0


def test_customer_cannot_confirm_other_customer_offer(env):
    from conftest import new_conversation, send, run_job

    conv = new_conversation(env, customer=2)
    send(env, conv, item_id="demo-a-item-1")
    run_job(env)
    p = env.client.get(f"/api/v1/conversations/{conv}").json()["proposals"][0]
    response = env.login("customer").post(
        f"/api/v1/proposals/{p['id']}/confirmation", json={"version": 1, "approved": True}
    )
    assert response.status_code == 404


def test_expiry_blocks_execution(env):
    p = proposal(env)
    consent(env, p)
    with env.factory.begin() as db:
        db.get(Proposal, p["id"]).expires_at = "2000-01-01T00:00:00+00:00"
    assert approve(env, p).status_code == 409
    assert count(env, Receipt) == 0


def test_changed_price_requires_new_consent(env):
    p = proposal(env)
    consent(env, p)
    with env.factory.begin() as db:
        db.get(CatalogItem, "demo-a-item-1").price = "3000.00"
    assert approve(env, p).status_code == 409
    refreshed = env.client.post(f"/api/v1/proposals/{p['id']}/refresh", json={"version": 1}).json()
    assert refreshed["version"] == 2 and refreshed["payload"]["total"] == "2850.00"
    assert approve(env, p).status_code == 409
    assert approve(env, refreshed).status_code == 409
    consent(env, refreshed)
    assert approve(env, refreshed).status_code == 200


def test_policy_fingerprint_changes_invalidate_offer(env):
    p = proposal(env)
    consent(env, p)
    env.app.state.profile = env.profile.model_copy(update={"display_name": "Changed configuration"})
    assert approve(env, p).status_code == 409
    assert count(env, ServiceRequest) == 0


def test_rejection_requires_reason_and_cannot_execute(env):
    p = proposal(env)
    consent(env, p)
    assert approve(env, p, approved=False).status_code == 422
    assert approve(env, p, approved=False, reason="Customer requested review").status_code == 200
    assert approve(env, p).status_code == 409
    assert count(env, Receipt) == 0


def test_discount_above_policy_does_not_create_offer(env):
    from conftest import new_conversation, send, run_job

    conv = new_conversation(env)
    send(env, conv, item_id="demo-a-item-1", discount_pct=6)
    run_job(env)
    detail = env.client.get(f"/api/v1/conversations/{conv}").json()
    assert detail["proposals"] == []
    assert "outside policy" in detail["messages"][-1]["content"]


def test_competing_transactions_cannot_double_book(env):
    first = proposal(env, booking=True)
    second = proposal(env, booking=True)
    assert first["payload"]["slot_id"] == second["payload"]["slot_id"]
    consent(env, first)
    consent(env, second)

    def execute(p):
        try:
            with env.factory.begin() as db:
                approvals.decide(
                    db, env.profile, p["id"], env.admin, ProposalDecision(version=1, approved=True)
                )
            return "success"
        except (HTTPException, IntegrityError, OperationalError):
            return "conflict"

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(execute, [first, second]))
    assert outcomes.count("success") == 1
    assert count(env, Booking) == count(env, ServiceRequest) == count(env, Receipt) == 1


def test_duplicate_approval_transactions_have_one_effect(env):
    p = proposal(env)
    consent(env, p)

    def execute(_):
        try:
            with env.factory.begin() as db:
                return approvals.decide(
                    db, env.profile, p["id"], env.admin, ProposalDecision(version=1, approved=True)
                )
        except (HTTPException, IntegrityError, OperationalError):
            return None

    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(execute, range(2)))
    assert count(env, ServiceRequest) == count(env, Receipt) == 1
    assert approve(env, p).status_code == 200
