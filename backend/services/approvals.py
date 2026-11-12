"""Proposal validation shared by later consent and approval handlers."""

from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select

from backend.db.models import Booking, Proposal
from backend.services.quotes import quote

PAYLOAD_FIELDS = {
    "item_id",
    "item_name",
    "quantity",
    "unit_price",
    "discount_pct",
    "total",
    "currency",
    "slot_id",
    "slot_start",
    "resource",
}


def _expiry(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, TypeError, ValueError) as exc:
        raise HTTPException(422, "Proposal expiry is malformed") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise HTTPException(422, "Proposal expiry must include a timezone")
    return parsed.astimezone(timezone.utc)


def validate(db, proposal: Proposal, profile, version: int) -> None:
    """Validate terms only; the caller must separately authenticate and authorize the actor."""
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
        raise HTTPException(409, "Proposal changed; reload and review the current version")
    if not isinstance(proposal.status, str):
        raise HTTPException(422, "Stored proposal status is malformed")
    if proposal.status not in {"awaiting_customer", "awaiting_admin"}:
        raise HTTPException(409, "Proposal is not open for confirmation or approval")
    if not isinstance(proposal.payload, dict) or set(proposal.payload) != PAYLOAD_FIELDS:
        raise HTTPException(422, "Proposal payload is malformed")
    if _expiry(proposal.expires_at) <= datetime.now(timezone.utc):
        raise HTTPException(409, "Quote expired; request a new version")
    if proposal.profile_hash != profile.fingerprint:
        raise HTTPException(409, "Business policy changed; refresh the quote")

    payload = proposal.payload
    current = quote(db, profile, payload["item_id"], payload["quantity"],
                    payload["discount_pct"], payload["slot_id"])
    if current != payload:
        raise HTTPException(409, "Price or appointment changed; request a new version")
    if payload["slot_id"] and db.scalar(
        select(Booking).where(Booking.slot_id == payload["slot_id"])
    ) is not None:
        raise HTTPException(409, "Appointment is already booked; select another time")
