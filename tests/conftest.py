"""Synthetic databases only. TEST_DATABASE_URL must point to a disposable CI database."""

from dataclasses import replace
import asyncio
import os
import secrets
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from backend.config import ROOT, Settings
from backend.db.connection import connect
from backend.db.models import Base, User
from backend.main import create_app
from backend.api.auth import attempts
from backend.rag.retriever import Retriever
from backend.services.jobs import process_one
from scripts.seed import seed


@pytest.fixture(scope="session")
def password():
    return secrets.token_urlsafe(24)


@pytest.fixture(scope="session")
def index_path(tmp_path_factory):
    return str(tmp_path_factory.mktemp("knowledge"))


@pytest.fixture
def env(tmp_path, index_path, password):
    settings = Settings(
        os.getenv("TEST_DATABASE_URL", f"sqlite:///{tmp_path}/test.db"),
        str(ROOT / "examples/business-profiles/profile-a.json"),
        index_path,
        "demo",
        "http://localhost:3000",
        False,
        "",
        "",
        "",
        "lexical",
        False,
    )
    engine, factory = connect(settings.database_url)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    seed(settings, password)
    retriever = Retriever(index_path, settings.profile())
    app = create_app(settings, retriever)
    attempts.clear()

    def login(role="admin"):
        client = TestClient(app)
        result = client.post(
            "/api/v1/auth/login", json={"email": f"{role}@agenthive.test", "password": password}
        )
        assert result.status_code == 200, result.text
        client.headers["X-CSRF-Token"] = result.json()["csrf_token"]
        client.headers["Origin"] = settings.frontend_origin
        return client

    client = login()
    with factory() as db:
        admin = db.scalar(select(User).where(User.role == "admin"))
    yield SimpleNamespace(
        settings=settings,
        app=app,
        factory=factory,
        client=client,
        login=login,
        profile=settings.profile(),
        admin=admin,
        password=password,
        engine=engine,
    )
    client.close()
    engine.dispose()
    app.state.engine.dispose()


def new_conversation(env, client=None, customer=1):
    client = client or env.client
    result = client.post(
        "/api/v1/conversations", json={"customer_id": f"{env.profile.business_id}-customer-{customer}"}
    )
    assert result.status_code == 201, result.text
    return result.json()["id"]


def send(env, conversation, content="I need support and a quote", client=None, **choices):
    client = client or env.client
    result = client.post(
        f"/api/v1/conversations/{conversation}/messages",
        json={"content": content, **choices},
        headers={"Idempotency-Key": str(uuid4())},
    )
    assert result.status_code == 202, result.text
    return result.json()["run_id"]


def run_job(env):
    return asyncio.run(process_one(env.factory, env.profile, env.app.state.workflow))


def proposal(env, booking=False):
    conv = new_conversation(env)
    choices = {"item_id": "demo-a-item-1", "discount_pct": 5}
    if booking:
        choices["slot_id"] = env.client.get("/api/v1/reference-data").json()["slots"][0]["id"]
    send(env, conv, **choices)
    assert run_job(env)
    detail = env.client.get(f"/api/v1/conversations/{conv}").json()
    assert len(detail["proposals"]) == 1, detail
    return detail["proposals"][0]


def consent(env, p):
    return env.client.post(
        f"/api/v1/proposals/{p['id']}/confirmation", json={"version": p["version"], "approved": True}
    )


def approve(env, p, client=None, approved=True, reason=""):
    return (client or env.client).post(
        f"/api/v1/approvals/{p['id']}/decision",
        json={"version": p["version"], "approved": approved, "reason": reason},
    )


@pytest.fixture
def isp(env, tmp_path):
    settings = replace(env.settings, database_url=f"sqlite:///{tmp_path}/isp.db",
                       chroma_path=str(tmp_path / "isp-index"),
                       profile_path=str(ROOT / "examples/business-profiles/profile-isp.json"))
    engine, factory = connect(settings.database_url)
    Base.metadata.create_all(engine)
    seed(settings, env.password)
    app = create_app(settings)
    with TestClient(app) as client:
        result = client.post("/api/v1/auth/login", json={"email": "admin@agenthive.test",
                                                       "password": env.password})
        assert result.status_code == 200
        client.headers.update({"X-CSRF-Token": result.json()["csrf_token"],
                               "Origin": settings.frontend_origin})
        from types import SimpleNamespace
        yield SimpleNamespace(settings=settings, profile=settings.profile(), app=app,
                              client=client, factory=factory, password=env.password)
    engine.dispose()

