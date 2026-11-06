from app.ingest import import_reviews
from app.storage import load_reviews, add_reviews


def display_menu():
    print("\n===================================")
    print("       ASAKE - VIBECHECK AI")
    print("   FESTIVAL FEEDBACK DETECTIVE")
    print("===================================")

    print("1. Import Festival Reviews")
    print("2. List Imported Reviews")
    print("3. View Import Statistics")
    print("0. Exit")

    print("===================================")


def import_festival_reviews():
    file_path = input("\nEnter CSV file path: ").strip()

    if not file_path:
        print("Please provide a file path.")
        return

    try:
        existing_reviews = load_reviews()

        result = import_reviews(
            file_path,
            existing_reviews
        )

        if not result["success"]:
            print("\nImport failed:", result["error"])
            return

        # Save only validated reviews
        storage_result = add_reviews(
            result["accepted"]
        )

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

        elif choice == "0":
            print("\nThank you for using Asake!")
            break

        else:
            print("\nInvalid choice. Please select 1, 2, 3 or 0.")


if __name__ == "__main__":
    main()