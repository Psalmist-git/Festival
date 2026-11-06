import csv

from app.models import validate_review


def import_reviews(file_path, existing_reviews=None):
    """
    Import and validate festival reviews from CSV.
    """

    if existing_reviews is None:
        existing_reviews = []

    existing_ids = {
        review["id"].strip()
        for review in existing_reviews
    }

    accepted_reviews = []
    rejected_reviews = []

    required_columns = {
        "id",
        "event",
        "text",
        "created_at"
    }

    try:
        with open(
            file_path,
            "r",
            encoding="utf-8-sig",
            newline=""
        ) as file:

            reader = csv.DictReader(file)

            if not reader.fieldnames:
                return {
                    "success": False,
                    "error": "CSV file has no header.",
                    "accepted": [],
                    "rejected": [],
                    "total": 0
                }

            if not required_columns.issubset(reader.fieldnames):
                return {
                    "success": False,
                    "error": "Missing required CSV columns.",
                    "accepted": [],
                    "rejected": [],
                    "total": 0
                }

            for row_number, row in enumerate(reader, start=2):

                # Normalize selected fields
                row["id"] = row["id"].strip()
                row["event"] = row["event"].strip()
                row["created_at"] = row["created_at"].strip()

                result = validate_review(row, existing_ids)

                if result["valid"]:
                    accepted_reviews.append(row)
                    existing_ids.add(row["id"])

                else:
                    rejected_reviews.append({
                        "row": row_number,
                        "review": row,
                        "errors": result["errors"]
                    })

    except (OSError, UnicodeDecodeError, csv.Error) as error:
        return {
            "success": False,
            "error": str(error),
            "accepted": [],
            "rejected": [],
            "total": 0
        }

    return {
        "success": True,
        "accepted": accepted_reviews,
        "rejected": rejected_reviews,
        "total": len(accepted_reviews) + len(rejected_reviews),
        "accepted_count": len(accepted_reviews),
        "rejected_count": len(rejected_reviews)
    }