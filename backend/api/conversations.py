import hashlib
import json
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy import select, update

from backend.db.models import Conversation, Customer, Decision, Message, Proposal, Receipt, Run, Trace, now
from backend.schemas.api import NewConversation, NewMessage
from backend.services.service_context import select_connection
from backend.services.data import conversation_for, record
from backend.services.security import authenticate, require_role

router = APIRouter(prefix="/api/v1/conversations", tags=["conversations"])


@router.get("")
def listing(request: Request, user=Depends(authenticate)):
    with request.app.state.db() as db:
        query = select(Conversation).where(Conversation.business_id == user.business_id)
        if user.role == "customer":
            query = query.where(Conversation.customer_id == user.customer_id)
        return [record(c) for c in db.scalars(query.order_by(Conversation.updated_at.desc()).limit(100))]


@router.post("", status_code=201)
def create(body: NewConversation, request: Request, user=Depends(authenticate)):
    require_role(user, "customer", "operator", "admin")
    customer_id = user.customer_id if user.role == "customer" else body.customer_id
    with request.app.state.db.begin() as db:
        customer = db.get(Customer, customer_id) if customer_id else None
        if not customer or customer.business_id != user.business_id:
            raise HTTPException(422, "Choose a valid customer for this simulation")
        if body.language not in request.app.state.profile.languages:
            raise HTTPException(422, "Language is not enabled")
        connection_id = select_connection(db, request.app.state.profile, customer_id, body.connection_id)
        conv = Conversation(
            business_id=user.business_id,
            customer_id=customer_id,
            connection_id=connection_id,
            language=body.language,
            status="waiting_customer",
        )
        db.add(conv)
        db.flush()
        return record(conv)


@router.get("/{id}")
def detail(id: str, request: Request, user=Depends(authenticate)):
    with request.app.state.db() as db:
        conv = conversation_for(db, id, user)
        proposals = list(db.scalars(select(Proposal).where(Proposal.conversation_id == id)))
        rows = []
        for p in proposals:
            data = record(p)
            data["expired"] = p.expires_at <= now() and p.status in {"awaiting_customer", "awaiting_admin"}
            data["decisions"] = [
                record(x) for x in db.scalars(select(Decision).where(Decision.proposal_id == p.id))
            ]
            receipt = db.scalar(select(Receipt).where(Receipt.proposal_id == p.id))
            data["receipt"] = record(receipt) if receipt else None
            rows.append(data)
        return {
            **record(conv),
            "messages": [
                record(m)
                for m in db.scalars(
                    select(Message).where(Message.conversation_id == id).order_by(Message.created_at)
                )
            ],
            "proposals": rows,
        }


@router.get("/{id}/trace")
def trace(id: str, request: Request, after: int = 0, user=Depends(authenticate)):
    with request.app.state.db() as db:
        conversation_for(db, id, user)
        return [
            record(t)
            for t in db.scalars(
                select(Trace)
                .where(Trace.conversation_id == id, Trace.sequence > after)
                .order_by(Trace.sequence)
                .limit(500)
            )
        ]


@router.post("/{id}/messages", status_code=202)
def send(
    id: str,
    body: NewMessage,
    request: Request,
    idempotency_key: str = Header(min_length=8, max_length=100),
    user=Depends(authenticate),
):
    require_role(user, "customer", "operator", "admin")
    payload = body.model_dump()
    if not body.content.strip():
        raise HTTPException(422, "Message must not be blank")
    fingerprint = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
    with request.app.state.db.begin() as db:
        conv = conversation_for(db, id, user)
        existing = db.scalar(select(Run).where(Run.conversation_id == id, Run.request_key == idempotency_key))
        if existing:
            if existing.request_hash != fingerprint:
                raise HTTPException(409, "Idempotency key was used for a different message")
            return {"run_id": existing.id, "replayed": True}
        active = db.execute(
            update(Conversation)
            .where(Conversation.id == id, Conversation.status.not_in(["running", "queued", "waiting_admin"]))
            .values(status="queued", updated_at=now())
        )
        if active.rowcount == 0:
            raise HTTPException(409, "Finish the pending run or approval before sending another message")
        pending = db.scalar(
            select(Proposal.id).where(
                Proposal.conversation_id == id, Proposal.status.in_(["awaiting_customer", "awaiting_admin"])
            )
        )
        if pending:
            raise HTTPException(409, "Confirm, decline or refresh the pending offer first")
        conv.title = body.content[:70]
        conv.status = "queued"
        run = Run(conversation_id=id, request_key=idempotency_key, request_hash=fingerprint, input=payload)
        db.add(run)
        db.add(Message(conversation_id=id, sender="customer", content=body.content))
        db.flush()
        db.add(
            Trace(
                conversation_id=id,
                run_id=run.id,
                agent="intake",
                status="queued",
                summary="Request stored in the durable queue.",
                details={"mode": request.app.state.settings.mode},
            )
        )
        return {"run_id": run.id, "replayed": False}
