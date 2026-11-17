"""Opaque server sessions with Argon2 passwords and session-bound CSRF."""

import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, Request
from pwdlib import PasswordHash
from sqlalchemy import select

from backend.db.models import AuthSession, User

passwords = PasswordHash.recommended()


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def expiry(hours=8):
    return (datetime.now(timezone.utc) + timedelta(hours=hours)).isoformat()


def authenticate(request: Request):
    token = request.cookies.get("hive_session", "")
    with request.app.state.db() as db:
        session = db.get(AuthSession, digest(token))
        if not session or session.expires_at <= datetime.now(timezone.utc).isoformat():
            raise HTTPException(401, "Sign in to continue")
        user = db.get(User, session.user_id)
        if not user or user.business_id != request.app.state.profile.business_id:
            raise HTTPException(403, "Business access denied")
        if request.method not in {"GET", "HEAD", "OPTIONS"}:
            csrf = request.headers.get("x-csrf-token", "")
            if not secrets.compare_digest(csrf, session.csrf):
                raise HTTPException(403, "Invalid CSRF token")
            origin = request.headers.get("origin")
            if origin and origin != request.app.state.settings.frontend_origin:
                raise HTTPException(403, "Origin not allowed")
        return user


def require_role(user, *roles):
    if user.role not in roles:
        raise HTTPException(403, "Your role cannot perform this action")


def login(db, profile, email, password):
    user = db.scalar(select(User).where(User.email == email.lower(), User.business_id == profile.business_id))
    if not user or not passwords.verify(password, user.password_hash):
        raise HTTPException(401, "Invalid email or password")
    token, csrf = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
    db.add(AuthSession(token_hash=digest(token), user_id=user.id, csrf=csrf, expires_at=expiry()))
    return user, token, csrf
