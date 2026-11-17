import time
from collections import defaultdict, deque
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from backend.schemas.api import Login
from backend.services.security import authenticate, digest, login
from backend.db.models import AuthSession

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])
# Single-process demo limiter; use a shared gateway limiter before multi-instance deployment.
attempts = defaultdict(deque)


@router.post("/login")
def sign_in(body: Login, request: Request, response: Response):
    origin = request.headers.get("origin")
    if origin and origin != request.app.state.settings.frontend_origin:
        raise HTTPException(403, "Origin not allowed")
    key = request.client.host
    timestamps = attempts[key]
    while timestamps and timestamps[0] < time.monotonic() - 60:
        timestamps.popleft()
    if len(timestamps) >= 10:
        raise HTTPException(429, "Too many attempts. Try again in a minute.")
    timestamps.append(time.monotonic())
    with request.app.state.db.begin() as db:
        user, token, csrf = login(db, request.app.state.profile, body.email, body.password)
    response.set_cookie(
        "hive_session",
        token,
        httponly=True,
        secure=request.app.state.settings.secure_cookie,
        samesite="lax",
        max_age=28800,
    )
    return {"user": public_user(user), "csrf_token": csrf}


def public_user(user):
    return {"id": user.id, "name": user.name, "email": user.email, "role": user.role}


@router.get("/me")
def me(request: Request, user=Depends(authenticate)):
    with request.app.state.db() as db:
        session = db.get(AuthSession, digest(request.cookies["hive_session"]))
        return {"user": public_user(user), "csrf_token": session.csrf}


@router.post("/logout")
def logout(request: Request, response: Response, user=Depends(authenticate)):
    with request.app.state.db.begin() as db:
        db.delete(db.get(AuthSession, digest(request.cookies["hive_session"])))
    response.delete_cookie("hive_session")
    return {"ok": True}
