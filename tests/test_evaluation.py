import csv
import tempfile
import unittest

from pathlib import Path
from io import StringIO
from contextlib import redirect_stdout
from unittest.mock import patch

from app.evaluation import (
    calculate_accuracy,
    load_gold_standard,
    evaluate_gold_standard,
)

from app.ai.gemini import GeminiAnalysisError


class TestGoldStandardLoading(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.csv_path = Path(self.temp_dir.name) / "gold.csv"

        self.columns = [
            "id",
            "event",
            "text",
            "expected_sentiment",
            "expected_emotions",
            "expected_topics",
            "expected_complaint_detected",
            "expected_complaint_category",
        ]

    def tearDown(self):
        self.temp_dir.cleanup()

    def create_csv(self, rows):
        with self.csv_path.open(
            "w",
            encoding="utf-8",
            newline=""
        ) as file:
            writer = csv.DictWriter(
                file,
                fieldnames=self.columns
            )
            writer.writeheader()
            writer.writerows(rows)

    def test_gold_standard_loads_successfully(self):
        self.create_csv([
            {
                "id": "G001",
                "event": "Music Fest",
                "text": "The music was excellent.",
                "expected_sentiment": "positive",
                "expected_emotions": "joy",
                "expected_topics": "Music",
                "expected_complaint_detected": "false",
                "expected_complaint_category": "",
            }
        ])

        result = load_gold_standard(self.csv_path)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "G001")

    def test_empty_gold_standard_raises_value_error(self):
        self.csv_path.write_text(
            "id,event,text,expected_sentiment\n",
            encoding="utf-8"
        )

        with self.assertRaises(ValueError):
            load_gold_standard(self.csv_path)

    def test_missing_required_columns_raises_value_error(self):
        self.csv_path.write_text(
            "id,event,text\nG001,Music Fest,Great music\n",
            encoding="utf-8"
        )

        with self.assertRaises(ValueError):
            load_gold_standard(self.csv_path)

    def test_missing_gold_standard_file_raises_file_error(self):
        missing_path = (
            Path(self.temp_dir.name) / "missing.csv"
        )

        with self.assertRaises(FileNotFoundError):
            load_gold_standard(missing_path)


class TestAccuracyCalculation(unittest.TestCase):

    def test_accuracy_is_calculated_correctly(self):
        self.assertEqual(calculate_accuracy(8, 10), 80.0)

    def test_zero_total_returns_zero_accuracy(self):
        self.assertEqual(calculate_accuracy(0, 0), 0.0)


class TestGoldStandardEvaluation(unittest.TestCase):

    def setUp(self):
        self.examples = [
            {
                "id": "G001",
                "event": "Music Fest",
                "text": "The music was excellent.",
                "expected_sentiment": "positive",
                "expected_emotions": "joy",
                "expected_topics": "Music",
                "expected_complaint_detected": "false",
                "expected_complaint_category": "",
            },
            {
                "id": "G002",
                "event": "Food Fest",
                "text": "The food was cold and disappointing.",
                "expected_sentiment": "negative",
                "expected_emotions": "disappointment",
                "expected_topics": "Food",
                "expected_complaint_detected": "true",
                "expected_complaint_category": "Food & Catering",
            },
        ]

    @patch("app.evaluation.load_gold_standard")
    @patch("app.evaluation.analyze_review")
    def test_evaluation_uses_mocked_ai(
        self,
        mock_analyze,
        mock_load
    ):
        mock_load.return_value = self.examples

        mock_analyze.side_effect = [
            {
                "sentiment": "positive",
                "complaint_detected": False,
            },
            {
                "sentiment": "negative",
                "complaint_detected": True,
                "complaint_summary": "The food was cold.",
            },
        ]

        output = StringIO()

        with redirect_stdout(output):
            evaluate_gold_standard()

        displayed_text = output.getvalue()

        self.assertIn("100.0%", displayed_text)
        self.assertIn("EVALUATION COMPLETED", displayed_text)

        self.assertEqual(mock_analyze.call_count, 2)

    @patch("app.evaluation.load_gold_standard")
    @patch("app.evaluation.analyze_review")
    def test_failed_analysis_is_counted(
        self,
        mock_analyze,
        mock_load
    ):
        mock_load.return_value = self.examples

        mock_analyze.side_effect = [
            GeminiAnalysisError("Simulated analysis failure"),
            {
                "sentiment": "negative",
                "complaint_detected": True,
                "complaint_summary": "The food was cold.",
            },
        ]

        output = StringIO()

        with redirect_stdout(output):
            evaluate_gold_standard()

        self.assertIn("Failed analyses: 1", output.getvalue())


if __name__ == "__main__":
    unittest.main()
