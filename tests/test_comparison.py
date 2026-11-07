import unittest

from io import StringIO
from contextlib import redirect_stdout

from app.analytics.comparison import (
    get_festival_names,
    compare_festival_data,
    display_festival_comparison,
)


class TestFestivalComparison(unittest.TestCase):

    def setUp(self):
        self.reviews = [
            {
                "id": "R001",
                "event": "Music Fest",
                "text": "The music was excellent."
            },
            {
                "id": "R002",
                "event": "Music Fest",
                "text": "The food queues were very long."
            },
            {
                "id": "R003",
                "event": "Food Fest",
                "text": "The food was delicious."
            },
        ]

        self.analyses = [
            {
                "review_id": "R001",
                "analysis": {
                    "sentiment": "positive",
                    "topics": ["Music"],
                    "complaint_detected": False,
                    "recommendation": "Keep up the good performances."
                }
            },
            {
                "review_id": "R002",
                "analysis": {
                    "sentiment": "negative",
                    "topics": ["Food"],
                    "complaint_detected": True,
                    "complaint_summary": "Long food queues.",
                    "recommendation": "Improve queue management."
                }
            },
            {
                "review_id": "R003",
                "analysis": {
                    "sentiment": "positive",
                    "topics": ["Food Quality"],
                    "complaint_detected": False,
                    "recommendation": "Maintain food quality."
                }
            },
        ]

    def test_festival_names_are_unique(self):
        names = get_festival_names(self.reviews)

        self.assertEqual(
            names,
            ["Food Fest", "Music Fest"]
        )

    def test_comparison_returns_correct_festival_names(self):
        result = compare_festival_data(
            self.reviews,
            self.analyses,
            "Music Fest",
            "Food Fest"
        )

        self.assertEqual(result["first_event"], "Music Fest")
        self.assertEqual(result["second_event"], "Food Fest")

    def test_comparison_uses_correct_reviews(self):
        result = compare_festival_data(
            self.reviews,
            self.analyses,
            "Music Fest",
            "Food Fest"
        )

        self.assertEqual(
            result["first_report"]["total_reviews"],
            2
        )

        self.assertEqual(
            result["second_report"]["total_reviews"],
            1
        )

    def test_comparison_counts_unanalysed_reviews(self):
        result = compare_festival_data(
            self.reviews,
            self.analyses[:1],
            "Music Fest",
            "Food Fest"
        )

        self.assertEqual(
            result["first_report"]["unanalyzed_reviews"],
            1
        )

        self.assertEqual(
            result["second_report"]["unanalyzed_reviews"],
            1
        )

    def test_display_shows_both_festivals(self):
        comparison = compare_festival_data(
            self.reviews,
            self.analyses,
            "Music Fest",
            "Food Fest"
        )

        output = StringIO()

        with redirect_stdout(output):
            display_festival_comparison(comparison)

        displayed_text = output.getvalue()

        self.assertIn("Music Fest", displayed_text)
        self.assertIn("Food Fest", displayed_text)
        self.assertIn("OVERALL ASSESSMENT", displayed_text)
        self.assertIn("DATA NOTES", displayed_text)


if __name__ == "__main__":
    unittest.main()

