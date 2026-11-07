from app.self_check import run_self_check
from app.ai.qa import ask_festival_question
from collections import defaultdict
from app.evaluation import evaluate_gold_standard
from app.ingest import import_reviews
from app.storage import load_reviews, add_reviews

from app.analysis_storage import (
    load_analyses,
    save_analysis,
    get_analysis,
)

from app.analytics.comparison import (
    run_festival_comparison,
    get_festival_names,
    compare_festival_data,
)

from app.exports import export_report
from app.analytics.insights import build_intelligence_report

from app.ai.gemini import (
    analyze_review,
    GeminiConfigurationError,
    GeminiAnalysisError,
)


def display_menu():
    print("\n===================================")
    print("       ASAKE - VIBECHECK AI")
    print("   FESTIVAL FEEDBACK DETECTIVE")
    print("===================================")

    print("1. Import Festival Reviews")
    print("2. List Imported Reviews")
    print("3. View Import Statistics")
    print("4. Analyse a Review with Gemini")
    print("5. Generate Festival Intelligence Report")
    print("6. Compare Festivals")
    print("7. Ask Questions About Festival Feedback")
    print("8. Export Festival Reports")
    print("9. Run Engineering Self-Check")
    print("10. Evaluate Gemini Against Gold Standard")
    print("0. Exit")

    print("===================================")


def import_festival_reviews():
    file_path = input("\nEnter CSV file path: ").strip()

    if not file_path:
        print("Please provide a file path.")
        return

    try:
        existing_reviews = load_reviews()

        result = import_reviews(file_path, existing_reviews)

        if not result["success"]:
            print("\nImport failed:", result["error"])
            return

        storage_result = add_reviews(result["accepted"])

        print("\n========== IMPORT SUMMARY ==========")
        print("Total processed:", result["total"])
        print("Accepted:", storage_result["added"])
        print("Rejected:", result["rejected_count"])
        print("Duplicates skipped:", storage_result["skipped"])

        if result["rejected"]:
            print("\nRejected Reviews:")

            for rejected in result["rejected"]:
                print(
                    f"\nRow {rejected['row']}: "
                    f"{rejected['errors']}"
                )

        print("\nImport completed.")

    except (OSError, ValueError, TypeError) as error:
        print("\nUnable to complete import:", error)


def list_reviews():
    try:
        reviews = load_reviews()

        if not reviews:
            print("\nNo reviews have been imported yet.")
            return

        print("\n========== IMPORTED REVIEWS ==========")

        for review in reviews:
            print(f"\nID: {review['id']}")
            print(f"Event: {review['event']}")
            print(f"Review: {review['text']}")
            print(f"Date: {review['created_at']}")

        print(f"\nTotal reviews: {len(reviews)}")

    except (OSError, ValueError) as error:
        print("\nUnable to retrieve reviews:", error)


def view_statistics():
    try:
        reviews = load_reviews()

        print("\n========== REVIEW STATISTICS ==========")
        print("Total stored reviews:", len(reviews))

        events = {}

        for review in reviews:
            event = review["event"]
            events[event] = events.get(event, 0) + 1

        print("\nReviews by event:")

        for event, count in events.items():
            print(f"{event}: {count}")

    except (OSError, ValueError) as error:
        print("\nUnable to retrieve statistics:", error)


def display_analysis(analysis):
    """Display one Gemini analysis."""

    print("\n========== ANALYSIS RESULTS ==========")

    print("Sentiment:", analysis["sentiment"].upper())

    print("\nEmotions:")
    for emotion in analysis["emotions"]:
        print("-", emotion)

    print("\nTopics:")
    for topic in analysis["topics"]:
        print("-", topic)

    print(
        "\nComplaint detected:",
        "Yes" if analysis["complaint_detected"] else "No"
    )

    print(
        "Complaint summary:",
        analysis["complaint_summary"] or "No complaint identified."
    )

    print("\nRecommendation:")
    print(analysis["recommendation"])

    print("\nExperience summary:")
    print(analysis["summary"])

    print("\n=====================================")


def analyze_festival_review():
    """Select and analyse one review, reusing cached results."""

    try:
        reviews = load_reviews()

        if not reviews:
            print("\nNo reviews available for analysis.")
            return

        print("\n========== SELECT A REVIEW ==========")

        for index, review in enumerate(reviews, start=1):
            print(
                f"{index}. [{review['event']}] "
                f"{review['text']}"
            )

        print("0. Return to main menu")

        choice = input("\nSelect a review number: ").strip()

        if choice == "0":
            return

        try:
            review_number = int(choice)
        except ValueError:
            print("\nPlease enter a valid number.")
            return

        if not 1 <= review_number <= len(reviews):
            print("\nThat review number does not exist.")
            return

        selected_review = reviews[review_number - 1]

        print("\n========== GEMINI ANALYSIS ==========")
        print("Festival:", selected_review["event"])
        print("Review:", selected_review["text"])

        # Check whether this review was analysed before.
        analysis = get_analysis(selected_review["id"])

        if analysis is not None:
            print("\nUsing previously saved analysis.")
        else:
            print("\nAnalysing review with Gemini...")

            analysis = analyze_review(selected_review)

            save_analysis(
                selected_review["id"],
                selected_review["event"],
                analysis,
            )

            print("\nAnalysis saved successfully.")

        display_analysis(analysis)

    except GeminiConfigurationError as error:
        print("\nGemini configuration problem:", error)

    except GeminiAnalysisError as error:
        print("\nGemini analysis problem:", error)

    except (OSError, ValueError, TypeError, KeyError) as error:
        print("\nUnable to analyse review:", error)


def print_intelligence_report(report, title):
    """Display the complete festival management intelligence report."""

    print(f"\n========== {title} ==========")

    # 1. Review coverage
    print("\nREVIEW COVERAGE")
    print("Total reviews:", report["total_reviews"])
    print("Analysed reviews:", report["analyzed_reviews"])
    print("Awaiting analysis:", report["unanalyzed_reviews"])

    # 2. Performance indicators
    performance = report.get("performance_summary", {})

    print("\nFESTIVAL PERFORMANCE INDICATORS")
    print(
        "Customer Sentiment Index:",
        f"{performance.get('sentiment_index', 0)}/100"
    )
    print(
        "Complaint Rate:",
        f"{performance.get('complaint_rate', 0)}%"
    )
    print(
        "Reviews containing complaints:",
        performance.get("complaint_reviews", 0)
    )

    print(
        "Main Concern:",
        performance.get("main_concern") or "None identified"
    )

    print("\nPOSITIVE HIGHLIGHTS")

    highlights = performance.get("positive_highlights", [])

    if highlights:
        for topic, count in highlights:
            print(f"- {topic}: {count} positive mention(s)")
    else:
        print("No positive highlights identified.")

    # 3. Sentiment distribution
    print("\nSENTIMENT DISTRIBUTION")

    for sentiment, count in report["sentiment_counts"].items():
        percentage = report["sentiment_percentages"][sentiment]

        print(f"{sentiment.title()}: {count} ({percentage}%)")

    # 4. Most discussed topics
    print("\nMOST DISCUSSED TOPICS")

    if report["topic_counts"]:
        for topic, count in report["topic_counts"][:5]:
            print(f"{topic}: {count} mentions")
    else:
        print("No topic data available.")

    # 5. Individual complaints
    print("\nINDIVIDUAL COMPLAINTS")

    if report["complaint_counts"]:
        for complaint, count in report["complaint_counts"]:
            print(f"- {complaint} ({count} occurrence(s))")
    else:
        print("No complaints identified.")

    # 6. Complaint categories
    print("\nCOMPLAINT CATEGORIES")

    categories = report.get("complaint_categories", [])

    if categories:
        for item in categories:

            print(
                f"\n{item['category']} "
                f"({item['count']} complaint(s))"
            )

            for issue in item["issues"]:
                print(
                    f"  - Review {issue['review_id']} "
                    f"[{issue['event']}]"
                )
                print(f"    Issue: {issue['complaint']}")
                print(f"    Sentiment: {issue['sentiment'].title()}")

    else:
        print("No complaint categories identified.")

    # 7. Recurring complaints
    print("\nRECURRING COMPLAINT CATEGORIES")

    if report["recurring_complaints"]:
        for item in report["recurring_complaints"]:
            print(
                f"- {item['complaint']} "
                f"({item['count']} occurrences)"
            )
    else:
        print("No recurring complaint categories identified yet.")

    # 8. Priority rankings
    print("\nISSUE PRIORITY RANKINGS")

    priorities = report.get("priority_insights", [])

    if priorities:
        for index, item in enumerate(priorities, start=1):
            print(
                f"{index}. {item['category']} "
                f"| Priority: {item['priority']} "
                f"| Score: {item['score']} "
                f"| Complaints: {item['count']} "
                f"| Negative reviews: {item['negative_count']}"
            )
    else:
        print("No priority insights available.")

    # 9. Management action plan
    print("\nFESTIVAL MANAGEMENT ACTION PLAN")

    actions = report.get("management_actions", [])

    if actions:
        for index, item in enumerate(actions, start=1):

            print(
                f"\n{index}. {item['category']} "
                f"[{item['priority']} PRIORITY]"
            )

            print(f"   Priority score: {item['score']}")
            print(f"   Complaints: {item['complaint_count']}")
            print(f"   Related reviews: {', '.join(item['review_ids'])}")
            print(f"   Recommended action: {item['action']}")

    else:
        print("No management actions required.")

    # 10. Individual Gemini recommendations
    print("\nINDIVIDUAL AI RECOMMENDATIONS")

    if report["recommendations"]:
        for item in report["recommendations"]:
            print(
                f"- Review {item['review_id']}: "
                f"{item['recommendation']}"
            )
    else:
        print("No individual recommendations available.")

    print("\n=====================================")



def generate_festival_intelligence():
    """Analyse outstanding reviews and generate festival insights."""

    try:
        reviews = load_reviews()

        if not reviews:
            print("\nNo reviews are available.")
            return

        analyses = load_analyses()

        analysed_ids = {
            record.get("review_id")
            for record in analyses
        }

        pending_reviews = [
            review
            for review in reviews
            if review.get("id") not in analysed_ids
        ]

        print("\n========== FESTIVAL INTELLIGENCE ==========")
        print("Total reviews:", len(reviews))
        print("Already analysed:", len(analyses))
        print("Awaiting analysis:", len(pending_reviews))

        if pending_reviews:
            print(
                f"\nVibeCheck needs to analyse "
                f"{len(pending_reviews)} additional review(s)."
            )

            confirmation = input(
                "Continue with Gemini analysis? (y/n): "
            ).strip().lower()

            if confirmation != "y":
                print("\nReport generation cancelled.")
                return

            for index, review in enumerate(pending_reviews, start=1):
                print(
                    f"\nAnalysing review {index} "
                    f"of {len(pending_reviews)}: {review['id']}"
                )

                try:
                    analysis = analyze_review(review)

                    save_analysis(
                        review["id"],
                        review["event"],
                        analysis,
                    )

                    print("Analysis saved.")

                except GeminiAnalysisError as error:
                    print("\nGemini could not complete the analysis:", error)
                    print("Stopping batch processing.")
                    break

        analyses = load_analyses()

        # Generate the overall report.
        report = build_intelligence_report(reviews, analyses)

        if report["analyzed_reviews"] == 0:
            print("\nNo completed analyses are available for a report.")
            return

        print_intelligence_report(
            report,
            "OVERALL FESTIVAL INTELLIGENCE",
        )

        # Generate a separate report for each event.
        event_groups = defaultdict(list)

        for review in reviews:
            event_groups[review["event"]].append(review)

        for event, event_reviews in event_groups.items():
            event_report = build_intelligence_report(
                event_reviews,
                analyses,
            )

            if event_report["analyzed_reviews"] > 0:
                print_intelligence_report(
                    event_report,
                    f"INTELLIGENCE: {event}",
                )

        if report["unanalyzed_reviews"] > 0:
            print(
                "\nNote: This report is based on completed analyses. "
                "Some reviews are still awaiting analysis."
            )

    except GeminiConfigurationError as error:
        print("\nGemini configuration problem:", error)

    except GeminiAnalysisError as error:
        print("\nGemini analysis problem:", error)

    except (OSError, ValueError, TypeError, KeyError) as error:
        print("\nUnable to generate intelligence report:", error)

def ask_festival_question_menu():
    """Allow users to ask questions about stored festival feedback."""

    try:
        reviews = load_reviews()
        analyses = load_analyses()

        if not reviews:
            print("\nNo festival reviews are available.")
            return

        print("\n========== ASAKE FESTIVAL ASSISTANT ==========")
        print("Ask questions about your stored festival feedback.")
        print("Enter 0 to return to the main menu.")

        while True:
            question = input("\nYour question: ").strip()

            if question == "0":
                return

            if not question:
                print("Please enter a question.")
                continue

            print("\nASAKE is reviewing the available evidence...")

            answer = ask_festival_question(
                question,
                reviews,
                analyses,
            )

            print("\n========== ASAKE RESPONSE ==========")
            print(answer)
            print("\n====================================")

    except GeminiConfigurationError as error:
        print("\nGemini configuration problem:", error)

    except GeminiAnalysisError as error:
        print("\nAI question-answering problem:", error)

    except (OSError, ValueError, TypeError, KeyError) as error:
        print("\nUnable to answer your question:", error)

def export_festival_reports():
    """Export overall, individual, or comparison intelligence reports."""

    try:
        reviews = load_reviews()
        analyses = load_analyses()

        if not reviews:
            print("\nNo festival reviews are available to export.")
            return

        print("\n========== ASAKE REPORT EXPORT ==========")
        print("1. Export Overall Festival Intelligence")
        print("2. Export Individual Festival Report")
        print("3. Export Festival Comparison")
        print("0. Return to Main Menu")

        report_choice = input("\nSelect report type: ").strip()

        if report_choice == "0":
            return

        report = None
        filename = None

        # OPTION 1: Overall intelligence report
        if report_choice == "1":

            report = build_intelligence_report(
                reviews,
                analyses,
            )

            filename = "overall_festival_intelligence"

        # OPTION 2: Individual festival report
        elif report_choice == "2":

            festivals = get_festival_names(reviews)

            print("\n========== SELECT FESTIVAL ==========")

            for index, festival in enumerate(festivals, start=1):
                print(f"{index}. {festival}")

            print("0. Cancel")

            choice = input("\nSelect festival: ").strip()

            if choice == "0":
                return

            if not choice.isdigit():
                print("\nPlease enter a valid number.")
                return

            festival_number = int(choice)

            if not 1 <= festival_number <= len(festivals):
                print("\nInvalid festival selection.")
                return

            selected_event = festivals[festival_number - 1]

            event_reviews = [
                review for review in reviews
                if review.get("event") == selected_event
            ]

            report = build_intelligence_report(
                event_reviews,
                analyses,
            )

            filename = selected_event.replace(" ", "_").lower()

        # OPTION 3: Festival comparison
        elif report_choice == "3":

            festivals = get_festival_names(reviews)

            if len(festivals) < 2:
                print("\nAt least two festivals are required.")
                return

            print("\n========== SELECT FESTIVALS ==========")

            for index, festival in enumerate(festivals, start=1):
                print(f"{index}. {festival}")

            first_choice = input(
                "\nSelect first festival: "
            ).strip()

            second_choice = input(
                "Select second festival: "
            ).strip()

            if not first_choice.isdigit() or not second_choice.isdigit():
                print("\nPlease enter valid festival numbers.")
                return

            first_number = int(first_choice)
            second_number = int(second_choice)

            if not (
                1 <= first_number <= len(festivals)
                and 1 <= second_number <= len(festivals)
            ):
                print("\nInvalid festival selection.")
                return

            if first_number == second_number:
                print("\nPlease select two different festivals.")
                return

            report = compare_festival_data(
                reviews,
                analyses,
                festivals[first_number - 1],
                festivals[second_number - 1],
            )

            filename = "festival_comparison"

        else:
            print("\nInvalid report selection.")
            return

        if report is None:
            print("\nUnable to prepare report.")
            return

        print("\n========== EXPORT FORMAT ==========")
        print("1. JSON")
        print("2. CSV")
        print("0. Cancel")

        format_choice = input("\nChoose export format: ").strip()

        if format_choice == "0":
            return

        formats = {
            "1": "json",
            "2": "csv",
        }

        export_format = formats.get(format_choice)

        if export_format is None:
            print("\nInvalid export format.")
            return

        file_path = export_report(
            report,
            filename,
            export_format,
        )

        print("\n========== EXPORT SUCCESSFUL ==========")
        print("Report type:", filename.replace("_", " ").title())
        print("Format:", export_format.upper())
        print("Saved location:", file_path)
        print("\nYour report is ready.")

    except (OSError, ValueError, TypeError, KeyError) as error:
        print("\nUnable to export report:", error)

def main():
    while True:
        display_menu()

        choice = input("Select an option: ").strip()

        if choice == "1":
            import_festival_reviews()

        elif choice == "2":
            list_reviews()

        elif choice == "3":
            view_statistics()

        elif choice == "4":
            analyze_festival_review()

        elif choice == "5":
            generate_festival_intelligence()

        elif choice == "6":
            run_festival_comparison()

        elif choice == "7":
            ask_festival_question_menu()

        elif choice == "8":
            export_festival_reports()

        elif choice == "9":
            run_self_check()

        elif choice == "10":
            try:
                evaluate_gold_standard()
            except (
                OSError,
                ValueError,
                TypeError,
                KeyError,
                GeminiConfigurationError,
            ) as error:
                print("\nUnable to run evaluation:", error)
                print("\nUnable to run evaluation:", error)

        elif choice == "0":
            print("\nThank you for using Asake!")
            break

        else:
            print(
                "\nInvalid choice. "
                "Please select an option between 0 and 10."
            )


if __name__ == "__main__":
    main()