"""Customer service context and time-bounded area incidents."""
from alembic import op
import sqlalchemy as sa
revision = "20261104_context"
down_revision = "1e58c02f5ad2"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("service_connections",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("business_id", sa.String(), nullable=False),
        sa.Column("customer_id", sa.String(), sa.ForeignKey("customers.id"), nullable=False),
        *[sa.Column(name, sa.String(), nullable=False) for name in
          ["label", "city", "area", "address", "plan", "account_status"]],
        sa.Column("synthetic", sa.Boolean(), nullable=False))
    op.create_table("area_incidents",
        sa.Column("id", sa.String(), primary_key=True),
        *[sa.Column(name, sa.String(), nullable=False) for name in
          ["business_id", "city", "area", "summary", "status", "starts_at", "ends_at"]],
        sa.Column("synthetic", sa.Boolean(), nullable=False))
    if op.get_bind().dialect.name == "sqlite":
        # A nullable inline reference can be added without rebuilding a referenced table.
        op.execute("ALTER TABLE conversations ADD COLUMN connection_id VARCHAR REFERENCES service_connections (id)")
    else:
        op.add_column("conversations", sa.Column("connection_id", sa.String(), nullable=True))
        op.create_foreign_key("fk_conversation_connection", "conversations", "service_connections", ["connection_id"], ["id"])


def downgrade():
    if op.get_bind().dialect.name != "sqlite":
        op.drop_constraint("fk_conversation_connection", "conversations", type_="foreignkey")
    op.drop_column("conversations", "connection_id")
    op.drop_table("area_incidents")
    op.drop_table("service_connections")
