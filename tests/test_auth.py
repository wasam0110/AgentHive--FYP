from fastapi.testclient import TestClient
from backend.db.models import AuthSession
from sqlalchemy import select
from conftest import new_conversation


def test_authentication_and_logout(env):
    stranger = TestClient(env.app)
    assert stranger.get("/api/v1/conversations").status_code == 401
    assert (
        stranger.post(
            "/api/v1/auth/login", json={"email": "admin@agenthive.test", "password": "incorrect"}
        ).status_code
        == 401
    )
    assert env.client.get("/api/v1/auth/me").json()["user"]["role"] == "admin"
    assert env.client.post("/api/v1/auth/logout", json={}).status_code == 200
    assert env.client.get("/api/v1/auth/me").status_code == 401


def test_csrf_and_origin_are_checked(env):
    body = {"customer_id": "demo-a-customer-1"}
    assert (
        env.client.post("/api/v1/conversations", json=body, headers={"X-CSRF-Token": "wrong"}).status_code
        == 403
    )
    assert (
        env.client.post(
            "/api/v1/conversations", json=body, headers={"Origin": "https://attacker.invalid"}
        ).status_code
        == 403
    )


def test_expired_session(env):
    with env.factory.begin() as db:
        db.scalar(select(AuthSession)).expires_at = "2000-01-01T00:00:00+00:00"
    assert env.client.get("/api/v1/profile").status_code == 401


def test_customer_cannot_impersonate_another_customer(env):
    other = new_conversation(env, customer=2)
    customer = env.login("customer")
    own = new_conversation(env, client=customer, customer=2)
    assert customer.get(f"/api/v1/conversations/{own}").json()["customer_id"] == "demo-a-customer-1"
    assert customer.get(f"/api/v1/conversations/{other}").status_code == 404
    assert customer.get(f"/api/v1/conversations/{other}/trace").status_code == 404
    assert customer.get("/api/v1/approvals").status_code == 403
    assert len(customer.get("/api/v1/reference-data").json()["customers"]) == 1


def test_evaluator_cannot_write(env):
    client = env.login("evaluator")
    assert client.get("/api/v1/overview").status_code == 200
    assert client.post("/api/v1/conversations", json={"customer_id": "demo-a-customer-1"}).status_code == 403


def test_unknown_input_fields_and_large_body_rejected(env):
    assert (
        env.client.post(
            "/api/v1/conversations", json={"customer_id": "demo-a-customer-1", "role": "admin"}
        ).status_code
        == 422
    )
    assert env.client.post("/api/v1/conversations", content="x" * 33000).status_code == 413


def test_cookie_is_httponly_and_login_rate_limited(env):
    from backend.api.auth import attempts

    attempts.clear()
    result = env.client.post(
        "/api/v1/auth/login", json={"email": "admin@agenthive.test", "password": env.password}
    )
    assert "HttpOnly" in result.headers["set-cookie"]
    assert "SameSite=lax" in result.headers["set-cookie"]
    for _ in range(9):
        env.client.post("/api/v1/auth/login", json={"email": "nobody@agenthive.test", "password": "bad"})
    assert (
        env.client.post(
            "/api/v1/auth/login", json={"email": "nobody@agenthive.test", "password": "bad"}
        ).status_code
        == 429
    )
