from app.analytics.insights import build_intelligence_report
from app.storage import load_reviews
from app.analysis_storage import load_analyses


def get_festival_names(reviews):
    """Return a sorted list of unique festival names."""

    return sorted({
        review.get("event", "Unknown")
        for review in reviews
    })


def compare_festival_data(reviews, analyses, first_event, second_event):
    """Build intelligence reports for two selected festivals."""

    first_reviews = [
        review for review in reviews
        if review.get("event") == first_event
    ]

    second_reviews = [
        review for review in reviews
        if review.get("event") == second_event
    ]

    first_review_ids = {
        str(review.get("id"))
        for review in first_reviews
    }

    second_review_ids = {
        str(review.get("id"))
        for review in second_reviews
    }

    first_analyses = [
        analysis for analysis in analyses
        if str(analysis.get("review_id")) in first_review_ids
    ]

    second_analyses = [
        analysis for analysis in analyses
        if str(analysis.get("review_id")) in second_review_ids
    ]

    first_report = build_intelligence_report(
        first_reviews,
        first_analyses,
    )

    second_report = build_intelligence_report(
        second_reviews,
        second_analyses,
    )

    return {
        "first_event": first_event,
        "second_event": second_event,
        "first_report": first_report,
        "second_report": second_report,
    }


def display_festival_comparison(comparison):
    """Display a side-by-side intelligence comparison."""

    first_name = comparison["first_event"]
    second_name = comparison["second_event"]

    first = comparison["first_report"]
    second = comparison["second_report"]

    first_performance = first["performance_summary"]
    second_performance = second["performance_summary"]

    print("\n" + "=" * 55)
    print("          ASAKE FESTIVAL COMPARISON")
    print("=" * 55)

    print(f"\nFestival A: {first_name}")
    print(f"Festival B: {second_name}")

    # 1. Review coverage
    print("\n========== REVIEW COVERAGE ==========")

    print(
        f"{'Metric':<25}"
        f"{'Festival A':>14}"
        f"{'Festival B':>14}"
    )

    print("-" * 53)

    print(
        f"{'Total reviews':<25}"
        f"{first['total_reviews']:>14}"
        f"{second['total_reviews']:>14}"
    )

    print(
        f"{'Analysed reviews':<25}"
        f"{first['analyzed_reviews']:>14}"
        f"{second['analyzed_reviews']:>14}"
    )

    print(
        f"{'Awaiting analysis':<25}"
        f"{first['unanalyzed_reviews']:>14}"
        f"{second['unanalyzed_reviews']:>14}"
    )

    # 2. Performance comparison
    print("\n========== PERFORMANCE COMPARISON ==========")

    first_index = first_performance["sentiment_index"]
    second_index = second_performance["sentiment_index"]

    first_complaint_rate = first_performance["complaint_rate"]
    second_complaint_rate = second_performance["complaint_rate"]

    print(
        f"{'Metric':<25}"
        f"{'Festival A':>14}"
        f"{'Festival B':>14}"
    )

    print("-" * 53)

    print(
        f"{'Sentiment Index':<25}"
        f"{str(first_index) + '/100':>14}"
        f"{str(second_index) + '/100':>14}"
    )

    print(
        f"{'Complaint Rate':<25}"
        f"{str(first_complaint_rate) + '%':>14}"
        f"{str(second_complaint_rate) + '%':>14}"
    )

    # 3. Sentiment comparison
    print("\n========== SENTIMENT COMPARISON ==========")

    for sentiment in ("positive", "negative", "neutral"):

        first_count = first["sentiment_counts"][sentiment]
        second_count = second["sentiment_counts"][sentiment]

        print(
            f"{sentiment.title():<15}"
            f"{first_count:>10}"
            f"{second_count:>15}"
        )

    print(f"\n{'':<15}{'Festival A':>10}{'Festival B':>15}")

    # 4. Complaint categories
    print("\n========== COMPLAINT COMPARISON ==========")

    first_categories = {
        item["category"]: item["count"]
        for item in first["complaint_categories"]
    }

    second_categories = {
        item["category"]: item["count"]
        for item in second["complaint_categories"]
    }

    all_categories = sorted(
        set(first_categories) | set(second_categories)
    )

    if all_categories:

        print(
            f"{'Category':<30}"
            f"{'Festival A':>12}"
            f"{'Festival B':>12}"
        )

        print("-" * 54)

        for category in all_categories:

            print(
                f"{category:<30}"
                f"{first_categories.get(category, 0):>12}"
                f"{second_categories.get(category, 0):>12}"
            )

    else:
        print("Neither festival has recorded complaints.")

    # 5. Positive highlights
    print("\n========== POSITIVE HIGHLIGHTS ==========")

    print(f"\n{first_name}:")

    if first_performance["positive_highlights"]:
        for topic, count in first_performance["positive_highlights"]:
            print(f"- {topic}: {count} positive mention(s)")
    else:
        print("No positive highlights identified.")

    print(f"\n{second_name}:")

    if second_performance["positive_highlights"]:
        for topic, count in second_performance["positive_highlights"]:
            print(f"- {topic}: {count} positive mention(s)")
    else:
        print("No positive highlights identified.")

    # 6. Overall assessment
    print("\n========== OVERALL ASSESSMENT ==========")

    if not first["analyzed_reviews"] or not second["analyzed_reviews"]:
        print(
            "A fair comparison cannot be completed because "
            "one or both festivals have no analysed reviews."
        )

    else:
        sentiment_winner = (
            first_name if first_index > second_index
            else second_name if second_index > first_index
            else None
        )

        complaint_winner = (
            first_name if first_complaint_rate < second_complaint_rate
            else second_name if second_complaint_rate < first_complaint_rate
            else None
        )

        if sentiment_winner:
            print(
                f"Stronger customer sentiment: {sentiment_winner}"
            )
        else:
            print("Customer sentiment: Both festivals are equal.")

        if complaint_winner:
            print(
                f"Lower complaint rate: {complaint_winner}"
            )
        else:
            print("Complaint rate: Both festivals are equal.")

        if (
            sentiment_winner == first_name
            and complaint_winner == first_name
        ):
            print(f"\nOverall stronger performance: {first_name}")

        elif (
            sentiment_winner == second_name
            and complaint_winner == second_name
        ):
            print(f"\nOverall stronger performance: {second_name}")

        else:
            print(
                "\nOverall assessment: Mixed results. "
                "Each festival performs better on a different indicator, "
                "or the indicators are tied."
            )

    # 7. Management recommendations
    print("\n========== MANAGEMENT RECOMMENDATIONS ==========")

    for event_name, report in (
        (first_name, first),
        (second_name, second),
    ):

        print(f"\n{event_name}:")

        actions = report["management_actions"]

        if actions:
            for action in actions:
                print(
                    f"- {action['category']} "
                    f"[{action['priority']} priority]: "
                    f"{action['action']}"
                )
        else:
            print("No complaint-based management actions identified.")

    # 8. Data quality warning
    print("\n========== DATA NOTES ==========")

    print(
        "This comparison uses completed AI analyses only. "
        "Festivals with pending reviews may have incomplete results."
    )

    print(
        "Small review samples may not represent the experience "
        "of all festival attendees."
    )

    print("\n" + "=" * 55)


def run_festival_comparison():
    """Allow the user to select and compare two festivals."""

    try:
        reviews = load_reviews()
        analyses = load_analyses()

        if not reviews:
            print("\nNo festival reviews are available.")
            return

        festivals = get_festival_names(reviews)

        if len(festivals) < 2:
            print(
                "\nAt least two different festivals are required "
                "to perform a comparison."
            )
            return

        print("\n========== SELECT FESTIVALS ==========")

        for index, festival in enumerate(festivals, start=1):
            print(f"{index}. {festival}")

        print("0. Return to main menu")

        first_choice = input(
            "\nSelect the first festival: "
        ).strip()

        if first_choice == "0":
            return

        second_choice = input(
            "Select the second festival: "
        ).strip()

        if second_choice == "0":
            return

        try:
            first_number = int(first_choice)
            second_number = int(second_choice)

        except ValueError:
            print("\nPlease enter valid festival numbers.")
            return

        if not (
            1 <= first_number <= len(festivals)
            and 1 <= second_number <= len(festivals)
        ):
            print("\nOne or both festival selections are invalid.")
            return

        if first_number == second_number:
            print("\nPlease select two different festivals.")
            return

        first_event = festivals[first_number - 1]
        second_event = festivals[second_number - 1]

        comparison = compare_festival_data(
            reviews,
            analyses,
            first_event,
            second_event,
        )

        display_festival_comparison(comparison)

    except (OSError, ValueError, TypeError, KeyError) as error:
        print("\nUnable to compare festivals:", error)
