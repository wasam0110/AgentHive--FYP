"""Read-only LangGraph work; all mutation happens once at a durable DB boundary."""

import asyncio
from time import perf_counter
from typing import TypedDict

from backend.tools import reference
from backend.services.reference_offers import offer_evidence
from backend.services.service_context import evidence as service_evidence
from backend.db.models import now
from langgraph.graph import StateGraph, START, END


class State(TypedDict, total=False):
    message: dict
    intents: dict
    results: list[dict]
    language: str


class Workflow:
    def __init__(self, profile, provider, retriever, factory):
        self.profile, self.provider, self.retriever = profile, provider, retriever
        self.factory = factory
        graph = StateGraph(State)
        graph.add_node("intake", self.intake)
        graph.add_node("specialists", self.specialists)
        graph.add_edge(START, "intake")
        graph.add_edge("intake", "specialists")
        graph.add_edge("specialists", END)
        self.graph = graph.compile()

    async def intake(self, state):
        result = await self.provider.intake(state["message"]["content"])
        # Explicit selectors describe user choices, not authorization to write.
        if state["message"].get("item_id"):
            result.sales = True
        if state["message"].get("slot_id"):
            result.scheduling = True
        return {"intents": result.model_dump()}

    async def specialists(self, state):
        intents, text = state["intents"], state["message"]["content"]

        async def reference_worker():
            refs = await asyncio.to_thread(offer_evidence, self.profile, text)
            return {
                "worker": "sales", "status": "reference", "evidence": refs,
                "summary": "\n".join(r["excerpt"] for r in refs) if refs else
                    "Reference information only. Open Reference offers for the sourced price list. "
                    "No quote, purchase, activation or booking has been made.",
            }

        async def worker(name, capability):
            started = perf_counter()
            started_at = now()
            if capability not in self.profile.capabilities:
                return {
                    "worker": name,
                    "status": "denied",
                    "summary": f"{name.title()} is disabled for this business.",
                    "evidence": [],
                    "latency_ms": 0,
                }
            try:
                if name == "support":
                    refs = await asyncio.to_thread(self.retriever.search, text)
                    answer = await self.provider.answer(text, refs, state["language"])
                    if refs:
                        answer += "\nSources: " + ", ".join(ref["source_id"] for ref in refs)
                    history = await asyncio.to_thread(
                        reference.support_context, self.factory, state["message"].get("_customer_id")
                    )
                    refs += history
                    if "service_context" in self.profile.capabilities:
                        service_refs = await asyncio.to_thread(
                            service_evidence, self.factory, self.profile,
                            state["message"].get("_customer_id"), state["message"].get("_connection_id"))
                        refs += service_refs
                        answer = "\n".join(r["excerpt"] for r in service_refs) + "\n\n" + answer
                elif name == "sales":
                    refs = await asyncio.to_thread(
                        reference.catalog, self.factory, self.profile, state["message"].get("item_id")
                    )
                    answer = "Catalog checked: " + "; ".join(r["excerpt"] for r in refs)
                else:
                    refs = await asyncio.to_thread(
                        reference.appointments, self.factory, self.profile, state["message"].get("slot_id")
                    )
                    answer = (
                        f"Found {len(refs)} available appointment option(s). A proposal is not a reservation."
                    )
                return {
                    "worker": name,
                    "status": "completed",
                    "summary": answer,
                    "evidence": refs,
                    "latency_ms": round((perf_counter() - started) * 1000),
                    "started_at": started_at,
                    "ended_at": now(),
                }
            except Exception:
                # Keep provider details/keys out of customer-facing traces. Do not fake a result.
                return {
                    "worker": name,
                    "status": "failed",
                    "summary": f"{name.title()} could not complete. Please retry or contact an operator.",
                    "evidence": [],
                    "latency_ms": round((perf_counter() - started) * 1000),
                    "started_at": started_at,
                    "ended_at": now(),
                }

        tasks = []
        if intents["support"]:
            tasks.append(worker("support", "knowledge_answer"))
        if intents["sales"]:
            if ("reference_information" in self.profile.capabilities
                    and "catalog_quote" not in self.profile.capabilities):
                tasks.append(reference_worker())
            else:
                tasks.append(worker("sales", "catalog_quote"))
        results = await asyncio.gather(*tasks)
        # Scheduling follows quote investigation when both are requested.
        if intents["scheduling"]:
            if intents["sales"] and any(
                r["worker"] == "sales" and r["status"] != "completed" for r in results
            ):
                results.append(
                    {
                        "worker": "scheduling",
                        "status": "skipped",
                        "evidence": [],
                        "summary": "Scheduling is paused until the catalog selection is valid.",
                    }
                )
            else:
                results.append(await worker("scheduling", "resource_booking"))
        if intents["manual"]:
            results.append(
                {
                    "worker": "support",
                    "status": "manual",
                    "summary": "Refund/cancellation request recorded for manual review. No refund or cancellation has been performed.",
                    "evidence": [],
                }
            )
        return {"results": results}

    async def run(self, message, language):
        return await self.graph.ainvoke({"message": message, "language": language}, {"recursion_limit": 12})
