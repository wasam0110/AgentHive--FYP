"""Service-level identity checks; no application startup or integration fixtures."""

from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from backend.db.connection import connect
from backend.db.models import AuthSession, Base, User
from backend.services.security import digest, login, passwords, require_role


def test_login_stores_only_hashed_session_and_rejects_wrong_password(tmp_path):
    engine, factory = connect(f"sqlite:///{tmp_path / 'identity.db'}")
    try:
        Base.metadata.create_all(engine)
        profile = SimpleNamespace(business_id="demo-a")
        with factory.begin() as db:
            db.add(User(id="u", business_id="demo-a", email="u@example.test", name="Synthetic",
                        role="operator", password_hash=passwords.hash("test-only-long-password")))
        with factory.begin() as db:
            user, token, csrf = login(db, profile, "u@example.test", "test-only-long-password")
            assert csrf and token != csrf
            assert user.role == "operator"
        with factory() as db:
            assert db.get(AuthSession, token) is None
            assert db.get(AuthSession, digest(token)).user_id == "u"
            with pytest.raises(HTTPException) as error:
                login(db, profile, "u@example.test", "wrong")
            assert error.value.status_code == 401
            with pytest.raises(HTTPException) as error:
                require_role(user, "admin")
            assert error.value.status_code == 403
    finally:
        engine.dispose()
