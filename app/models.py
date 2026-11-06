from datetime import datetime


def validate_review(review, existing_ids=None):
    """
    Validate an original festival review.

    Returns:
        A dictionary containing:
        - valid: True or False
        - errors: List of validation errors
    """

    if existing_ids is None:
        existing_ids = set()

    errors = []

    if not isinstance(review, dict):
        return {
            "valid": False,
            "errors": ["Review must be a dictionary."]
        }

    # Validate review ID
    review_id = review.get("id")

    if not isinstance(review_id, str) or not review_id.strip():
        errors.append("Review ID is missing or invalid.")

    elif review_id.strip() in existing_ids:
        errors.append("Duplicate review ID.")

    # Validate event
    event = review.get("event")

    if not isinstance(event, str) or not event.strip():
        errors.append("Event name is missing or invalid.")

    # Validate review text
    text = review.get("text")

    if not isinstance(text, str):
        errors.append("Review text must be a string.")

    elif not 5 <= len(text.strip()) <= 500:
        errors.append(
            "Review text must contain between 5 and 500 characters."
        )

    # Validate date
    created_at = review.get("created_at")

    if not isinstance(created_at, str):
        errors.append("Review date must be a string.")

    else:
        try:
            parsed_date = datetime.strptime(
                created_at, "%Y-%m-%d"
            )

            if parsed_date.strftime("%Y-%m-%d") != created_at:
                errors.append("Date must use YYYY-MM-DD format.")

        except ValueError:
            errors.append("Invalid review date.")

    return {
        "valid": len(errors) == 0,
        "errors": errors
    }