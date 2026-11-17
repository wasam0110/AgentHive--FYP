import unittest

from backend.services.overview import CONVERSATION_STATUSES, summarize_conversation_statuses


class OverviewCountTests(unittest.TestCase):
    def test_empty_input_returns_every_status_with_zero_count(self):
        result = summarize_conversation_statuses([])

        self.assertEqual(result["total"], 0)
        self.assertEqual(result["status_counts"], {status: 0 for status in CONVERSATION_STATUSES})

    def test_counts_each_status_and_preserves_partial_completion(self):
        statuses = [
            "queued",
            "running",
            "waiting_customer",
            "waiting_admin",
            "partially_completed",
            "completed",
            "failed",
            "cancelled",
            "waiting_customer",
        ]

        result = summarize_conversation_statuses(statuses)

        self.assertEqual(result["total"], 9)
        self.assertEqual(
            result["status_counts"],
            {
                "queued": 1,
                "running": 1,
                "waiting_customer": 2,
                "waiting_admin": 1,
                "partially_completed": 1,
                "completed": 1,
                "failed": 1,
                "cancelled": 1,
            },
        )

    def test_rejects_status_outside_the_shared_contract(self):
        with self.assertRaisesRegex(ValueError, "Unknown conversation status"):
            summarize_conversation_statuses(["processing"])