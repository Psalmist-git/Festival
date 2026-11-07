# ASAKE — VibeCheck AI
## Festival Feedback Detective

ASAKE (VibeCheck AI) is a Python command-line application that helps festival organisers understand audience feedback using AI-powered review analysis and structured data analytics.

The application imports festival reviews from CSV files, validates and stores review data, analyses individual reviews using Google Gemini, identifies recurring complaints, compares festivals, and generates reports to support evidence-based event management decisions.

---

## Project Objectives

Festival organisers receive feedback through different channels, but identifying recurring problems and understanding audience satisfaction can be difficult.

ASAKE addresses this problem by helping organisers:

- Understand audience sentiment.
- Identify emotions and recurring discussion topics.
- Detect complaints and classify complaint categories.
- Identify areas requiring management attention.
- Compare feedback across different festivals.
- Ask questions about collected festival feedback.
- Export festival intelligence reports.
- Evaluate AI performance against manually labelled examples.

## Features

### 1. Festival Review Import
- Import reviews from CSV files.
- Validate required fields and review formats.
- Reject invalid records with explanations.
- Detect duplicate review IDs.
- Store accepted reviews in JSON.

### 2. Review Management
- List imported festival reviews.
- View import statistics.
- Maintain review records locally.

### 3. Gemini-Powered Review Analysis
Analyse individual reviews using Google Gemini.

The analysis produces:
- Sentiment: positive, negative, or neutral.
- Emotions.
- Topics.
- Complaint detection.
- Complaint summary.
- Recommendation.
- Review summary.

### 4. Festival Intelligence Reports
Generate reports containing:
- Total, analysed, and unanalyzed reviews.
- Sentiment distribution and percentages.
- Topic frequency.
- Complaint categories.
- Recurring complaints.
- Priority insights.
- Suggested management actions.
- Recommendations and performance indicators.

### 5. Festival Comparison
Compare two festivals using their available review data and intelligence reports.

### 6. AI-Powered Questions and Answers
Ask questions about imported festival feedback. The AI assistant uses the supplied reviews and saved analyses as evidence.

### 7. Report Export
Export festival intelligence reports in:
- JSON
- CSV

### 8. Engineering Self-Check
Run the built-in engineering self-check to assess understanding of selected project concepts.

### 9. Gold-Standard Evaluation
Evaluate Gemini's predictions against a manually labelled dataset.

The evaluation currently measures:
- Sentiment accuracy.
- Complaint detection accuracy.
- Complaint category accuracy.

---

## Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.12 | Core application |
| Google Gemini | AI review analysis and question answering |
| Google Gen AI SDK | Gemini API integration |
| python-dotenv | Loading environment variables |
| CSV | Review import and gold-standard dataset |
| JSON | Local data persistence |
| unittest | Automated testing |

---

## Project Structure

```text
Festival-VibeCheck/
│
├── main.py
├── README.md
├── requirements.txt
├── .gitignore
├── .env.example
│
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── ingest.py
│   ├── storage.py
│   ├── analysis_storage.py
│   ├── evaluation.py
│   ├── exports.py
│   ├── self_check.py
│   │
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── gemini.py
│   │   └── qa.py
│   │
│   └── analytics/
│       ├── __init__.py
│       ├── insights.py
│       └── comparison.py
│
├── data/
│   ├── synthetic_reviews.csv
│   ├── reviews.json
│   ├── analyses.json
│   ├── gold_standard.csv
│   └── exports/
│
├── docs/
│   └── TECHNICAL_DOCUMENTATION.md
│
└── tests/
    ├── test_injest.py
    ├── test_storage.py
    ├── test_insights.py
    ├── test_comparison.py
    ├── test_exports.py
    └── test_evaluation.py
```

## Installation

### Prerequisites

- Python 3.12 or later.
- Internet connection for Gemini-powered features.
- A Google Gemini API key.

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd Festival-VibeCheck
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
```

### 3. Activate the virtual environment

Linux/macOS:

```bash
source .venv/bin/activate
```

Windows:

```bash
.venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment variables

Create a local `.env` file in the project root.

Add:

```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-3.1-flash-lite
```

Replace the placeholder with your own Gemini API key.

**Important:** Never commit your `.env` file or expose your API key publicly.

### 6. Run the application

```bash
python main.py
```

---

## Running the Tests

Run the automated test suite:

```bash
python -m unittest discover -s tests -v
```

The current development test suite has **61 passing tests**.

These tests cover review ingestion, validation, storage, analytics, festival comparison, report exports, and gold-standard evaluation logic.

The automated evaluation tests use mocked AI responses; they do not replace live Gemini API acceptance testing.

---

## Current Dataset

The current local project data contains:

| Dataset | Current count |
|---|---:|
| Stored festival reviews | 30 |
| Saved Gemini analyses | 10 |
| Gold-standard examples | 12 |

The gold-standard dataset contains manually labelled examples used to compare AI predictions with expected results.

## Current Evaluation Results

The most recent recorded gold-standard evaluation produced:

| Metric | Result |
|---|---:|
| Sentiment accuracy | 83.33% (10/12) |
| Complaint detection accuracy | 100% (12/12) |
| Complaint category accuracy | 100% (6/6) |

Complaint category accuracy is calculated only from the six examples labelled as complaints. These results are based on a relatively small evaluation dataset and should not be treated as proof of perfect real-world performance.

## Important Notes

- Gemini-powered features require a valid API key and internet access.
- AI-generated classifications and recommendations may be inaccurate and should be reviewed before operational decisions are made.
- Review and analysis records are stored locally as JSON files.
- The application is currently designed as a command-line tool.
- The current dataset includes synthetic festival reviews.

## Documentation

For details about the application's internal architecture, data flow, AI integration, analytics, storage, evaluation, and security considerations, see:

`docs/TECHNICAL_DOCUMENTATION.md`

## Project Status

ASAKE — VibeCheck AI is an actively developed Python project focused on applying AI and data analytics to festival feedback management.