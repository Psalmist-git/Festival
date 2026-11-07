import csv
from pathlib import Path

from app.ai.gemini import (
    analyze_review,
    GeminiConfigurationError,
    GeminiAnalysisError,
)

from app.analytics.insights import identify_complaint_category


GOLD_STANDARD_FILE = Path("data/gold_standard.csv")


def calculate_accuracy(correct, total):
    """Calculate accuracy as a percentage."""

    if total == 0:
        return 0.0

    return round((correct / total) * 100, 2)


def load_gold_standard(file_path=GOLD_STANDARD_FILE):
    """Load the manually labelled evaluation examples."""

    with Path(file_path).open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:

        reader = csv.DictReader(file)
        examples = list(reader)

    if not examples:
        raise ValueError("The gold-standard dataset is empty.")

    required_columns = {
        "id",
        "event",
        "text",
        "expected_sentiment",
        "expected_complaint_detected",
        "expected_complaint_category",
    }

    missing_columns = required_columns - set(reader.fieldnames or [])

    if missing_columns:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(sorted(missing_columns))
        )

    return examples


def evaluate_gold_standard():
    """
    Compare Gemini's predictions with the gold-standard labels.

    Evaluation results are displayed but are not saved to
    the normal festival review or analysis storage.
    """

    examples = load_gold_standard()

    sentiment_correct = 0
    complaint_correct = 0
    category_correct = 0

    sentiment_total = 0
    complaint_total = 0
    category_total = 0

    failed_reviews = 0

    print("\n========== ASAKE AI EVALUATION ==========")
    print("Gold-standard examples:", len(examples))
    print("Evaluating Gemini predictions...")
    print("\nPlease allow time for the AI requests to complete.")

    for index, example in enumerate(examples, start=1):

        review = {
            "id": example["id"],
            "event": example["event"],
            "text": example["text"],
        }

        expected_sentiment = (
            example["expected_sentiment"].strip().lower()
        )

        expected_complaint = (
            example["expected_complaint_detected"].strip().lower()
            == "true"
        )

        expected_category = (
            example["expected_complaint_category"].strip()
        )

        print(
            f"\n[{index}/{len(examples)}] "
            f"Evaluating {example['id']}..."
        )

        try:
            analysis = analyze_review(review)

        except GeminiConfigurationError:
            print("\nGemini configuration error.")
            print("Evaluation stopped.")
            raise

        except GeminiAnalysisError as error:
            print("Analysis failed:", error)
            failed_reviews += 1
            continue

        predicted_sentiment = (
            str(analysis.get("sentiment", "")).strip().lower()
        )

        predicted_complaint = bool(
            analysis.get("complaint_detected", False)
        )

        predicted_category = ""

        if predicted_complaint:
            predicted_category = (
                identify_complaint_category(review, analysis) or ""
            )

        # Compare sentiment.
        sentiment_total += 1

        if predicted_sentiment == expected_sentiment:
            sentiment_correct += 1
            sentiment_result = "PASS"
        else:
            sentiment_result = "FAIL"

        # Compare complaint detection.
        complaint_total += 1

        if predicted_complaint == expected_complaint:
            complaint_correct += 1
            complaint_result = "PASS"
        else:
            complaint_result = "FAIL"

        # Evaluate category only when the reference says
        # a complaint is present.
        if expected_complaint:
            category_total += 1

            if (
                predicted_complaint
                and predicted_category == expected_category
            ):
                category_correct += 1
                category_result = "PASS"
            else:
                category_result = "FAIL"
        else:
            category_result = "N/A"

        print(
            f"Sentiment: {sentiment_result} "
            f"(expected: {expected_sentiment}, "
            f"predicted: {predicted_sentiment})"
        )

        print(
            f"Complaint detection: {complaint_result} "
            f"(expected: {expected_complaint}, "
            f"predicted: {predicted_complaint})"
        )

        if expected_complaint:
            print(
                f"Complaint category: {category_result} "
                f"(expected: {expected_category}, "
                f"predicted: {predicted_category or 'None'})"
            )

    print("\n" + "=" * 50)
    print("ASAKE GOLD-STANDARD EVALUATION RESULTS")
    print("=" * 50)

    print("\nEVALUATION COVERAGE")
    print("Total examples:", len(examples))
    print("Successfully analysed:", sentiment_total)
    print("Failed analyses:", failed_reviews)

    print("\nSENTIMENT ACCURACY")
    print(
        f"{sentiment_correct}/{sentiment_total} "
        f"({calculate_accuracy(sentiment_correct, sentiment_total)}%)"
    )

    print("\nCOMPLAINT DETECTION ACCURACY")
    print(
        f"{complaint_correct}/{complaint_total} "
        f"({calculate_accuracy(complaint_correct, complaint_total)}%)"
    )

    print("\nCOMPLAINT CATEGORY ACCURACY")
    print(
        f"{category_correct}/{category_total} "
        f"({calculate_accuracy(category_correct, category_total)}%)"
    )

    print("\n" + "=" * 50)
    print("EVALUATION COMPLETED")
    print("=" * 50)

    print(
        "\nNote: These scores measure performance on this "
        "12-example evaluation dataset. They should not be "
        "treated as proof of accuracy across all festival reviews."
    )
