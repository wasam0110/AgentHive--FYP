"""Code-registered synthetic fixtures; profile values never become file paths."""

from pydantic import BaseModel, ConfigDict, Field, model_validator

from backend.config import ROOT

FIXTURES = {
    "demo-a-knowledge": "demo-a",
    "demo-b-knowledge": "demo-b",
}


class SeedItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str
    description: str
    price: str = Field(pattern=r"^\d+\.\d{2}$")


class SeedConnection(BaseModel):
    model_config = ConfigDict(extra="forbid")
    customer: int = Field(ge=1)
    label: str = Field(min_length=1)
    city: str = Field(min_length=1)
    area: str = Field(min_length=1)
    address: str = Field(min_length=1)
    plan: str = Field(min_length=1)
    account_status: str = Field(pattern="^(active|suspended|unknown)$")


class SeedIncident(BaseModel):
    model_config = ConfigDict(extra="forbid")
    city: str = Field(min_length=1)
    area: str = Field(min_length=1)
    summary: str = Field(min_length=1)


class SeedFixture(BaseModel):
    model_config = ConfigDict(extra="forbid")
    knowledge_directory: str
    catalog_reference: str | None
    resource_reference: str | None
    customers: list[str] = Field(min_length=1)
    resource_label: str
    items: list[SeedItem]
    connections: list[SeedConnection] = Field(default_factory=list)
    incidents: list[SeedIncident] = Field(default_factory=list)

    @model_validator(mode="after")
    def customer_bounds(self):
        if any(connection.customer > len(self.customers) for connection in self.connections):
            raise ValueError("Connection references an unknown fixture customer")
        return self


def load_fixture(profile):
    """Validate all fixture references before opening the database or writing records."""
    key = FIXTURES.get(profile.knowledge_source)
    if not key:
        raise ValueError("No sandbox dataset registered for this knowledge reference")
    fixture = SeedFixture.model_validate_json(
        (ROOT / "examples/seed-fixtures" / f"{key}.json").read_text(encoding="utf-8")
    )
    if (
        fixture.knowledge_directory != key
        or profile.catalog != fixture.catalog_reference
        or profile.resources != fixture.resource_reference
    ):
        raise ValueError("Sandbox catalog/resources references do not match the registered fixture")
    return fixture
