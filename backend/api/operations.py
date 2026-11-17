from collections import Counter
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy import select

from backend.db.models import Conversation, Proposal, Run, Trace, now
from backend.schemas.api import ProposalDecision, RefreshProposal
from backend.services import approvals
from backend.services.service_context import context
from backend.services.reference_offers import load_offers
from backend.services.data import record, snapshot
from backend.services.security import authenticate, require_role

router = APIRouter(prefix="/api/v1", tags=["operations"])


@router.get("/profile")
def profile(request: Request, user=Depends(authenticate)):
    p = request.app.state.profile
    return {
        **p.model_dump(),
        "profile_hash": p.fingerprint,
        "mode": request.app.state.settings.mode,
        "embedding_mode": request.app.state.settings.embedding_mode,
    }


@router.get("/reference-data")
def reference_data(request: Request, user=Depends(authenticate)):
    with request.app.state.db() as db:
        data = snapshot(db, user.business_id)
        if user.role == "customer":
            data["customers"] = [c for c in data["customers"] if c["id"] == user.customer_id]
        if "resource_booking" not in request.app.state.profile.capabilities:
            data["slots"] = []
        return data


@router.get("/approvals")
def queue(request: Request, user=Depends(authenticate)):
    require_role(user, "operator", "admin", "evaluator")
    with request.app.state.db() as db:
        rows = db.scalars(
            select(Proposal)
            .join(Conversation)
            .where(Conversation.business_id == user.business_id)
            .order_by(Proposal.created_at.desc())
            .limit(100)
        )
        return [
            {
                **record(p),
                "expired": p.expires_at <= now() and p.status in {"awaiting_customer", "awaiting_admin"},
            }
            for p in rows
        ]


@router.post("/proposals/{id}/confirmation")
def confirm(id: str, body: ProposalDecision, request: Request, user=Depends(authenticate)):
    with request.app.state.db.begin() as db:
        return approvals.confirm(db, request.app.state.profile, id, user, body)


@router.post("/approvals/{id}/decision")
def decide(id: str, body: ProposalDecision, request: Request, user=Depends(authenticate)):
    with request.app.state.db.begin() as db:
        return approvals.decide(db, request.app.state.profile, id, user, body)


@router.post("/proposals/{id}/refresh")
def refresh(id: str, body: RefreshProposal, request: Request, user=Depends(authenticate)):
    with request.app.state.db.begin() as db:
        return approvals.refresh(db, request.app.state.profile, id, user, body)


@router.get("/overview")
def overview(request: Request, user=Depends(authenticate)):
    require_role(user, "operator", "admin", "evaluator")
    with request.app.state.db() as db:
        conversations = list(
            db.scalars(select(Conversation).where(Conversation.business_id == user.business_id))
        )
        ids = [c.id for c in conversations]
        proposals = list(db.scalars(select(Proposal).where(Proposal.conversation_id.in_(ids))))
        runs = list(db.scalars(select(Run).where(Run.conversation_id.in_(ids))))
        completed = [c for c in conversations if c.status == "completed"]
        pending = [p for p in proposals if p.status == "awaiting_admin" and p.expires_at > now()]
        today = datetime.now(timezone.utc).date()
        series = []
        for i in range(6, -1, -1):
            day = str(today - timedelta(days=i))
            series.append({"date": day, "count": sum(c.created_at.startswith(day) for c in conversations)})
        traces = [
            record(t)
            for t in db.scalars(
                select(Trace).where(Trace.conversation_id.in_(ids)).order_by(Trace.sequence.desc()).limit(12)
            )
        ]
        latencies = [
            (datetime.fromisoformat(x.completed_at) - datetime.fromisoformat(x.created_at)).total_seconds()
            for x in runs
            if x.completed_at
        ]
        return {
            "total": len(conversations),
            "completed": len(completed),
            "pending": len(pending),
            "status_counts": dict(Counter(c.status for c in conversations)),
            "series": series,
            "completion_rate": round(100 * len(completed) / len(conversations)) if conversations else None,
            "average_seconds": round(sum(latencies) / len(latencies), 2) if latencies else None,
            "recent": traces,
            "updated_at": now(),
            "oldest_pending": min((p.created_at for p in pending), default=None),
        }


@router.get("/knowledge")
def knowledge(request: Request, user=Depends(authenticate)):
    require_role(user, "admin", "operator", "evaluator")
    collection = request.app.state.retriever.collection
    result = collection.get(limit=100)
    return {
        "embedding_mode": request.app.state.settings.embedding_mode,
        "count": collection.count(),
        "chunks": [
            {"id": id, "content": result["documents"][i], "metadata": result["metadatas"][i]}
            for i, id in enumerate(result["ids"])
        ],
    }


@router.get("/evaluations")
def evaluations(user=Depends(authenticate)):
    require_role(user, "admin", "operator", "evaluator")
    return {
        "runs": [],
        "status": "FYP-II research runs have not been performed. No benchmark scores are fabricated.",
    }


@router.get("/reference-offers")
def reference_offers(request: Request, user=Depends(authenticate)):
    """Authenticated, profile-scoped information only; never creates a quote."""
    data = load_offers(request.app.state.profile)
    if data is None:
        raise HTTPException(404, "Reference offers are not enabled for this business")
    return data.model_dump(mode="json")


@router.get("/service-context")
def service_context(request: Request, customer_id: str | None = None,
                    connection_id: str | None = None, user=Depends(authenticate)):
    require_role(user, "customer", "operator", "admin")
    profile = request.app.state.profile
    if "service_context" not in profile.capabilities:
        raise HTTPException(404, "Service context is not enabled")
    if user.role == "customer":
        if customer_id and customer_id != user.customer_id:
            raise HTTPException(403, "Only your own service records are available")
        customer_id = user.customer_id
    with request.app.state.db() as db:
        return context(db, profile, customer_id, connection_id)
