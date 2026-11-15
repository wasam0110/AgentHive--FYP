from fastapi import HTTPException
from sqlalchemy import select
from backend.db.models import Booking, CatalogItem, Conversation, Customer, Slot, now


def record(row):
    return {column.name: getattr(row, column.name) for column in row.__table__.columns}


def conversation_for(db, id, user):
    row = db.get(Conversation, id)
    if not row or row.business_id != user.business_id:
        raise HTTPException(404, "Conversation not found")
    if user.role == "customer" and row.customer_id != user.customer_id:
        raise HTTPException(404, "Conversation not found")
    return row


def available(db, business_id):
    booked = select(Booking.slot_id)
    return [
        record(s)
        for s in db.scalars(
            select(Slot)
            .where(
                Slot.business_id == business_id,
                Slot.active.is_(True),
                Slot.starts_at > now(),
                Slot.id.not_in(booked),
            )
            .order_by(Slot.starts_at)
        )
    ]


def snapshot(db, business_id):
    return {
        "customers": [
            record(c) for c in db.scalars(select(Customer).where(Customer.business_id == business_id))
        ],
        "catalog": [
            record(c)
            for c in db.scalars(
                select(CatalogItem).where(
                    CatalogItem.business_id == business_id, CatalogItem.active.is_(True)
                )
            )
        ],
        "slots": available(db, business_id),
    }
