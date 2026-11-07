def run_self_check():
    """
    Assess the developer's understanding of ASAKE.

    Multiple-choice questions are marked automatically.
    Written answers are collected for mentor review.

    This function does not modify reviews, analyses, or reports.
    """

    multiple_choice_questions = [
        {
            "question": "What is the main purpose of ASAKE?",
            "options": [
                "A. To sell festival tickets",
                "B. To analyse festival feedback and identify insights",
                "C. To manage festival performers",
                "D. To design festival posters",
            ],
            "answer": "B",
            "explanation": (
                "ASAKE analyses festival reviews to identify sentiment, "
                "complaints, recurring issues, and recommendations."
            ),
        },
        {
            "question": "Why does ASAKE store Gemini analyses separately?",
            "options": [
                "A. To delete original reviews",
                "B. To avoid analysing the same review repeatedly",
                "C. To create new festival events",
                "D. To replace the review database",
            ],
            "answer": "B",
            "explanation": (
                "Saved analyses can be reused without making another "
                "Gemini API request for the same review."
            ),
        },
        {
            "question": "What is the purpose of the complaint categorisation feature?",
            "options": [
                "A. To group similar problems into meaningful categories",
                "B. To remove negative reviews",
                "C. To change festival names",
                "D. To generate ticket numbers",
            ],
            "answer": "A",
            "explanation": (
                "It groups complaints into categories such as Food & "
                "Catering, Ticket Pricing, and Security & Safety."
            ),
        },
        {
            "question": "What should ASAKE do when the available reviews "
                        "cannot answer a user's question?",
            "options": [
                "A. Invent an answer",
                "B. Guess what happened",
                "C. Explain that the available evidence is insufficient",
                "D. Delete the question",
            ],
            "answer": "C",
            "explanation": (
                "AI answers should be grounded in available festival "
                "feedback rather than unsupported assumptions."
            ),
        },
    ]

    written_questions = [
        {
            "question": (
                "Explain the journey of a festival review from CSV import "
                "to storage in ASAKE."
            ),
            "review_points": [
                "CSV file is read by the ingestion module.",
                "Review data is converted into the expected structure.",
                "Duplicate review IDs are prevented.",
                "Valid reviews are saved to JSON storage.",
            ],
        },
        {
            "question": (
                "Explain how ASAKE uses Gemini to analyse a festival review."
            ),
            "review_points": [
                "The review is sent to the Gemini integration.",
                "Gemini analyses the review.",
                "The response is expected in a structured format.",
                "The analysis is saved separately for reuse.",
            ],
        },
        {
            "question": (
                "What is the difference between a sentiment analysis "
                "and a complaint category?"
            ),
            "review_points": [
                "Sentiment describes the overall emotional tone.",
                "Complaint categories identify the subject of a problem.",
                "A negative review can belong to a specific complaint category.",
                "One review can contain more than one topic.",
            ],
        },
        {
            "question": (
                "Why is it important for ASAKE's AI question-answering "
                "feature to use evidence from actual reviews?"
            ),
            "review_points": [
                "It reduces unsupported or invented answers.",
                "It keeps responses connected to customer feedback.",
                "Review IDs help identify supporting evidence.",
                "The system should admit when evidence is insufficient.",
            ],
        },
    ]

    multiple_choice_score = 0
    written_responses = []

    print("\n" + "=" * 55)
    print("              ASAKE ENGINEERING SELF-CHECK")
    print("=" * 55)

    print("\nSECTION A: MULTIPLE-CHOICE QUESTIONS")
    print("Answer each question by entering A, B, C, or D.")

    for index, question in enumerate(
        multiple_choice_questions,
        start=1,
    ):
        print(f"\nQuestion {index}: {question['question']}")

        for option in question["options"]:
            print(option)

        while True:
            answer = input("Your answer: ").strip().upper()

            if answer in ("A", "B", "C", "D"):
                break

            print("Invalid choice. Enter A, B, C, or D.")

        if answer == question["answer"]:
            print("Correct!")
            multiple_choice_score += 1
        else:
            print("Not quite.")
            print("Correct answer:", question["answer"])

        print("Explanation:", question["explanation"])

    print("\n" + "=" * 55)
    print("SECTION A RESULT")
    print("=" * 55)

    print(
        f"Multiple-choice score: "
        f"{multiple_choice_score}/"
        f"{len(multiple_choice_questions)}"
    )

    percentage = (
        multiple_choice_score
        / len(multiple_choice_questions)
    ) * 100

    print(f"Score percentage: {percentage:.1f}%")

    if multiple_choice_score == 4:
        print("Excellent understanding!")
    elif multiple_choice_score >= 3:
        print("Good work. Review the question you missed.")
    elif multiple_choice_score >= 2:
        print("Fair attempt. Revisit the project concepts.")
    else:
        print("More revision is recommended.")

    print("\n" + "=" * 55)
    print("SECTION B: WRITTEN QUESTIONS")
    print("=" * 55)

    print(
        "Answer in your own words. These responses are not "
        "automatically graded; they are intended for mentor review."
    )

    for index, question in enumerate(
        written_questions,
        start=1,
    ):
        print(f"\nWritten Question {index}:")
        print(question["question"])

        response = input("\nYour explanation: ").strip()

        written_responses.append({
            "question": question["question"],
            "response": response,
            "review_points": question["review_points"],
        })

    print("\n" + "=" * 55)
    print("WRITTEN ANSWERS — MENTOR REVIEW")
    print("=" * 55)

    for index, item in enumerate(written_responses, start=1):
        print(f"\nQuestion {index}:")
        print(item["question"])

        print("\nYour response:")
        print(item["response"] or "[No response provided]")

        print("\nPoints for mentor review:")

        for point in item["review_points"]:
            print("-", point)

    print("\n" + "=" * 55)
    print("ASAKE ENGINEERING SELF-CHECK COMPLETED")
    print("=" * 55)

    print(
        "Your multiple-choice answers have been marked. "
        "Your written explanations are ready for mentor review."
    )
