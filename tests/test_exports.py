import csv
import json
import tempfile
import unittest

from pathlib import Path
from unittest.mock import patch

from app.exports import export_report, flatten_report


class TestReportExports(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.export_folder = Path(self.temp_dir.name)

        self.report = {
            "festival": "Music Fest",
            "total_reviews": 10,
            "sentiment": {
                "positive": 6,
                "negative": 3,
                "neutral": 1,
            },
            "highlights": ["Music", "Performance"],
            "complaints": [
                {"category": "Food", "count": 3}
            ],
        }

        self.folder_patch = patch(
            "app.exports.EXPORT_FOLDER",
            self.export_folder
        )
        self.folder_patch.start()

    def tearDown(self):
        self.folder_patch.stop()
        self.temp_dir.cleanup()

    def test_json_export_creates_valid_file(self):
        result = export_report(
            self.report,
            "festival_report",
            "json"
        )

        self.assertTrue(result.exists())

        with result.open(encoding="utf-8") as file:
            exported_data = json.load(file)

        self.assertEqual(exported_data, self.report)

    def test_csv_export_creates_valid_file(self):
        result = export_report(
            self.report,
            "festival_report",
            "csv"
        )

        self.assertTrue(result.exists())

        with result.open(
            encoding="utf-8",
            newline=""
        ) as file:
            rows = list(csv.DictReader(file))

        self.assertIn(
            {"Metric": "festival", "Value": "Music Fest"},
            rows
        )

        self.assertIn(
            {"Metric": "sentiment.positive", "Value": 6},
            rows
        )

    def test_export_accepts_uppercase_format(self):
        result = export_report(
            self.report,
            "festival_report",
            "JSON"
        )

        self.assertEqual(result.suffix, ".json")

    def test_invalid_export_format_raises_value_error(self):
        with self.assertRaises(ValueError):
            export_report(
                self.report,
                "festival_report",
                "pdf"
            )

    def test_empty_report_raises_value_error(self):
        with self.assertRaises(ValueError):
            export_report(
                {},
                "festival_report",
                "json"
            )

    def test_non_dictionary_report_raises_value_error(self):
        with self.assertRaises(ValueError):
            export_report(
                ["invalid report"],
                "festival_report",
                "json"
            )


class TestReportFlattening(unittest.TestCase):

    def test_nested_dictionary_is_flattened(self):
        result = flatten_report({
            "sentiment": {
                "positive": 5
            }
        })

        self.assertEqual(
            result,
            [{
                "Metric": "sentiment.positive",
                "Value": 5
            }]
        )

    def test_list_of_dictionaries_is_serialised(self):
        result = flatten_report({
            "complaints": [
                {"category": "Food", "count": 2}
            ]
        })

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["Metric"], "complaints")

        exported_value = json.loads(result[0]["Value"])

        self.assertEqual(
            exported_value[0]["category"],
            "Food"
        )


if __name__ == "__main__":
    unittest.main()
