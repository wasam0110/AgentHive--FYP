"""Read registered service records; never infer identity or a diagnosis from message text."""
from fastapi import HTTPException
from sqlalchemy import select
from backend.db.models import Customer, ServiceConnection, AreaIncident, now
from backend.services.data import record


def connections(db, business_id, customer_id):
    customer = db.get(Customer, customer_id) if customer_id else None
    if not customer or customer.business_id != business_id:
        raise HTTPException(404, "Customer not found")
    return list(db.scalars(select(ServiceConnection).where(
        ServiceConnection.business_id == business_id,
        ServiceConnection.customer_id == customer_id).order_by(ServiceConnection.id)))


def select_connection(db, profile, customer_id, connection_id):
    """Validate explicit ownership, or select the sole connection. Never guess among several."""
    if "service_context" not in profile.capabilities:
        if connection_id:
            raise HTTPException(422, "Service context is not enabled")
        return None
    rows = connections(db, profile.business_id, customer_id)
    if connection_id:
        if not any(c.id == connection_id for c in rows):
            raise HTTPException(422, "Choose one of this customer's connections")
        return connection_id
    return rows[0].id if len(rows) == 1 else None


def context(db, profile, customer_id, connection_id=None):
    rows = connections(db, profile.business_id, customer_id)
    chosen = next((c for c in rows if c.id == connection_id), None)
    if connection_id and chosen is None:
        raise HTTPException(422, "Connection no longer belongs to this customer")
    if chosen is None and len(rows) == 1:
        chosen = rows[0]
    checked = now()
    incidents = []
    if chosen:
        incidents = list(db.scalars(select(AreaIncident).where(
            AreaIncident.business_id == profile.business_id,
            AreaIncident.city == chosen.city, AreaIncident.area == chosen.area,
            AreaIncident.status == "active", AreaIncident.starts_at <= checked,
            AreaIncident.ends_at > checked).order_by(AreaIncident.id)))
    return {"connections": [record(c) for c in rows],
            "selected": record(chosen) if chosen else None,
            "incidents": [record(i) for i in incidents], "checked_at": checked}


def evidence(factory, profile, customer_id, connection_id):
    """Return deterministic account/status evidence; no network checks or data writes."""
    with factory() as db:
        data = context(db, profile, customer_id, connection_id)
    c = data["selected"]
    if not c:
        text = ("Multiple connections are registered. Start a new conversation and choose the affected connection."
                if data["connections"] else
                "No service connection is registered. Please provide your city and area for staff review; coverage is unconfirmed.")
        return [{"source_type": "database", "source_id": "service-context", "excerpt": text}]
    label = "Synthetic demo record" if c["synthetic"] else "Registered service record"
    text = (f"{label}: {c['label']}; {c['city']}, {c['area']}; address: {c['address']}; "
            f"plan: {c['plan']}; account status: {c['account_status']}. ")
    if not data["incidents"]:
        text += "No active area incident is recorded. This does not establish that the connection is healthy. Please describe the symptoms and device indicators; live diagnostics are unavailable."
    refs = [{"source_type": "database", "source_id": f"connection:{c['id']}", "excerpt": text}]
    for i in data["incidents"]:
        label = "Synthetic demo incident" if i["synthetic"] else "Recorded area incident"
        refs.append({"source_type": "database", "source_id": f"incident:{i['id']}",
                     "excerpt": f"{label}: {i['summary']} Checked {data['checked_at']}. This may explain the symptoms; no individual line diagnosis or repair is confirmed."})
    return refs
