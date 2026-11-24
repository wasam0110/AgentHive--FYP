from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Login(StrictModel):
    email: str = Field(min_length=3, max_length=150)
    password: str = Field(min_length=1, max_length=256)


class NewConversation(StrictModel):
    customer_id: str | None = None  # Staff simulation only; never trusted for customers.
    language: Literal["en", "ur", "roman-ur"] = "en"
    connection_id: str | None = None


class NewMessage(StrictModel):
    content: str = Field(min_length=1, max_length=4000)
    item_id: str | None = None
    slot_id: str | None = None
    quantity: int = Field(default=1, ge=1, le=100)
    discount_pct: int = Field(default=0, ge=0, le=100)


class ProposalDecision(StrictModel):
    version: int = Field(ge=1)
    approved: bool
    reason: str = Field(default="", max_length=500)


class RefreshProposal(StrictModel):
    version: int = Field(ge=1)
    slot_id: str | None = None


class Intake(StrictModel):
    support: bool = False
    sales: bool = False
    scheduling: bool = False
    manual: bool = False
    language: Literal["en", "ur", "roman-ur"] = "en"


class Intent(StrictModel):
    intent_type: Literal[
        "support_complaint",
        "catalog_enquiry",
        "service_request",
        "resource_appointment",
        "discount_request",
        "refund_cancellation",
        "unclear",
    ]
    confidence: Literal["high", "medium", "low"] = "medium"
    entities: dict = Field(default_factory=dict)
    missing_fields: list[str] = Field(default_factory=list)


class IntakeOutput(StrictModel):
    conversation_id: str
    run_id: str
    raw_message: str
    language_detected: Literal["en", "ur", "roman-ur"]
    intents: list[Intent] = Field(min_length=1)
    clarification_needed: bool = False
    clarification_question: str | None = None


class TaskDefinition(StrictModel):
    task_id: str
    run_id: str
    conversation_id: str
    intent_type: str
    assigned_worker: Literal["support", "sales", "scheduling"]
    dependencies: list[str] = Field(default_factory=list)
    input_payload: dict = Field(default_factory=dict)
    created_at: str
