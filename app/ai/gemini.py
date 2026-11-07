import json
import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

MAX_ATTEMPTS = 2
RETRY_DELAY = 3


class GeminiConfigurationError(Exception):
    """Raised when Gemini configuration is missing or invalid."""
    pass


class GeminiAnalysisError(Exception):
    """Raised when Gemini cannot analyse a review."""
    pass


def get_gemini_client():
    """Create a Gemini client with a request timeout."""

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise GeminiConfigurationError(
            "GEMINI_API_KEY is missing. Check your .env file."
        )

    return genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(
            timeout=30000,
            retry_options=types.HttpRetryOptions(attempts=1),
        ),
    )


def analyze_review(review):
    """Analyse one festival review using Gemini."""

    if not isinstance(review, dict):
        raise ValueError("Review must be a dictionary.")

    review_text = review.get("text", "").strip()
    event_name = review.get("event", "").strip()

    if not review_text:
        raise ValueError("Review text cannot be empty.")

    if not event_name:
        raise ValueError("Event name cannot be empty.")

    prompt = f"""
You are VibeCheck AI, an expert festival feedback analyst.

Analyse this festival review.

Festival: {event_name}

Customer Review:
{review_text}

Return valid JSON using this structure:

{{
    "sentiment": "positive, negative, or neutral",
    "emotions": ["emotion 1"],
    "topics": ["topic 1"],
    "complaint_detected": true,
    "complaint_summary": "Brief complaint description",
    "recommendation": "Practical recommendation",
    "summary": "Brief customer experience summary"
}}

Rules:
- Sentiment must be positive, negative, or neutral.
- Only identify emotions supported by the review.
- Do not invent information.
- complaint_detected must be a boolean.
- Use an empty complaint_summary if no complaint exists.
- Return JSON only.
"""

    client = None

    try:
        client = get_gemini_client()

        response = None

        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                response = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.2,
                        max_output_tokens=500,
                        response_mime_type="application/json",
                    ),
                )

                break

            except Exception as error:
                error_message = str(error)

                temporary_overload = any(
                    error_code in error_message.upper()
                    for error_code in (
                        "503",
                        "504",
                        "500",
                        "502",
                        "UNAVAILABLE",
                        "DEADLINE_EXCEEDED",
                        "INTERNAL",
                    )
                )

                if temporary_overload and attempt < MAX_ATTEMPTS:
                    print(
                        "\nGemini is temporarily busy. "
                        "Retrying in 3 seconds..."
                    )
                    time.sleep(RETRY_DELAY)
                    continue

                if temporary_overload:
                    raise GeminiAnalysisError(
                        "Gemini is experiencing high demand. "
                        "Please try again shortly."
                    ) from error

                raise GeminiAnalysisError(
                    f"Gemini request failed: {error}"
                ) from error

        if response is None or not response.text:
            raise GeminiAnalysisError(
                "Gemini returned an empty response."
            )

        analysis = json.loads(response.text)

        required_fields = {
            "sentiment",
            "emotions",
            "topics",
            "complaint_detected",
            "complaint_summary",
            "recommendation",
            "summary",
        }

        if not isinstance(analysis, dict):
            raise GeminiAnalysisError(
                "Gemini returned an invalid response structure."
            )

        if not required_fields.issubset(analysis):
            raise GeminiAnalysisError(
                "Gemini response is missing required fields."
            )

        if analysis["sentiment"] not in {
            "positive", "negative", "neutral"
        }:
            raise GeminiAnalysisError(
                "Gemini returned an invalid sentiment."
            )

        if not isinstance(analysis["emotions"], list):
            raise GeminiAnalysisError("Invalid emotions format.")

        if not isinstance(analysis["topics"], list):
            raise GeminiAnalysisError("Invalid topics format.")

        if not isinstance(analysis["complaint_detected"], bool):
            raise GeminiAnalysisError(
                "Invalid complaint detection result."
            )

        return analysis

    except (GeminiConfigurationError, GeminiAnalysisError):
        raise

    except json.JSONDecodeError as error:
        raise GeminiAnalysisError(
            "Gemini returned invalid JSON."
        ) from error

    finally:
        if client is not None:
            client.close()