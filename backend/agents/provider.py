"""Model access is opt-in; offline behavior is always identified as deterministic demo."""

import asyncio
import json
import re
from pathlib import Path

import httpx
from backend.schemas.api import Intake

PROMPTS = Path(__file__).resolve().parents[1] / "prompts"


def demo_intake(text):
    lower = text.lower()
    return Intake(
        support=any(
            w in lower
            for w in [
                "not working", "isn't working", "slow", "outage", "disconnected",
                "help",
                "support",
                "complaint",
                "problem",
                "issue",
                "madad",
                "masla",
                "مدد",
                "مسئلہ",
                "شکایت",
            ]
        ),
        sales=any(
            w in lower
            for w in ["plan", "package", "monthly", "quote", "price", "service", "catalog", "buy", "discount", "qeemat", "قیمت", "سروس"]
        ),
        scheduling=any(w in lower for w in ["book", "appointment", "schedule", "slot", "وقت", "بکنگ"]),
        manual=any(w in lower for w in ["refund", "cancel", "واپس", "منسوخ"]),
        language="ur"
        if re.search(r"[\u0600-\u06ff]", text)
        else ("roman-ur" if any(w in lower for w in ["madad", "masla", "qeemat"]) else "en"),
    )


class Provider:
    def __init__(self, settings):
        self.settings = settings

    async def complete(self, prompt_name, data):
        """Retry transient provider errors twice; never fall back to fake success."""
        last = None
        for attempt in range(3):
            try:
                async with httpx.AsyncClient(timeout=25) as client:
                    response = await client.post(
                        self.settings.model_url,
                        headers={"Authorization": f"Bearer {self.settings.model_key}"},
                        json={
                            "model": self.settings.model_name,
                            "temperature": 0,
                            "messages": [
                                {"role": "system", "content": (PROMPTS / prompt_name).read_text()},
                                {"role": "user", "content": json.dumps(data, ensure_ascii=False)},
                            ],
                            "response_format": {"type": "json_object"},
                        },
                    )
                    response.raise_for_status()
                    return json.loads(response.json()["choices"][0]["message"]["content"])
            except (httpx.TimeoutException, httpx.TransportError) as exc:
                last = exc
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code != 429 and exc.response.status_code < 500:
                    raise
                last = exc
            if attempt < 2:
                await asyncio.sleep(0.5 * (attempt + 1))
        raise RuntimeError("Model provider unavailable") from last

    async def intake(self, text):
        if self.settings.mode == "demo":
            return demo_intake(text)
        return Intake.model_validate(await self.complete("intake.txt", {"message": text}))

    async def answer(self, text, evidence, language):
        if not evidence:
            return "I could not find supporting guidance. Please provide more detail; an operator can help."
        if self.settings.mode == "demo":
            prefix = {
                "en": "From the configured knowledge base: ",
                "ur": "علمی ذخیرے کے مطابق: ",
                "roman-ur": "Knowledge base ke mutabiq: ",
            }[language]
            return prefix + evidence[0]["excerpt"]
        result = await self.complete(
            "support.txt", {"message": text, "evidence": evidence, "language": language}
        )
        answer = result.get("answer")
        if not isinstance(answer, str) or not answer.strip() or len(answer) > 3000:
            raise ValueError("Invalid provider answer")
        return answer
