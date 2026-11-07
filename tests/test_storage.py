import json
import tempfile
import unittest

from pathlib import Path

from app.storage import (
    load_reviews,
    save_reviews,
    add_reviews,
)

from app.analysis_storage import (
    load_analyses,
    save_analysis,
    get_analysis,
)


class TestReviewStorage(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.file_path = Path(self.temp_dir.name) / "reviews.json"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_missing_file_returns_empty_list(self):
        self.assertEqual(load_reviews(self.file_path), [])

    def test_save_and_load_reviews(self):
        reviews = [
            {"id": "R001", "event": "Music Fest"},
            {"id": "R002", "event": "Food Fest"},
        ]

        save_reviews(reviews, self.file_path)

        self.assertEqual(load_reviews(self.file_path), reviews)

    def test_save_creates_missing_directory(self):
        nested_path = (
            Path(self.temp_dir.name) / "new_folder" / "reviews.json"
        )

        save_reviews([{"id": "R001"}], nested_path)

        self.assertTrue(nested_path.exists())

    def test_corrupted_json_raises_value_error(self):
        self.file_path.write_text("{invalid json", encoding="utf-8")

        with self.assertRaises(ValueError):
            load_reviews(self.file_path)

    def test_non_list_json_raises_value_error(self):
        self.file_path.write_text(
            '{"id": "R001"}',
            encoding="utf-8"
        )

        with self.assertRaises(ValueError):
            load_reviews(self.file_path)

    def test_saving_non_list_raises_type_error(self):
        with self.assertRaises(TypeError):
            save_reviews({"id": "R001"}, self.file_path)

    def test_saving_non_dictionary_review_raises_value_error(self):
        with self.assertRaises(ValueError):
            save_reviews(["not a dictionary"], self.file_path)

    def test_add_reviews_skips_duplicate_ids(self):
        existing = [
            {"id": "R001", "event": "Music Fest"}
        ]

        save_reviews(existing, self.file_path)

        new_reviews = [
            {"id": "R001", "event": "Duplicate Fest"},
            {"id": "R002", "event": "Food Fest"},
        ]

        result = add_reviews(new_reviews, self.file_path)

        self.assertEqual(result["added"], 1)
        self.assertEqual(result["skipped"], 1)
        self.assertEqual(result["total_reviews"], 2)


class TestAnalysisStorage(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.file_path = Path(self.temp_dir.name) / "analyses.json"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_missing_analysis_file_returns_empty_list(self):
        self.assertEqual(load_analyses(self.file_path), [])

    def test_save_and_retrieve_analysis(self):
        analysis = {
            "sentiment": "positive",
            "topics": ["Music", "Performance"],
        }

        save_analysis(
            "R001",
            "Music Fest",
            analysis,
            self.file_path
        )

        result = get_analysis("R001", self.file_path)

        self.assertEqual(result, analysis)

    def test_saving_same_review_updates_analysis(self):
        first_analysis = {"sentiment": "neutral"}
        updated_analysis = {"sentiment": "positive"}

        save_analysis(
            "R001", "Music Fest", first_analysis, self.file_path
        )

        save_analysis(
            "R001", "Music Fest", updated_analysis, self.file_path
        )

        analyses = load_analyses(self.file_path)

        self.assertEqual(len(analyses), 1)
        self.assertEqual(
            analyses[0]["analysis"],
            updated_analysis
        )

    def test_missing_review_analysis_returns_none(self):
        self.assertIsNone(
            get_analysis("UNKNOWN", self.file_path)
        )

    def test_empty_review_id_raises_value_error(self):
        with self.assertRaises(ValueError):
            save_analysis(
                "",
                "Music Fest",
                {"sentiment": "positive"},
                self.file_path
            )

    def test_non_dictionary_analysis_raises_type_error(self):
        with self.assertRaises(TypeError):
            save_analysis(
                "R001",
                "Music Fest",
                "positive",
                self.file_path
            )

    def test_corrupted_analysis_json_raises_value_error(self):
        self.file_path.write_text(
            "{invalid json",
            encoding="utf-8"
        )

        with self.assertRaises(ValueError):
            load_analyses(self.file_path)

    def test_non_list_analysis_json_raises_value_error(self):
        self.file_path.write_text(
            '{"review_id": "R001"}',
            encoding="utf-8"
        )

        with self.assertRaises(ValueError):
            load_analyses(self.file_path)


if __name__ == "__main__":
    unittest.main()
