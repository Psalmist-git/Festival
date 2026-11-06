import csv
import tempfile
import unittest

from pathlib import Path

from app.ingest import import_reviews


class TestReviewImport(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.csv_path = Path(self.temp_dir.name) / "reviews.csv"

    def tearDown(self):
        self.temp_dir.cleanup()

    def create_csv(self, rows):
        with open(self.csv_path, "w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=["id", "event", "text", "created_at"]
            )
            writer.writeheader()
            writer.writerows(rows)

    def test_valid_review_import(self):
        self.create_csv([
            {
                "id": "R001",
                "event": "Music Fest",
                "text": "The music was absolutely amazing!",
                "created_at": "2026-01-15"
            }
        ])

        result = import_reviews(self.csv_path)

        self.assertTrue(result["success"])
        self.assertEqual(result["accepted_count"], 1)

    def test_duplicate_review_id(self):
        self.create_csv([
            {
                "id": "R001",
                "event": "Music Fest",
                "text": "The music was absolutely amazing!",
                "created_at": "2026-01-15"
            },
            {
                "id": "R001",
                "event": "Food Fest",
                "text": "The food was really delicious!",
                "created_at": "2026-01-16"
            }
        ])

        result = import_reviews(self.csv_path)

        self.assertEqual(result["accepted_count"], 1)
        self.assertEqual(result["rejected_count"], 1)

    def test_existing_id_is_rejected(self):
        self.create_csv([
            {
                "id": "R001",
                "event": "Music Fest",
                "text": "The music was absolutely amazing!",
                "created_at": "2026-01-15"
            }
        ])

        existing = [{"id": "R001"}]

        result = import_reviews(self.csv_path, existing)

        self.assertEqual(result["accepted_count"], 0)
        self.assertEqual(result["rejected_count"], 1)

    def test_invalid_date_is_rejected(self):
        self.create_csv([
            {
                "id": "R002",
                "event": "Music Fest",
                "text": "The music was absolutely amazing!",
                "created_at": "2026-15-40"
            }
        ])

        result = import_reviews(self.csv_path)

        self.assertEqual(result["rejected_count"], 1)

    def test_empty_review_text_is_rejected(self):
        self.create_csv([
            {
                "id": "R003",
                "event": "Music Fest",
                "text": "",
                "created_at": "2026-01-15"
            }
        ])

        result = import_reviews(self.csv_path)

        self.assertEqual(result["rejected_count"], 1)

    def test_unicode_review_is_accepted(self):
        self.create_csv([
            {
                "id": "R004",
                "event": "Music Fest",
                "text": "The performance was शानदार and enjoyable!",
                "created_at": "2026-01-15"
            }
        ])

        result = import_reviews(self.csv_path)

        self.assertEqual(result["accepted_count"], 1)

    def test_missing_csv_columns(self):
        with open(self.csv_path, "w", encoding="utf-8") as file:
            file.write("id,event\nR001,Music Fest\n")

        result = import_reviews(self.csv_path)

        self.assertFalse(result["success"])
        self.assertEqual(result["accepted_count"] if "accepted_count" in result else 0, 0)

    def test_missing_file_does_not_import_partial_data(self):
        result = import_reviews(
            Path(self.temp_dir.name) / "missing.csv"
        )

        self.assertFalse(result["success"])
        self.assertEqual(result["accepted"], [])


if __name__ == "__main__":
    unittest.main()