"""Database-leased jobs: safe read-stage retries and atomic final materialization."""

import asyncio
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import or_, select, update

from backend.db.models import Conversation, Message, Proposal, Run, Ticket, Trace, now
from backend.services.approvals import deadline
from backend.services.quotes import quote
from backend.services.redaction import redact


def claim(factory):
    with factory.begin() as db:
        run = db.scalar(
            select(Run)
            .where(or_(Run.status == "queued", (Run.status == "running") & (Run.lease_until < now())))
            .order_by(Run.created_at)
            .limit(1)
        )
        if not run:
            return None
        token = str(uuid4())
        changed = db.execute(
            update(Run)
            .where(
                Run.id == run.id,
                or_(Run.status == "queued", (Run.status == "running") & (Run.lease_until < now())),
            )
            .values(
                status="running",
                lease_token=token,
                attempts=Run.attempts + 1,
                lease_until=(datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat(),
            )
        )
        if changed.rowcount != 1:
            return None
        conv = db.get(Conversation, run.conversation_id)
        conv.status = "running"
        return {
            "id": run.id,
            "token": token,
            "input": {**run.input, "_customer_id": conv.customer_id, "_connection_id": conv.connection_id},
            "language": conv.language,
            "attempts": run.attempts,
        }


def materialize(db, profile, run, outcome):
    conv = db.get(Conversation, run.conversation_id)
    results, message = outcome["results"], run.input
    for result in results:
        db.add(
            Trace(
                conversation_id=conv.id,
                run_id=run.id,
                agent=result["worker"],
                status=result["status"],
                summary=redact(result["summary"]),
                details=redact(result),
            )
        )
    summaries = [x["summary"] for x in results]
    intents = outcome["intents"]
    if intents["manual"]:
        db.add(
            Ticket(
                run_id=run.id,
                customer_id=conv.customer_id,
                category="manual_review",
                summary=message["content"][:500],
            )
        )
    elif intents["support"]:
        db.add(
            Ticket(
                run_id=run.id,
                customer_id=conv.customer_id,
                category="support",
                summary=message["content"][:500],
            )
        )
    if intents["manual"] or intents["support"]:
        db.flush()
        ticket = db.scalar(select(Ticket).where(Ticket.run_id == run.id))
        summaries.append(f"Support ticket {ticket.id} recorded ({ticket.status}). No repair has been confirmed.")
    active = {x["worker"] for x in results if x["status"] == "completed"}
    wants_sales = intents["sales"] and "sales" in active
    wants_booking = intents["scheduling"] and "scheduling" in active
    missing = (wants_sales and not message.get("item_id")) or (wants_booking and not message.get("slot_id"))
    if intents["manual"] and (wants_sales or wants_booking):
        summaries.append(
            "A purchase/booking conflicts with the cancellation request. Please clarify before proceeding."
        )
        missing = True
    conv.status = "waiting_customer" if missing else "completed"
    if missing:
        summaries.append(
            "Please select a catalog item and/or an available appointment in the composer, then send your request again."
        )
    elif wants_sales or wants_booking:
        try:
            payload = quote(
                db,
                profile,
                message.get("item_id") if wants_sales else None,
                message["quantity"],
                message["discount_pct"],
                message.get("slot_id") if wants_booking else None,
            )
            refs = [e for result in results for e in result["evidence"]]
            p = Proposal(
                conversation_id=conv.id,
                run_id=run.id,
                payload=payload,
                evidence=refs,
                expires_at=deadline(profile),
                profile_hash=profile.fingerprint,
            )
            db.add(p)
            conv.status = "waiting_customer"
            summaries.append(
                f"Offer prepared: {payload['currency']} {payload['total']}. Review and confirm the exact proposal below. Nothing has been booked or charged."
            )
        except HTTPException as exc:
            summaries.append(str(exc.detail))
            conv.status = "waiting_customer"
    if not results:
        summaries.append("Please describe your support question, catalog enquiry or appointment request.")
        conv.status = "waiting_customer"
    if any(x["status"] == "failed" for x in results) and conv.status == "completed":
        conv.status = "partially_completed"
    db.add(Message(conversation_id=conv.id, sender="system", content="\n\n".join(summaries)))
    db.add(
        Trace(
            conversation_id=conv.id,
            run_id=run.id,
            agent="supervisor",
            status=conv.status,
            summary="Results combined; proposal controls enforced by backend.",
            details={"intents": intents},
        )
    )
    conv.updated_at = now()
    run.status, run.completed_at, run.checkpoint = "completed", now(), outcome
    run.lease_until = None


async def process_one(factory, profile, workflow):
    job = claim(factory)
    if not job:
        return False
    try:
        if job["attempts"] > 3:
            raise RuntimeError("Job retry budget exceeded")
        outcome = await workflow.run(job["input"], job["language"])
        with factory.begin() as db:
            run = db.scalar(select(Run).where(Run.id == job["id"]).with_for_update())
            if run.lease_token != job["token"] or run.status != "running":
                return True  # A new worker owns the lease; discard these read-only results.
            materialize(db, profile, run, outcome)
    except Exception:
        with factory.begin() as db:
            run = db.get(Run, job["id"])
            if run.lease_token == job["token"] and run.status == "running":
                run.status, run.completed_at = "failed", now()
                conv = db.get(Conversation, run.conversation_id)
                conv.status = "failed"
                db.add(
                    Message(
                        conversation_id=conv.id,
                        sender="system",
                        content="The workflow failed. No proposed action was executed. Please retry or contact an operator.",
                    )
                )
                db.add(
                    Trace(
                        conversation_id=conv.id,
                        run_id=run.id,
                        agent="supervisor",
                        status="failed",
                        summary="Workflow unavailable; check configured provider and data services.",
                        details={},
                    )
                )
    return True


async def worker_loop(app):
    while True:
        worked = await process_one(app.state.db, app.state.profile, app.state.workflow)
        await asyncio.sleep(0.1 if worked else 0.8)
