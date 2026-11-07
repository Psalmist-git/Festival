from collections import Counter, defaultdict


COMPLAINT_CATEGORIES = {
    "Food & Catering": [
        "food", "meal", "catering", "vendor", "queue",
        "queues", "drink", "restaurant", "eating",
    ],
    "Ticket Pricing": [
        "ticket", "price", "pricing", "cost", "expensive",
        "affordable", "payment",
    ],
    "Staff & Customer Service": [
        "staff", "customer service", "rude", "unhelpful",
        "attitude", "service", "unprofessional",
    ],
    "Parking & Transport": [
        "parking", "transport", "traffic", "vehicle",
        "car park", "access",
    ],
    "Sound & Production": [
        "sound", "audio", "music", "speaker", "microphone",
        "dj", "performance", "stage",
    ],
    "Security & Safety": [
        "security", "safety", "unsafe", "theft",
        "crowd control", "emergency",
    ],
    "Venue & Facilities": [
        "venue", "cleanliness", "clean", "comfort",
        "toilet", "restroom", "facility", "facilities",
    ],
}


MANAGEMENT_ACTIONS = {
    "Food & Catering": (
        "Review food vendor performance, improve food quality, "
        "and consider adding vendors or queue-management systems."
    ),
    "Ticket Pricing": (
        "Review ticket pricing against customer expectations. "
        "Consider early-bird offers and clearer ticket-value packages."
    ),
    "Staff & Customer Service": (
        "Provide customer-service training, reinforce staff conduct "
        "standards, and establish a process for handling complaints."
    ),
    "Parking & Transport": (
        "Improve parking signage, traffic coordination, parking "
        "capacity planning, and arrival instructions."
    ),
    "Sound & Production": (
        "Review sound equipment, audio engineering, stage production, "
        "and technical checks before the next event."
    ),
    "Security & Safety": (
        "Review security coverage, emergency procedures, crowd control, "
        "and communication between security teams."
    ),
    "Venue & Facilities": (
        "Inspect venue facilities, improve cleaning schedules, "
        "and address comfort and accessibility concerns."
    ),
    "Other": (
        "Review the original customer feedback and investigate "
        "the issue before deciding on corrective action."
    ),
}


def identify_complaint_category(review, analysis):
    """
    Classify a complaint using its description and original review.

    Complaint wording receives more weight than general discussion
    topics, preventing positive topics from dominating classification.
    """

    complaint_text = str(
        analysis.get("complaint_summary", "")
    ).lower()

    review_text = str(
        review.get("text", "")
    ).lower()

    analysis_summary = str(
        analysis.get("summary", "")
    ).lower()

    topics = " ".join(
        topic for topic in analysis.get("topics", [])
        if isinstance(topic, str)
    ).lower()

    scores = {}

    for category, keywords in COMPLAINT_CATEGORIES.items():

        complaint_score = sum(
            3 for keyword in keywords
            if keyword in complaint_text
        )

        review_score = sum(
            2 for keyword in keywords
            if keyword in review_text
        )

        summary_score = sum(
            1 for keyword in keywords
            if keyword in analysis_summary
        )

        topic_score = sum(
            1 for keyword in keywords
            if keyword in topics
        )

        total_score = (
            complaint_score
            + review_score
            + summary_score
            + topic_score
        )

        if total_score:
            scores[category] = total_score

    if not scores:
        return "Other"

    return max(scores, key=scores.get)


def calculate_priority(count, negative_count):
    """
    Rank issues using complaint frequency and negative sentiment.

    This is an initial ranking model, not a verified severity measure.
    """

    score = (count * 10) + (negative_count * 5)

    if score >= 30:
        priority = "High"
    elif score >= 15:
        priority = "Medium"
    else:
        priority = "Low"

    return {
        "score": score,
        "priority": priority,
    }


def build_intelligence_report(reviews, analyses):
    """Build an intelligence report for a collection of reviews."""

    analysis_lookup = {
        record["review_id"]: record["analysis"]
        for record in analyses
    }

    analyzed_reviews = [
        review for review in reviews
        if review.get("id") in analysis_lookup
    ]

    sentiment_counts = Counter({
        "positive": 0,
        "negative": 0,
        "neutral": 0,
    })

    topic_counts = Counter()
    positive_topic_counts = Counter()
    complaint_counts = Counter()

    category_counts = Counter()
    category_negative_counts = Counter()

    category_details = defaultdict(list)
    recommendations = []

    complaint_review_count = 0

    for review in analyzed_reviews:

        analysis = analysis_lookup[review["id"]]

        sentiment = str(
            analysis.get("sentiment", "")
        ).lower()

        if sentiment in sentiment_counts:
            sentiment_counts[sentiment] += 1

        topics = analysis.get("topics", [])

        for topic in topics:

            if isinstance(topic, str) and topic.strip():

                clean_topic = topic.strip().title()
                topic_counts[clean_topic] += 1

                if sentiment == "positive":
                    positive_topic_counts[clean_topic] += 1

        if analysis.get("complaint_detected"):

            complaint_review_count += 1

            complaint = str(
                analysis.get("complaint_summary", "")
            ).strip()

            if complaint:
                complaint_counts[complaint] += 1

            category = identify_complaint_category(
                review,
                analysis
            )

            category_counts[category] += 1

            if sentiment == "negative":
                category_negative_counts[category] += 1

            category_details[category].append({
                "review_id": review["id"],
                "event": review.get("event", "Unknown"),
                "complaint": complaint or "Complaint detected",
                "sentiment": sentiment,
            })

        recommendation = str(
            analysis.get("recommendation", "")
        ).strip()

        if recommendation:
            recommendations.append({
                "review_id": review["id"],
                "recommendation": recommendation,
            })

    total_reviews = len(reviews)
    analyzed_count = len(analyzed_reviews)

    # Sentiment percentages.
    sentiment_percentages = {}

    for sentiment, count in sentiment_counts.items():

        percentage = (
            (count / analyzed_count) * 100
            if analyzed_count else 0
        )

        sentiment_percentages[sentiment] = round(
            percentage, 1
        )

    # ASAKE sentiment index.
    sentiment_index = 0

    if analyzed_count:
        sentiment_index = round(
            (
                sentiment_counts["positive"]
                + sentiment_counts["neutral"] * 0.5
            )
            / analyzed_count
            * 100,
            1
        )

    # Complaint rate.
    complaint_rate = (
        round(
            (complaint_review_count / analyzed_count) * 100,
            1
        )
        if analyzed_count else 0
    )

    # Group complaints into categories.
    complaint_categories = []

    for category, count in category_counts.most_common():

        complaint_categories.append({
            "category": category,
            "count": count,
            "negative_count": category_negative_counts[category],
            "issues": category_details[category],
        })

    # Rank complaint categories.
    priority_insights = []

    for category, count in category_counts.items():

        priority_data = calculate_priority(
            count,
            category_negative_counts[category]
        )

        priority_insights.append({
            "category": category,
            "count": count,
            "negative_count": category_negative_counts[category],
            "score": priority_data["score"],
            "priority": priority_data["priority"],
        })

    priority_insights.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    # Build management action plan.
    management_actions = []

    for item in priority_insights:

        category = item["category"]

        management_actions.append({
            "category": category,
            "priority": item["priority"],
            "score": item["score"],
            "complaint_count": item["count"],
            "action": MANAGEMENT_ACTIONS.get(
                category,
                MANAGEMENT_ACTIONS["Other"]
            ),
            "review_ids": [
                issue["review_id"]
                for issue in category_details[category]
            ],
        })

    # Identify recurring complaint categories.
    recurring_complaints = [
        {
            "complaint": category,
            "count": count,
        }
        for category, count in category_counts.most_common()
        if count >= 2
    ]

    # Identify the main concern.
    main_concern = (
        priority_insights[0]["category"]
        if priority_insights else None
    )

    # Build performance indicators.
    performance_summary = {
        "sentiment_index": sentiment_index,
        "complaint_rate": complaint_rate,
        "complaint_reviews": complaint_review_count,
        "positive_highlights": positive_topic_counts.most_common(3),
        "main_concern": main_concern,
    }

    return {
        "total_reviews": total_reviews,
        "analyzed_reviews": analyzed_count,
        "unanalyzed_reviews": total_reviews - analyzed_count,
        "sentiment_counts": dict(sentiment_counts),
        "sentiment_percentages": sentiment_percentages,
        "topic_counts": topic_counts.most_common(),
        "complaint_counts": complaint_counts.most_common(),
        "complaint_categories": complaint_categories,
        "recurring_complaints": recurring_complaints,
        "priority_insights": priority_insights,
        "management_actions": management_actions,
        "performance_summary": performance_summary,
        "recommendations": recommendations,
    }