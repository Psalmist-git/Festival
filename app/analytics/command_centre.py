"""Data preparation for the VibeCheck command-centre dashboard.

All metrics are derived from imported reviews and saved AI analyses.
This module does not make external API calls or invent live activity.
"""


VALID_SENTIMENTS = {"positive", "neutral", "negative"}


def build_command_centre_data(reviews, analyses, report):
    """Build dashboard monitoring data from existing application records."""

    analysis_lookup = {
        str(record.get("review_id")): record.get("analysis", {})
        for record in analyses
        if record.get("review_id") is not None
        and isinstance(record.get("analysis"), dict)
    }

    festival_map = {}
    complaint_activity = []

    for review in reviews:
        review_id = str(review.get("id", ""))
        analysis = analysis_lookup.get(review_id)

        if analysis is None:
            continue

        event = str(review.get("event") or "Unspecified festival")
        festival = festival_map.setdefault(
            event,
            {
                "event": event,
                "analysed_reviews": 0,
                "positive": 0,
                "neutral": 0,
                "negative": 0,
                "complaint_reviews": 0,
            },
        )

        festival["analysed_reviews"] += 1
        sentiment = str(analysis.get("sentiment", "")).lower()

        if sentiment in VALID_SENTIMENTS:
            festival[sentiment] += 1

        if analysis.get("complaint_detected") is True:
            festival["complaint_reviews"] += 1
            complaint_activity.append({
                "review_id": review.get("id", "Unknown"),
                "event": event,
                "created_at": str(review.get("created_at") or ""),
                "sentiment": sentiment if sentiment in VALID_SENTIMENTS else "unknown",
                "complaint": str(
                    analysis.get("complaint_summary")
                    or analysis.get("summary")
                    or "A complaint was flagged in the saved AI analysis."
                ),
            })

    festival_performance = []

    for festival in festival_map.values():
        known_sentiments = sum(
            festival[key] for key in VALID_SENTIMENTS
        )
        festival["sentiment_index"] = round(
            (
                (festival["positive"] + festival["neutral"] * 0.5)
                / known_sentiments * 100
            ) if known_sentiments else 0,
            1,
        )
        festival["negative_rate"] = round(
            festival["negative"] / known_sentiments * 100,
            1,
        ) if known_sentiments else 0
        festival_performance.append(festival)

    festival_performance.sort(
        key=lambda item: (item["analysed_reviews"], item["sentiment_index"]),
        reverse=True,
    )

    complaint_categories = report.get("complaint_categories", [])
    complaint_monitor = sorted(
        complaint_categories,
        key=lambda item: item.get("count", 0),
        reverse=True,
    )[:5]

    priority_alerts = [
        item for item in report.get("priority_insights", [])
        if item.get("priority") == "High"
    ][:4]

    complaint_activity.sort(
        key=lambda item: item["created_at"],
        reverse=True,
    )

    performance = report.get("performance_summary", {})
    sentiment_counts = report.get("sentiment_counts", {})
    sentiment_total = sum(
        sentiment_counts.get(key, 0) for key in VALID_SENTIMENTS
    )
    positive_rate = round(
        sentiment_counts.get("positive", 0) / sentiment_total * 100,
        1,
    ) if sentiment_total else 0

    top_concern = performance.get("main_concern")
    top_positive = performance.get("positive_highlights", [])
    recommendations = report.get("recommendations", [])

    if report.get("analyzed_reviews", 0) == 0:
        intelligence_summary = (
            "No saved AI analyses are available yet. Import attendee reviews "
            "and run AI analysis to activate evidence-based monitoring."
        )
    else:
        parts = [
            f"VibeCheck has processed {report.get('analyzed_reviews', 0)} "
            f"of {report.get('total_reviews', 0)} imported reviews. "
            f"{positive_rate}% of classified feedback is positive."
        ]

        if top_concern:
            parts.append(
                f"The most prominent complaint area is {top_concern}; "
                "review the issue monitor and linked review IDs."
            )
        else:
            parts.append(
                "No complaint category has been identified in the saved analyses."
            )

        if top_positive:
            topic_names = ", ".join(
                str(item[0]) for item in top_positive[:3]
            )
            parts.append(
                f"Positive feedback most often highlights {topic_names}."
            )

        intelligence_summary = " ".join(parts)

    latest_recommendations = recommendations[-3:][::-1]

    return {
        "festival_performance": festival_performance[:6],
        "complaint_monitor": complaint_monitor,
        "priority_alerts": priority_alerts,
        "complaint_activity": complaint_activity[:5],
        "intelligence_summary": intelligence_summary,
        "latest_recommendations": latest_recommendations,
        "sentiment_total": sentiment_total,
        "positive_rate": positive_rate,
        "high_priority_count": len(priority_alerts),
        "tracked_complaint_categories": len(complaint_categories),
    }
