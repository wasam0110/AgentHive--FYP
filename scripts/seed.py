"""Create only synthetic records and demo accounts; rerunning never resets passwords."""

import os
from datetime import datetime, timedelta, timezone
from sqlalchemy import select

from backend.config import ROOT, Settings
from scripts.seed_fixtures import load_fixture
from backend.db.connection import connect
from backend.db.models import Business, CatalogItem, Customer, Slot, User, ServiceConnection, AreaIncident
from backend.rag.retriever import Retriever
from backend.services.security import passwords


def seed(settings, password):
    if len(password) < 12:
        raise ValueError("Choose DEMO_PASSWORD with at least 12 characters")
    profile = settings.profile()
    fixture = load_fixture(profile)
    engine, factory = connect(settings.database_url)
    with factory.begin() as db:
        existing = db.scalar(select(Business))
        if existing and existing.id != profile.business_id:
            raise ValueError("Use a separate database for each business; refusing to mix records")
        if not existing:
            db.add(Business(id=profile.business_id, fingerprint=profile.fingerprint))
        prefix = profile.business_id
        for i, name in enumerate(fixture.customers):
            id = f"{prefix}-customer-{i + 1}"
            if not db.get(Customer, id):
                db.add(Customer(id=id, business_id=prefix, name=name, email=f"customer{i + 1}@example.test"))
        db.flush()
        for i, connection in enumerate(fixture.connections, 1):
            id = f"{prefix}-connection-{i}"
            if not db.get(ServiceConnection, id):
                db.add(ServiceConnection(id=id, business_id=prefix,
                    customer_id=f"{prefix}-customer-{connection.customer}", synthetic=True,
                    **connection.model_dump(exclude={"customer"})))
        for i, incident in enumerate(fixture.incidents, 1):
            id = f"{prefix}-incident-{i}"
            if not db.get(AreaIncident, id):
                stamp = datetime.now(timezone.utc)
                db.add(AreaIncident(id=id, business_id=prefix, synthetic=True, status="active",
                    starts_at=stamp.isoformat(), ends_at=(stamp + timedelta(days=7)).isoformat(),
                    **incident.model_dump()))
        for i, item in enumerate(fixture.items):
            name, desc, price = item.name, item.description, item.price
            id = f"{prefix}-item-{i + 1}"
            if not db.get(CatalogItem, id):
                db.add(CatalogItem(id=id, business_id=prefix, name=name, description=desc, price=price))
        if "resource_booking" in profile.capabilities:
            start = datetime.now(timezone.utc).replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(
                days=1
            )
            for i in range(8):
                stamp = start + timedelta(days=i // 2, hours=2 * (i % 2))
                id = f"{prefix}-slot-{stamp:%Y%m%d%H%M}"
                if not db.get(Slot, id):
                    db.add(
                        Slot(
                            id=id,
                            business_id=prefix,
                            resource=fixture.resource_label + " " + str(i % 2 + 1),
                            starts_at=stamp.isoformat(),
                            ends_at=(stamp + timedelta(hours=1)).isoformat(),
                        )
                    )
        for role in ["admin", "operator", "evaluator", "customer"]:
            email = f"{role}@agenthive.test"
            if not db.scalar(select(User).where(User.email == email)):
                db.add(
                    User(
                        business_id=prefix,
                        email=email,
                        password_hash=passwords.hash(password),
                        role=role,
                        name=role.title() + " Demo",
                        customer_id=f"{prefix}-customer-1" if role == "customer" else None,
                    )
                )
        for i in range(2, len(fixture.customers) + 1):
            email = f"customer{i}@agenthive.test"
            if not db.scalar(select(User).where(User.email == email)):
                db.add(User(business_id=prefix, email=email, password_hash=passwords.hash(password),
                            role="customer", name=f"Customer {i} Demo", customer_id=f"{prefix}-customer-{i}"))
    Retriever(settings.chroma_path, profile, settings.embedding_mode).ingest(
        ROOT / "backend/rag/knowledge" / fixture.knowledge_directory
    )
    engine.dispose()


if __name__ == "__main__":
    settings = Settings.from_env()  # Load .env before reading the seed password.
    password = os.environ.get("DEMO_PASSWORD", "")
    seed(settings, password)
    print("Synthetic data/index ready. Sign in as admin@agenthive.test using your DEMO_PASSWORD.")
