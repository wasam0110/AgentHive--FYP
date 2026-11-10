"""Explicit environment configuration and validated business profiles."""

import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal
from zoneinfo import ZoneInfo

import pycountry
from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, Field, model_validator

ROOT = Path(__file__).resolve().parents[1]
CAPABILITIES = {"knowledge_answer", "catalog_quote", "resource_booking", "reference_information", "service_context"}


class Policy(BaseModel):
    model_config = ConfigDict(extra="forbid")
    max_discount_pct: int = Field(ge=0, le=100)
    quote_expiry_minutes: int = Field(gt=0, le=1440)
    approval_expiry_hours: int = Field(gt=0, le=168)


class Adapters(BaseModel):
    model_config = ConfigDict(extra="forbid")
    data: Literal["sandbox_v1"]
    execution: Literal["sandbox_v1"]


class Profile(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal[1]
    business_id: str = Field(pattern=r"^[a-z0-9-]{1,48}$")
    display_name: str = Field(min_length=1, max_length=100)
    timezone: str
    currency: str
    languages: list[Literal["en", "ur", "roman-ur"]] = Field(min_length=1)
    terminology: dict[str, str]
    capabilities: list[str] = Field(min_length=1)
    adapters: Adapters
    knowledge_source: str | None
    catalog: str | None
    resources: str | None
    policy: Policy
    reference_catalog: str | None = None

    @model_validator(mode="after")
    def check_profile(self):
        ZoneInfo(self.timezone)
        if not pycountry.currencies.get(alpha_3=self.currency):
            raise ValueError("Unknown ISO currency")
        if not set(self.capabilities) <= CAPABILITIES:
            raise ValueError("Unknown capability")
        for capability, reference in [
            ("knowledge_answer", self.knowledge_source),
            ("catalog_quote", self.catalog),
            ("resource_booking", self.resources),
            ("reference_information", self.reference_catalog),
        ]:
            if capability in self.capabilities and not reference:
                raise ValueError(f"Missing reference for {capability}")
        return self

    @property
    def fingerprint(self) -> str:
        """Hash content, not schema version, to invalidate approvals after policy edits."""
        encoded = json.dumps(self.model_dump(), sort_keys=True).encode()
        return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class Settings:
    database_url: str
    profile_path: str
    chroma_path: str
    mode: str
    frontend_origin: str
    secure_cookie: bool
    model_url: str
    model_name: str
    model_key: str
    embedding_mode: str
    worker_enabled: bool = True

    @classmethod
    def from_env(cls):
        load_dotenv(ROOT / ".env", override=False)
        mode = os.environ.get("AGENT_MODE", "demo")
        if mode not in {"demo", "hosted"}:
            raise ValueError("AGENT_MODE must be demo or hosted")
        if mode == "hosted" and not all(
            os.getenv(k) for k in ["MODEL_API_URL", "MODEL_NAME", "MODEL_API_KEY"]
        ):
            raise ValueError("Hosted mode requires MODEL_API_URL, MODEL_NAME and MODEL_API_KEY")
        return cls(
            os.getenv("DATABASE_URL", "sqlite:///./.local/hive.db"),
            os.getenv("BUSINESS_PROFILE", str(ROOT / "examples/business-profiles/profile-a.json")),
            os.getenv("CHROMA_PATH", str(ROOT / ".local/chroma")),
            mode,
            os.getenv("FRONTEND_ORIGIN", "http://localhost:3000"),
            os.getenv("SECURE_COOKIE", "false").lower() == "true",
            os.getenv("MODEL_API_URL", ""),
            os.getenv("MODEL_NAME", ""),
            os.getenv("MODEL_API_KEY", ""),
            os.getenv("EMBEDDING_MODE", "lexical"),
        )

    def profile(self) -> Profile:
        return Profile.model_validate_json(Path(self.profile_path).read_text())
