"""Read-only specialist tools. Tool output never grants authority to write."""

from sqlalchemy import select
from backend.db.models import CatalogItem, Ticket
from backend.services.data import available


def catalog(factory, profile, item_id):
    """Return authoritative eligible catalog records, bounded to the active business."""
    with factory() as db:
        query = select(CatalogItem).where(
            CatalogItem.business_id == profile.business_id, CatalogItem.active.is_(True)
        )
        if item_id:
            query = query.where(CatalogItem.id == item_id)
        rows = list(db.scalars(query.limit(20)))
        if item_id and not rows:
            raise ValueError("Selected item is unavailable")
        return [
            {
                "source_type": "database",
                "source_id": f"catalog:{item.id}",
                "excerpt": f"{item.name}: {profile.currency} {item.price} per unit. {item.description}",
            }
            for item in rows
        ]


def appointments(factory, profile, slot_id):
    """Read current unreserved availability; the executor will check again."""
    with factory() as db:
        slots = available(db, profile.business_id)
    if slot_id:
        slots = [s for s in slots if s["id"] == slot_id]
        if not slots:
            raise ValueError("Selected appointment is unavailable")
    return [
        {
            "source_type": "database",
            "source_id": f"slot:{s['id']}",
            "excerpt": f"{s['resource']} available at {s['starts_at']} UTC; no hold is created.",
        }
        for s in slots[:20]
    ]


def support_context(factory, customer_id):
    """Read bounded ticket history for server-bound identity, never an ID in model text."""
    with factory() as db:
        tickets = list(db.scalars(select(Ticket).where(Ticket.customer_id == customer_id).limit(10)))
        return [
            {
                "source_type": "database",
                "source_id": f"ticket:{t.id}",
                "excerpt": f"Previous {t.category} ticket status: {t.status}.",
            }
            for t in tickets
        ]
