"""Consent, approval, and writes share a transaction; nothing is authorized by the UI."""

from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy import select, update

from backend.db.models import (
    Booking,
    Conversation,
    Decision,
    Message,
    Proposal,
    Receipt,
    ServiceRequest,
    Trace,
    now,
)
from backend.services.data import conversation_for, record
from backend.services.quotes import quote
from backend.services.redaction import redact
from backend.services.security import require_role


def _expiry(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, TypeError, ValueError) as exc:
        raise HTTPException(422, "Proposal expiry is malformed") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise HTTPException(422, "Proposal expiry must include a timezone")
    return parsed.astimezone(timezone.utc)


def deadline(profile):
    minutes = min(profile.policy.quote_expiry_minutes, profile.policy.approval_expiry_hours * 60)
    return (datetime.now(timezone.utc) + timedelta(minutes=minutes)).isoformat()


def get_locked(db, proposal_id, user):
    proposal = db.scalar(select(Proposal).where(Proposal.id == proposal_id).with_for_update())
    if not proposal:
        raise HTTPException(404, "Proposal not found")
    conversation_for(db, proposal.conversation_id, user)
    return proposal


def validate(db, proposal, profile, version):
    """Validate proposal shape, status, expiry and current authoritative terms."""
    if isinstance(version, bool) or not isinstance(version, int) or version < 1:
        raise HTTPException(422, "Proposal version is invalid")
    if not all(
        hasattr(proposal, field) for field in ("version", "status", "payload", "expires_at", "profile_hash")
    ):
        raise HTTPException(422, "Proposal is malformed")
    if isinstance(proposal.version, bool) or not isinstance(proposal.version, int) or proposal.version < 1:
        raise HTTPException(422, "Stored proposal version is malformed")
    if not isinstance(proposal.profile_hash, str):
        raise HTTPException(422, "Stored proposal policy fingerprint is malformed")
    if version != proposal.version:
        raise HTTPException(409, "Proposal changed; reload and review the new version")
    if not isinstance(proposal.status, str):
        raise HTTPException(422, "Stored proposal status is malformed")
    if proposal.status not in {"awaiting_customer", "awaiting_admin"}:
        raise HTTPException(409, "Proposal is not open for confirmation or approval")
    if not isinstance(proposal.payload, dict) or set(proposal.payload) != {
        "item_id", "item_name", "quantity", "unit_price", "discount_pct", "total",
        "currency", "slot_id", "slot_start", "resource",
    }:
        raise HTTPException(422, "Proposal payload is malformed")
    if _expiry(proposal.expires_at) <= datetime.now(timezone.utc):
        raise HTTPException(409, "Quote expired; request a new version")
    if proposal.profile_hash != profile.fingerprint:
        raise HTTPException(409, "Business policy changed; refresh the quote")

    payload = proposal.payload
    current = quote(
        db, profile, payload["item_id"], payload["quantity"], payload["discount_pct"], payload["slot_id"]
    )
    if current != payload:
        raise HTTPException(409, "Price or appointment changed; request a new version")
    if payload["slot_id"] and db.scalar(select(Booking).where(Booking.slot_id == payload["slot_id"])):
        raise HTTPException(409, "Slot already booked; choose another slot and refresh")


def transition(db, proposal, expected, new):
    # Compare-and-set also protects SQLite, where SELECT FOR UPDATE is not available.
    changed = db.execute(
        update(Proposal)
        .where(Proposal.id == proposal.id, Proposal.version == proposal.version, Proposal.status == expected)
        .values(status=new)
    )
    if changed.rowcount != 1:
        raise HTTPException(409, "Another request changed this proposal; reload")
    proposal.status = new


def audit(db, proposal, user, kind, approved, reason):
    db.add(
        Decision(
            proposal_id=proposal.id,
            version=proposal.version,
            actor_id=user.id,
            kind=kind,
            approved=approved,
            reason=reason,
        )
    )
    db.add(
        Trace(
            conversation_id=proposal.conversation_id,
            run_id=proposal.run_id,
            agent="policy",
            status="completed" if approved else "rejected",
            summary=f"{kind}: {'accepted' if approved else 'rejected'} by {user.name}",
            details={
                "proposal_id": proposal.id,
                "version": proposal.version,
                "reason": redact(reason),
                "actor_id": user.id,
                "actor_role": user.role,
                "profile_hash": proposal.profile_hash,
            },
        )
    )


def finish(db, proposal, status, text):
    conv = db.get(Conversation, proposal.conversation_id)
    conv.status, conv.updated_at = status, now()
    db.add(Message(conversation_id=conv.id, sender="system", content=text))


def confirm(db, profile, proposal_id, user, body):
    require_role(user, "customer", "operator", "admin")
    p = get_locked(db, proposal_id, user)
    if body.version != p.version:
        raise HTTPException(409, "Proposal changed; reload before deciding")
    if body.approved:
        validate(db, p, profile, body.version)
    if p.status == "awaiting_admin" and body.approved:
        return record(p)
    if p.status != "awaiting_customer":
        raise HTTPException(409, "Proposal is not awaiting customer confirmation")
    transition(db, p, "awaiting_customer", "awaiting_admin" if body.approved else "rejected")
    audit(
        db,
        p,
        user,
        "customer_consent" if user.role == "customer" else "simulated_customer_consent",
        body.approved,
        body.reason,
    )
    finish(
        db,
        p,
        "waiting_admin" if body.approved else "completed",
        "Customer accepted the exact offer. Waiting for an administrator; nothing has been booked yet."
        if body.approved
        else "Customer declined. No account or booking changes were made.",
    )
    return record(p)


def decide(db, profile, proposal_id, user, body):
    require_role(user, "admin")
    p = get_locked(db, proposal_id, user)
    if body.version != p.version:
        raise HTTPException(409, "Proposal version changed")
    receipt = db.scalar(select(Receipt).where(Receipt.proposal_id == p.id))
    if receipt and body.approved:
        return {"proposal": record(p), "receipt": record(receipt), "replayed": True}
    if not body.approved and p.status == "rejected":
        return {"proposal": record(p), "receipt": None, "replayed": True}
    if p.status != "awaiting_admin":
        raise HTTPException(409, "Explicit customer consent is required before approval")
    if not body.approved:
        if not body.reason.strip():
            raise HTTPException(422, "Please give a rejection reason")
        transition(db, p, "awaiting_admin", "rejected")
        audit(db, p, user, "admin_approval", False, body.reason)
        finish(
            db, p, "completed", f"The administrator rejected the offer: {body.reason}. No changes were made."
        )
        return {"proposal": record(p), "receipt": None, "replayed": False}
    validate(db, p, profile, body.version)
    consent = db.scalar(
        select(Decision).where(
            Decision.proposal_id == p.id,
            Decision.version == p.version,
            Decision.kind.in_(["customer_consent", "simulated_customer_consent"]),
            Decision.approved.is_(True),
        )
    )
    if not consent:
        raise HTTPException(409, "Valid consent missing")
    transition(db, p, "awaiting_admin", "executing")
    audit(db, p, user, "admin_approval", True, body.reason)
    conv = db.get(Conversation, p.conversation_id)
    service = ServiceRequest(
        proposal_id=p.id, customer_id=conv.customer_id, item_id=p.payload["item_id"], total=p.payload["total"]
    )
    db.add(service)
    if p.payload["slot_id"]:
        db.add(Booking(slot_id=p.payload["slot_id"], proposal_id=p.id))
    db.flush()  # Unique slot/proposal constraints arbitrate competing transactions.
    receipt = Receipt(
        proposal_id=p.id,
        payload={
            **p.payload,
            "service_request_id": service.id,
            "simulated": True,
            "profile_hash": p.profile_hash,
            "proposal_version": p.version,
        },
    )
    db.add(receipt)
    p.status = "succeeded"
    db.flush()
    finish(
        db,
        p,
        "completed",
        f"Approved and recorded in the sandbox. Receipt {receipt.id[:8]}. "
        "No real payment was charged. "
        + ("Your selected appointment is recorded." if p.payload["slot_id"] else ""),
    )
    db.add(
        Trace(
            conversation_id=conv.id,
            run_id=p.run_id,
            agent="executor",
            status="completed",
            summary="Sandbox service request committed",
            details={"receipt_id": receipt.id},
        )
    )
    return {"proposal": record(p), "receipt": record(receipt), "replayed": False}


def refresh(db, profile, proposal_id, user, body):
    require_role(user, "customer", "operator", "admin")
    p = get_locked(db, proposal_id, user)
    if p.status not in {"awaiting_customer", "awaiting_admin"} or p.version != body.version:
        raise HTTPException(409, "This proposal cannot be refreshed")
    payload = quote(
        db,
        profile,
        p.payload["item_id"],
        p.payload["quantity"],
        p.payload["discount_pct"],
        body.slot_id if body.slot_id else p.payload["slot_id"],
    )
    updated = db.execute(
        update(Proposal)
        .where(
            Proposal.id == p.id,
            Proposal.version == body.version,
            Proposal.status.in_(["awaiting_customer", "awaiting_admin"]),
        )
        .values(
            version=body.version + 1,
            payload=payload,
            profile_hash=profile.fingerprint,
            expires_at=deadline(profile),
            status="awaiting_customer",
        )
    )
    if updated.rowcount != 1:
        raise HTTPException(409, "Another request changed the proposal")
    db.refresh(p)
    finish(
        db,
        p,
        "waiting_customer",
        "Offer refreshed. Previous consent and approval no longer apply; please review again.",
    )
    db.add(
        Trace(
            conversation_id=p.conversation_id,
            run_id=p.run_id,
            agent="policy",
            status="waiting",
            summary="New proposal version requires fresh consent",
            details={"version": p.version},
        )
    )
    return record(p)
