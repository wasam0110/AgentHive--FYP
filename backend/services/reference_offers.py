"""Read-only published offers, separate from executable database catalog items."""
import re
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, HttpUrl
from backend.config import ROOT

SOURCES = {"stormfiber-karachi": ROOT / "examples/reference-offers/stormfiber-karachi.json"}


class Offer(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    group: str
    name: str
    base_price: str | None = Field(pattern=r"^\d+\.\d{2}$")
    sales_tax: str | None = Field(pattern=r"^\d+\.\d{2}$")
    advance_tax: str | None = Field(pattern=r"^\d+\.\d{2}$")
    total: str | None = Field(pattern=r"^\d+\.\d{2}$")
    period: Literal["month", "once", "installment", "promotion", "minute"]
    base_speed_mbps: int | None = Field(ge=0)
    bonus_speed_mbps: int = Field(ge=0)
    notes: str
    ongoing_monthly: str | None = Field(pattern=r"^\d+\.\d{2}$")
    starts_month: int | None = Field(ge=1)
    source_page: int = Field(ge=1)


class ReferenceOffers(BaseModel):
    model_config = ConfigDict(extra="forbid")
    provider: str
    city: str
    currency: str
    source_url: HttpUrl
    source_date: str
    checked_on: str
    source_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    notice: str
    terms: list[str]
    offers: list[Offer]


def load_offers(profile):
    """Read an allowlisted source; no network access or database side effects."""
    if "reference_information" not in profile.capabilities:
        return None
    path = SOURCES.get(profile.reference_catalog)
    if path is None:
        raise ValueError("Unknown reference catalog")
    data = ReferenceOffers.model_validate_json(path.read_text(encoding="utf-8"))
    if data.currency != profile.currency:
        raise ValueError("Reference currency differs from business currency")
    if len({offer.id for offer in data.offers}) != len(data.offers):
        raise ValueError("Duplicate reference offer IDs")
    return data


def offer_evidence(profile, query):
    """Return at most three matching reference rows without producing purchasable offers."""
    data = load_offers(profile)
    if data is None:
        return []
    tokens = set(re.findall(r"[a-z0-9]+", query.lower())) - {
        "i", "a", "the", "and", "for", "me", "show", "please", "price", "prices", "plans"
    }
    if "monthly" in tokens:
        tokens.add("month")

    def score(offer):
        terms = set(re.findall(r"[a-z0-9]+", f"{offer.name} {offer.group} {offer.period}".lower()))
        if offer.base_speed_mbps is not None:
            terms |= {str(offer.base_speed_mbps), str(offer.base_speed_mbps + offer.bonus_speed_mbps)}
        return len(tokens & terms)
    ranked = sorted(data.offers, key=score, reverse=True)
    matches = [o for o in ranked if score(o) > 0][:3]
    refs = []
    for offer in matches:
        cost = f"{data.currency} {offer.total} per {offer.period}" if offer.total else "Price pending confirmation"
        detail = f"{offer.name}: {cost} (published tax-inclusive reference). "
        if offer.base_speed_mbps is not None:
            detail += (f"Base {offer.base_speed_mbps} Mbps; conditional payment bonus "
                       f"{offer.bonus_speed_mbps} Mbps. ")
        if offer.ongoing_monthly:
            detail += f"Then {data.currency} {offer.ongoing_monthly}/month from month {offer.starts_month}. "
        detail += offer.notes
        refs.append({"source_id": offer.id, "source": str(data.source_url),
                     "excerpt": f"{data.notice} Source date {data.source_date}. {detail}"})
    return refs
