import json
from pathlib import Path


DATA_FILE = Path("data/reviews.json")


def load_reviews(file_path=DATA_FILE):
    """
    Load previously saved reviews.

    Returns an empty list if the file does not exist.
    Raises an error if the JSON file is corrupted.
    """

    file_path = Path(file_path)

    if not file_path.exists():
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            reviews = json.load(file)

    except json.JSONDecodeError as error:
        raise ValueError("The reviews file contains invalid JSON.") from error

    if not isinstance(reviews, list):
        raise ValueError("Stored reviews must be a list.")

    return reviews


def save_reviews(reviews, file_path=DATA_FILE):
    """
    Save reviews to JSON using an atomic file replacement.
    """

    if not isinstance(reviews, list):
        raise TypeError("Reviews must be provided as a list.")

    if not all(isinstance(review, dict) for review in reviews):
        raise ValueError("Every review must be a dictionary.")

    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    temporary_file = file_path.with_suffix(".tmp")

    try:
        with open(temporary_file, "w", encoding="utf-8") as file:
            json.dump(reviews, file, indent=4, ensure_ascii=False)

        temporary_file.replace(file_path)

    finally:
        if temporary_file.exists():
            temporary_file.unlink()


def add_reviews(new_reviews, file_path=DATA_FILE):
    """
    Add new reviews without duplicating existing review IDs.
    """

    existing_reviews = load_reviews(file_path)

    existing_ids = {
        review.get("id") for review in existing_reviews
    }

    added_count = 0

    for review in new_reviews:
        review_id = review.get("id")

        if review_id not in existing_ids:
            existing_reviews.append(review)
            existing_ids.add(review_id)
            added_count += 1

    save_reviews(existing_reviews, file_path)

    return {
        "total_reviews": len(existing_reviews),
        "added": added_count,
        "skipped": len(new_reviews) - added_count
    }
