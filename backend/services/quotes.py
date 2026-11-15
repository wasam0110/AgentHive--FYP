"""Build deterministic quotes from the active profile and authoritative catalog data."""

from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from fastapi import HTTPException

from backend.db.models import CatalogItem, Slot

CENT = Decimal("0.01")


def _money(value: str) -> Decimal:
    if not isinstance(value, str):
        raise HTTPException(422, "Catalog price must be stored as a decimal string")
    try:
        amount = Decimal(value)
        rounded = amount.quantize(CENT)
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise HTTPException(422, "Catalog price is invalid") from exc
    if not amount.is_finite() or amount < 0 or rounded != amount:
        raise HTTPException(422, "Catalog price must be a non-negative amount with at most two decimals")
    return amount


def _timestamp(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, TypeError, ValueError) as exc:
        raise HTTPException(422, "Appointment time is invalid") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise HTTPException(422, "Appointment time must include a timezone")
    return parsed.astimezone(timezone.utc)


def quote(db, profile, item_id, quantity, discount_pct, slot_id=None):
    """Return canonical quote terms; never accepts a model-supplied price."""
    if isinstance(quantity, bool) or not isinstance(quantity, int) or not 1 <= quantity <= 100:
        raise HTTPException(422, "Quantity must be between 1 and 100")
    if (
        isinstance(discount_pct, bool)
        or not isinstance(discount_pct, int)
        or not 0 <= discount_pct <= profile.policy.max_discount_pct
    ):
        raise HTTPException(422, "Discount is outside the active business policy")
    if item_id is not None and (not isinstance(item_id, str) or not item_id.strip()):
        raise HTTPException(422, "Catalog item identifier is invalid")
    if slot_id is not None and (not isinstance(slot_id, str) or not slot_id.strip()):
        raise HTTPException(422, "Appointment identifier is invalid")

    item = db.get(CatalogItem, item_id) if item_id is not None else None
    if item_id is not None and (
        "catalog_quote" not in profile.capabilities
        or item is None
        or item.business_id != profile.business_id
        or not item.active
    ):
        raise HTTPException(422, "Catalog item is unavailable")
    if item is None and discount_pct:
        raise HTTPException(422, "A discount requires a catalog item")

    slot = db.get(Slot, slot_id) if slot_id is not None else None
    if slot_id is not None and (
        "resource_booking" not in profile.capabilities
        or slot is None
        or slot.business_id != profile.business_id
        or not slot.active
    ):
        raise HTTPException(422, "Appointment is unavailable or booking is disabled")
    if slot is not None:
        starts_at = _timestamp(slot.starts_at)
        ends_at = _timestamp(slot.ends_at)
        if starts_at <= datetime.now(timezone.utc) or ends_at <= starts_at:
            raise HTTPException(422, "Appointment time is unavailable")

    unit_price = _money(item.price) if item is not None else Decimal("0.00")
    try:
        total = (unit_price * quantity * Decimal(100 - discount_pct) / Decimal(100)).quantize(
            CENT, rounding=ROUND_HALF_UP
        )
    except InvalidOperation as exc:
        raise HTTPException(422, "Quote total is outside the supported monetary range") from exc
    return {
        "item_id": item_id,
        "item_name": item.name if item is not None else "Appointment",
        "quantity": quantity,
        "unit_price": str(unit_price),
        "discount_pct": discount_pct,
        "total": str(total),
        "currency": profile.currency,
        "slot_id": slot_id,
        "slot_start": slot.starts_at if slot is not None else None,
        "resource": slot.resource if slot is not None else None,
    }
