"""Small relational records; JSON is used only for validated workflow snapshots."""

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import JSON, Boolean, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def uid():
    return str(uuid4())


def now():
    return datetime.now(timezone.utc).isoformat()


class Base(DeclarativeBase):
    pass


class Business(Base):
    __tablename__ = "business"
    id: Mapped[str] = mapped_column(primary_key=True)
    fingerprint: Mapped[str]


class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(primary_key=True, default=uid)
    business_id: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    password_hash: Mapped[str]
    role: Mapped[str]
    customer_id: Mapped[str | None]
    name: Mapped[str]


class AuthSession(Base):
    __tablename__ = "auth_sessions"
    token_hash: Mapped[str] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    csrf: Mapped[str]
    expires_at: Mapped[str]


class Customer(Base):
    __tablename__ = "customers"
    id: Mapped[str] = mapped_column(primary_key=True)
    business_id: Mapped[str]
    name: Mapped[str]
    email: Mapped[str]


class ServiceConnection(Base):
    __tablename__ = "service_connections"
    id: Mapped[str] = mapped_column(primary_key=True)
    business_id: Mapped[str]
    customer_id: Mapped[str] = mapped_column(ForeignKey("customers.id"))
    label: Mapped[str]
    city: Mapped[str]
    area: Mapped[str]
    address: Mapped[str]
    plan: Mapped[str]
    account_status: Mapped[str]
    synthetic: Mapped[bool] = mapped_column(Boolean)


class AreaIncident(Base):
    __tablename__ = "area_incidents"
    id: Mapped[str] = mapped_column(primary_key=True)
    business_id: Mapped[str]
    city: Mapped[str]
    area: Mapped[str]
    summary: Mapped[str]
    status: Mapped[str]
    starts_at: Mapped[str]
    ends_at: Mapped[str]
    synthetic: Mapped[bool] = mapped_column(Boolean)


class CatalogItem(Base):
    __tablename__ = "catalog"
    id: Mapped[str] = mapped_column(primary_key=True)
    business_id: Mapped[str]
    name: Mapped[str]
    description: Mapped[str]
    price: Mapped[str]  # Decimal serialized as string, never float arithmetic.
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class Slot(Base):
    __tablename__ = "slots"
    id: Mapped[str] = mapped_column(primary_key=True)
    business_id: Mapped[str]
    resource: Mapped[str]
    starts_at: Mapped[str]
    ends_at: Mapped[str]
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class Conversation(Base):
    __tablename__ = "conversations"
    id: Mapped[str] = mapped_column(primary_key=True, default=uid)
    business_id: Mapped[str]
    customer_id: Mapped[str] = mapped_column(ForeignKey("customers.id"))
    status: Mapped[str] = mapped_column(default="queued")
    connection_id: Mapped[str | None] = mapped_column(ForeignKey("service_connections.id"))
    title: Mapped[str] = mapped_column(default="New conversation")
    language: Mapped[str] = mapped_column(default="en")
    created_at: Mapped[str] = mapped_column(default=now)
    updated_at: Mapped[str] = mapped_column(default=now)


class Message(Base):
    __tablename__ = "messages"
    id: Mapped[str] = mapped_column(primary_key=True, default=uid)
    conversation_id: Mapped[str] = mapped_column(ForeignKey("conversations.id"))
    sender: Mapped[str]
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[str] = mapped_column(default=now)


class Run(Base):
    __tablename__ = "runs"
    __table_args__ = (UniqueConstraint("conversation_id", "request_key"),)
    id: Mapped[str] = mapped_column(primary_key=True, default=uid)
    conversation_id: Mapped[str] = mapped_column(ForeignKey("conversations.id"))
    request_key: Mapped[str]
    request_hash: Mapped[str]
    status: Mapped[str] = mapped_column(default="queued")
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    lease_until: Mapped[str | None]
    lease_token: Mapped[str | None]
    input: Mapped[dict] = mapped_column(JSON)
    checkpoint: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[str] = mapped_column(default=now)
    completed_at: Mapped[str | None]


class Trace(Base):
    __tablename__ = "traces"
    sequence: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    conversation_id: Mapped[str] = mapped_column(ForeignKey("conversations.id"))
    run_id: Mapped[str | None]
    agent: Mapped[str]
    status: Mapped[str]
    summary: Mapped[str] = mapped_column(Text)
    details: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[str] = mapped_column(default=now)


class Proposal(Base):
    __tablename__ = "proposals"
    id: Mapped[str] = mapped_column(primary_key=True, default=uid)
    conversation_id: Mapped[str] = mapped_column(ForeignKey("conversations.id"))
    run_id: Mapped[str] = mapped_column(ForeignKey("runs.id"), unique=True)
    version: Mapped[int] = mapped_column(default=1)
    profile_hash: Mapped[str]
    status: Mapped[str] = mapped_column(default="awaiting_customer")
    payload: Mapped[dict] = mapped_column(JSON)
    evidence: Mapped[list] = mapped_column(JSON)
    expires_at: Mapped[str]
    created_at: Mapped[str] = mapped_column(default=now)


class Decision(Base):
    __tablename__ = "decisions"
    id: Mapped[str] = mapped_column(primary_key=True, default=uid)
    proposal_id: Mapped[str] = mapped_column(ForeignKey("proposals.id"))
    version: Mapped[int]
    actor_id: Mapped[str]
    kind: Mapped[str]
    approved: Mapped[bool]
    reason: Mapped[str]
    created_at: Mapped[str] = mapped_column(default=now)


class Receipt(Base):
    __tablename__ = "receipts"
    id: Mapped[str] = mapped_column(primary_key=True, default=uid)
    proposal_id: Mapped[str] = mapped_column(ForeignKey("proposals.id"), unique=True)
    payload: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[str] = mapped_column(default=now)


class ServiceRequest(Base):
    __tablename__ = "service_requests"
    id: Mapped[str] = mapped_column(primary_key=True, default=uid)
    proposal_id: Mapped[str] = mapped_column(ForeignKey("proposals.id"), unique=True)
    customer_id: Mapped[str]
    item_id: Mapped[str | None]
    total: Mapped[str]


class Booking(Base):
    __tablename__ = "bookings"
    id: Mapped[str] = mapped_column(primary_key=True, default=uid)
    slot_id: Mapped[str] = mapped_column(ForeignKey("slots.id"), unique=True)
    proposal_id: Mapped[str] = mapped_column(ForeignKey("proposals.id"), unique=True)


class Ticket(Base):
    __tablename__ = "tickets"
    id: Mapped[str] = mapped_column(primary_key=True, default=uid)
    run_id: Mapped[str] = mapped_column(ForeignKey("runs.id"), unique=True)
    customer_id: Mapped[str]
    category: Mapped[str]
    status: Mapped[str] = mapped_column(default="open")
    summary: Mapped[str]
