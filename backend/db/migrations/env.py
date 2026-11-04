from alembic import context
from backend.config import Settings
from backend.db.connection import connect
from backend.db.models import Base

engine, _ = connect(Settings.from_env().database_url)
with engine.connect() as connection:
    context.configure(connection=connection, target_metadata=Base.metadata, compare_type=True)
    with context.begin_transaction():
        context.run_migrations()
