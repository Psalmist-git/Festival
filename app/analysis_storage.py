import json
from pathlib import Path


ANALYSIS_FILE = Path("data/analyses.json")


def load_analyses(file_path=ANALYSIS_FILE):
    """Load previously saved Gemini analyses."""

    file_path = Path(file_path)

    if not file_path.exists():
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            analyses = json.load(file)

    except json.JSONDecodeError as error:
        raise ValueError(
            "The analyses file contains invalid JSON."
        ) from error

    if not isinstance(analyses, list):
        raise ValueError("Stored analyses must be a list.")

    return analyses


def save_analysis(review_id, event, analysis, file_path=ANALYSIS_FILE):
    """Save or update the analysis belonging to a review."""

    if not review_id:
        raise ValueError("Review ID is required.")

    if not isinstance(analysis, dict):
        raise TypeError("Analysis must be a dictionary.")

    analyses = load_analyses(file_path)

    new_record = {
        "review_id": review_id,
        "event": event,
        "analysis": analysis,
    }

    updated = False

    for index, record in enumerate(analyses):
        if record.get("review_id") == review_id:
            analyses[index] = new_record
            updated = True
            break

    if not updated:
        analyses.append(new_record)

    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    temporary_file = file_path.with_suffix(".tmp")

    try:
        with open(temporary_file, "w", encoding="utf-8") as file:
            json.dump(analyses, file, indent=4, ensure_ascii=False)

        temporary_file.replace(file_path)

    finally:
        if temporary_file.exists():
            temporary_file.unlink()


def get_analysis(review_id, file_path=ANALYSIS_FILE):
    """Retrieve the saved analysis for one review."""

    analyses = load_analyses(file_path)

    for record in analyses:
        if record.get("review_id") == review_id:
            return record.get("analysis")

    return None