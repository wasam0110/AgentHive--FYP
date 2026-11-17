"""Pure aggregation helpers for operations overview data."""

from typing import Dict, Iterable, TypedDict

CONVERSATION_STATUSES = (
    "queued",
    "running",
    "waiting_customer",
    "waiting_admin",
    "partially_completed",
    "completed",
    "failed",
    "cancelled",
)


class OverviewCounts(TypedDict):
    total: int
    status_counts: Dict[str, int]


def summarize_conversation_statuses(statuses: Iterable[str]) -> OverviewCounts:
    """Count conversation statuses, returning zero-valued buckets for empty states."""
    status_counts = {status: 0 for status in CONVERSATION_STATUSES}
    total = 0

    for status in statuses:
        if status not in status_counts:
            raise ValueError(f"Unknown conversation status: {status}")
        status_counts[status] += 1
        total += 1

    return {"total": total, "status_counts": status_counts}
