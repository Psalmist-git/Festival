import os
import tempfile

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_file,
)
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from app.storage import load_reviews, add_reviews
from app.models import validate_review
import hashlib
import hmac
from app.analysis_storage import load_analyses, save_analysis
from app.ingest import import_reviews
from app.ai.gemini import analyze_review
from app.analytics.insights import build_intelligence_report
from app.analytics.command_centre import build_command_centre_data
from app.analytics.comparison import (
    get_festival_names,
    compare_festival_data,
)
from app.ai.qa import ask_festival_question
from app.exports import export_report


load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv(
    "FLASK_SECRET_KEY",
    "local-development-key-change-me",
)

app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024


# --------------------------------------------------
# Dashboard
# --------------------------------------------------

@app.route("/")
def dashboard():
    reviews = load_reviews()
    analyses = load_analyses()

    report = build_intelligence_report(reviews, analyses)
    command_centre = build_command_centre_data(reviews, analyses, report)

    total_reviews = len(reviews)
    total_analyses = len(analyses)
    festivals = get_festival_names(reviews)

    return render_template(
        "dashboard.html",
        reviews=reviews,
        analyses=analyses,
        report=report,
        total_reviews=total_reviews,
        total_analyses=total_analyses,
        festivals=festivals,
        command_centre=command_centre,
    )


# --------------------------------------------------
# Reviews
# --------------------------------------------------

@app.route("/reviews")
def reviews_page():
    reviews = load_reviews()
    analyses = load_analyses()

    analysis_ids = {
        str(analysis.get("review_id"))
        for analysis in analyses
        if analysis.get("review_id") is not None
    }

    return render_template(
        "reviews.html",
        reviews=reviews,
        analyses=analyses,
        analysis_ids=analysis_ids,
    )


# --------------------------------------------------
# Import Reviews
# --------------------------------------------------

@app.route("/import", methods=["GET", "POST"])
def import_page():
    if request.method == "POST":

        uploaded_file = request.files.get("file")

        if not uploaded_file or uploaded_file.filename == "":
            flash("Please select a CSV file.", "error")
            return redirect(url_for("import_page"))

        if not uploaded_file.filename.lower().endswith(".csv"):
            flash("Only CSV files are supported currently.", "error")
            return redirect(url_for("import_page"))

        temporary_path = None

        try:
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".csv",
            ) as temporary_file:

                uploaded_file.save(temporary_file)
                temporary_path = temporary_file.name

            existing_reviews = load_reviews()

            result = import_reviews(
                temporary_path,
                existing_reviews=existing_reviews,
            )

            if result.get("success"):
                accepted_reviews = result.get("accepted", [])

                add_reviews(accepted_reviews)

                flash(
                    f"Import completed. "
                    f"{result.get('accepted_count', 0)} reviews accepted.",
                    "success",
                )

            else:
                flash(
                    result.get("message", "Import failed."),
                    "error",
                )

        except Exception as error:
            flash(f"Import error: {error}", "error")

        finally:
            if temporary_path and os.path.exists(temporary_path):
                os.remove(temporary_path)

        return redirect(url_for("import_page"))

    return render_template("import.html")


# --------------------------------------------------
# Gemini Review Analysis
# --------------------------------------------------

@app.route("/analysis", methods=["GET", "POST"])
def analysis_page():

    reviews = load_reviews()
    analyses = load_analyses()

    # Build a dictionary connecting each review ID to its AI analysis.
    analysis_by_id = {
        str(record.get("review_id")): record.get("analysis", {})
        for record in analyses
        if record.get("review_id") is not None
    }

    if request.method == "POST":

        review_id = request.form.get("review_id")

        selected_review = next(
            (
                review
                for review in reviews
                if str(review.get("id")) == str(review_id)
            ),
            None,
        )

        if not selected_review:
            flash("Review not found.", "error")
            return redirect(url_for("analysis_page"))

        try:
            analysis = analyze_review(selected_review)

            save_analysis(
                review_id=selected_review["id"],
                event=selected_review["event"],
                analysis=analysis,
            )

            flash("Review analysis completed successfully.", "success")

        except Exception as error:
            flash(f"Analysis failed: {error}", "error")

        return redirect(url_for("analysis_page"))

    return render_template(
        "analysis.html",
        reviews=reviews,
        analysis_by_id=analysis_by_id,
    )


# --------------------------------------------------
# Festival Intelligence Reports
# --------------------------------------------------

@app.route("/reports")
def reports_page():

    reviews = load_reviews()
    analyses = load_analyses()

    report = build_intelligence_report(
        reviews,
        analyses,
    )

    return render_template(
        "reports.html",
        reviews=reviews,
        analyses=analyses,
        report=report,
    )


# --------------------------------------------------
# Festival Comparison
# --------------------------------------------------

@app.route("/compare", methods=["GET", "POST"])
def compare_page():

    reviews = load_reviews()
    analyses = load_analyses()

    festival_names = get_festival_names(reviews)

    comparison = None

    if request.method == "POST":

        first_event = request.form.get("first_event")
        second_event = request.form.get("second_event")

        if not first_event or not second_event:
            flash("Please select two festivals.", "error")

        elif first_event == second_event:
            flash("Please select two different festivals.", "error")

        else:
            try:
                comparison = compare_festival_data(
                    reviews,
                    analyses,
                    first_event,
                    second_event,
                )

            except Exception as error:
                flash(f"Comparison failed: {error}", "error")

    return render_template(
        "compare.html",
        festival_names=festival_names,
        comparison=comparison,
    )


# --------------------------------------------------
# Festival Feedback Chatbot
# --------------------------------------------------

@app.route("/chat", methods=["GET", "POST"])
def chat_page():

    answer = None
    question = ""

    reviews = load_reviews()
    analyses = load_analyses()

    if request.method == "POST":

        question = request.form.get("question", "").strip()

        if not question:
            flash("Please enter a question.", "error")

        else:
            try:
                answer = ask_festival_question(
                    question,
                    reviews,
                    analyses,
                )

            except Exception as error:
                flash(f"Could not answer your question: {error}", "error")

    return render_template(
        "chat.html",
        question=question,
        answer=answer,
    )


# --------------------------------------------------
# Export Reports
# --------------------------------------------------

@app.route("/exports", methods=["POST"])
def exports_page():

    reviews = load_reviews()
    analyses = load_analyses()

    report = build_intelligence_report(
        reviews,
        analyses,
    )

    export_format = request.form.get(
        "format",
        "json",
    ).lower()

    if export_format not in ["json", "csv"]:
        flash("Unsupported export format.", "error")
        return redirect(url_for("reports_page"))

    requested_filename = request.form.get(
        "filename",
        "vibecheck-festival-report",
    ).strip()

    safe_filename = secure_filename(requested_filename)

    if not safe_filename:
        safe_filename = "vibecheck-festival-report"

    # Remove an extension if the user included one.
    safe_filename = os.path.splitext(safe_filename)[0]

    filename = f"{safe_filename}.{export_format}"

    try:
        exported_path = export_report(
            report,
            filename,
            export_format,
        )

        return send_file(
            exported_path,
            as_attachment=True,
            download_name=filename,
        )

    except Exception as error:
        flash(f"Export failed: {error}", "error")
        return redirect(url_for("reports_page"))


# --------------------------------------------------
# Health Check
# --------------------------------------------------

# --------------------------------------------------
# Signed webhook: receive reviews from external platforms
# --------------------------------------------------

@app.route("/api/webhooks/reviews", methods=["POST"])
def receive_reviews_webhook():
    webhook_secret = os.getenv("VIBECHECK_WEBHOOK_SECRET")

    if not webhook_secret:
        return {"error": "Webhook integration is not configured."}, 503

    signature = request.headers.get("X-VibeCheck-Signature", "")
    expected_signature = "sha256=" + hmac.new(
        webhook_secret.encode("utf-8"),
        request.get_data(),
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(signature, expected_signature):
        return {"error": "Invalid webhook signature."}, 401

    payload = request.get_json(silent=True)

    if not isinstance(payload, dict):
        return {"error": "Request body must be a JSON object."}, 400

    incoming_reviews = payload.get("reviews")
    if incoming_reviews is None and "review" in payload:
        incoming_reviews = [payload["review"]]

    if not isinstance(incoming_reviews, list) or not incoming_reviews:
        return {"error": "Provide a non-empty 'reviews' list or a 'review' object."}, 400

    if len(incoming_reviews) > 100:
        return {"error": "A maximum of 100 reviews can be sent per request."}, 413

    existing_reviews = load_reviews()
    existing_ids = {
        str(review.get("id"))
        for review in existing_reviews
        if review.get("id") is not None
    }

    accepted = []
    rejected = []

    for index, review in enumerate(incoming_reviews):
        result = validate_review(review, existing_ids)

        if result["valid"]:
            accepted.append(review)
            existing_ids.add(review["id"].strip())
        else:
            rejected.append({
                "index": index,
                "id": review.get("id") if isinstance(review, dict) else None,
                "errors": result["errors"],
            })

    saved = add_reviews(accepted) if accepted else {
        "added": 0,
        "total_reviews": len(existing_reviews),
    }

    return {
        "status": "received",
        "accepted": saved["added"],
        "rejected": rejected,
        "total_reviews": saved["total_reviews"],
        "message": "Reviews received. Run AI analysis to include them in sentiment monitoring.",
    }, 202


# --------------------------------------------------
# Live dashboard data
# --------------------------------------------------

@app.route("/api/monitoring/dashboard")
def monitoring_dashboard_data():
    reviews = load_reviews()
    analyses = load_analyses()
    report = build_intelligence_report(reviews, analyses)
    command_centre = build_command_centre_data(reviews, analyses, report)

    monitoring_html = render_template(
        "_monitoring_panels.html",
        report=report,
        command_centre=command_centre,
    )

    return {
        "total_reviews": len(reviews),
        "total_analyses": len(analyses),
        "unanalyzed_reviews": report.get("unanalyzed_reviews", 0),
        "festival_count": len(get_festival_names(reviews)),
        "monitoring_html": monitoring_html,
    }


@app.route("/health")
def health_check():
    return {
        "status": "healthy",
        "application": "VibeCheck AI - Festival Feedback Detective",
    }


# --------------------------------------------------
# Run Flask Application
# --------------------------------------------------

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False,
    )
