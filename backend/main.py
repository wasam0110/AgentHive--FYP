import asyncio
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError

from backend.api import auth, conversations, operations
from backend.config import Settings
from backend.services.reference_offers import load_offers
from backend.db.connection import connect
from backend.db.models import Business
from backend.agents.provider import Provider
from backend.agents.workflow import Workflow
from backend.rag.retriever import Retriever
from backend.services.jobs import worker_loop


def create_app(settings=None, retriever=None):
    settings = settings or Settings.from_env()
    profile = settings.profile()
    load_offers(profile)  # Fail startup for invalid registered reference data.
    engine, factory = connect(settings.database_url)

    @asynccontextmanager
    async def lifespan(app):
        with factory() as db:
            business = db.scalar(select(Business))
            if not business or business.id != profile.business_id:
                raise RuntimeError(
                    "Run migrations and seed for this profile. Use an isolated database per business."
                )
        task = asyncio.create_task(worker_loop(app)) if settings.worker_enabled else None
        yield
        if task:
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task
        engine.dispose()

    app = FastAPI(title="Agent Hive API", version="0.1.0", lifespan=lifespan)
    app.state.settings, app.state.profile = settings, profile
    app.state.db, app.state.engine = factory, engine
    app.state.retriever = retriever or Retriever(settings.chroma_path, profile, settings.embedding_mode)
    app.state.workflow = Workflow(profile, Provider(settings), app.state.retriever, factory)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.frontend_origin],
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type", "X-CSRF-Token", "Idempotency-Key"],
    )

    @app.middleware("http")
    async def safety_headers(request: Request, call_next):
        length = request.headers.get("content-length")
        if length and (not length.isdigit() or int(length) > 32000):
            return JSONResponse(status_code=413, content={"detail": "Request too large"})
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Cache-Control"] = "no-store"
        return response

    @app.exception_handler(IntegrityError)
    async def conflict(request, exc):
        return JSONResponse(
            status_code=409,
            content={"detail": "A conflicting request changed this record. Reload before retrying."},
        )

    @app.get("/api/v1/health")
    def health():
        with engine.connect() as db:
            db.execute(text("SELECT 1"))
        return {
            "status": "ok",
            "database": "connected",
            "knowledge_chunks": app.state.retriever.collection.count(),
            "mode": settings.mode,
            "provider": "not probed" if settings.mode == "hosted" else "deterministic demo",
        }

    for router in [auth.router, conversations.router, operations.router]:
        app.include_router(router)
    return app


app = create_app()
