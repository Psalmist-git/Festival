import unittest

from app.analytics.insights import (
    identify_complaint_category,
    calculate_priority,
    build_intelligence_report,
)


class TestComplaintClassification(unittest.TestCase):

    def test_food_complaint_is_classified_correctly(self):
        review = {
            "text": "The food was cold and the queues were long."
        }

        analysis = {
            "complaint_summary": "Poor food quality and long queues."
        }

        result = identify_complaint_category(review, analysis)

        self.assertEqual(result, "Food & Catering")

    def test_ticket_complaint_is_classified_correctly(self):
        review = {
            "text": "The tickets were too expensive."
        }

        analysis = {
            "complaint_summary": "Ticket pricing was unreasonable."
        }

        result = identify_complaint_category(review, analysis)

        self.assertEqual(result, "Ticket Pricing")

    def test_unclassified_complaint_returns_other(self):
        review = {"text": "Something went wrong."}
        analysis = {"complaint_summary": "An unexpected issue occurred."}

        result = identify_complaint_category(review, analysis)

        self.assertEqual(result, "Other")


class TestComplaintPriority(unittest.TestCase):

    def test_low_priority_score(self):
        result = calculate_priority(1, 0)

        self.assertEqual(result["score"], 10)
        self.assertEqual(result["priority"], "Low")

    def test_medium_priority_score(self):
        result = calculate_priority(1, 1)

        self.assertEqual(result["score"], 15)
        self.assertEqual(result["priority"], "Medium")

    def test_high_priority_score(self):
        result = calculate_priority(2, 2)

        self.assertEqual(result["score"], 30)
        self.assertEqual(result["priority"], "High")


class TestIntelligenceReport(unittest.TestCase):

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
                "event": "Music Fest",
                "text": "The venue was available."
            },
            {
                "id": "R004",
                "event": "Food Fest",
                "text": "The food was cold."
            },
        ]

        self.analyses = [
            {
                "review_id": "R001",
                "analysis": {
                    "sentiment": "positive",
                    "topics": ["Music", "Performance"],
                    "complaint_detected": False,
                    "recommendation": "Keep improving the performances."
                }
            },
            {
                "review_id": "R002",
                "analysis": {
                    "sentiment": "negative",
                    "topics": ["Food", "Service"],
                    "complaint_detected": True,
                    "complaint_summary": "Long food queues.",
                    "recommendation": "Improve food queue management."
                }
            },
            {
                "review_id": "R003",
                "analysis": {
                    "sentiment": "neutral",
                    "topics": ["Venue"],
                    "complaint_detected": False,
                    "recommendation": ""
                }
            },
        ]

    def test_empty_report(self):
        report = build_intelligence_report([], [])

        self.assertEqual(report["total_reviews"], 0)
        self.assertEqual(report["analyzed_reviews"], 0)
        self.assertEqual(report["unanalyzed_reviews"], 0)
        self.assertEqual(
            report["performance_summary"]["sentiment_index"],
            0
        )

    def test_unanalyzed_reviews_are_counted(self):
        report = build_intelligence_report(
            self.reviews,
            self.analyses
        )

        self.assertEqual(report["total_reviews"], 4)
        self.assertEqual(report["analyzed_reviews"], 3)
        self.assertEqual(report["unanalyzed_reviews"], 1)

    def test_sentiment_counts_are_correct(self):
        report = build_intelligence_report(
            self.reviews,
            self.analyses
        )

        self.assertEqual(
            report["sentiment_counts"],
            {
                "positive": 1,
                "negative": 1,
                "neutral": 1,
            }
        )

    def test_sentiment_percentages_are_correct(self):
        report = build_intelligence_report(
            self.reviews,
            self.analyses
        )

        self.assertEqual(
            report["sentiment_percentages"],
            {
                "positive": 33.3,
                "negative": 33.3,
                "neutral": 33.3,
            }
        )

    def test_complaint_rate_is_correct(self):
        report = build_intelligence_report(
            self.reviews,
            self.analyses
        )

        self.assertEqual(
            report["performance_summary"]["complaint_rate"],
            33.3
        )

    def test_complaint_is_assigned_to_correct_category(self):
        report = build_intelligence_report(
            self.reviews,
            self.analyses
        )

        self.assertEqual(
            report["complaint_categories"][0]["category"],
            "Food & Catering"
        )

    def test_negative_complaint_creates_management_action(self):
        report = build_intelligence_report(
            self.reviews,
            self.analyses
        )

        self.assertEqual(len(report["management_actions"]), 1)

        action = report["management_actions"][0]

        self.assertEqual(action["category"], "Food & Catering")
        self.assertEqual(action["priority"], "Medium")

    def test_recommendations_are_collected(self):
        report = build_intelligence_report(
            self.reviews,
            self.analyses
        )

        self.assertEqual(len(report["recommendations"]), 2)

        self.assertEqual(
            report["recommendations"][0]["review_id"],
            "R001"
        )

    def test_positive_topics_are_highlighted(self):
        report = build_intelligence_report(
            self.reviews,
            self.analyses
        )

        highlights = (
            report["performance_summary"]["positive_highlights"]
        )

        self.assertIn(("Music", 1), highlights)
        self.assertIn(("Performance", 1), highlights)

    def test_sentiment_index_is_calculated_correctly(self):
        report = build_intelligence_report(
            self.reviews,
            self.analyses
        )

        self.assertEqual(
            report["performance_summary"]["sentiment_index"],
            50.0
        )


if __name__ == "__main__":
    unittest.main()
