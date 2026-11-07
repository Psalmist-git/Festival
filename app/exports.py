import csv
import json
from pathlib import Path


EXPORT_FOLDER = Path("data/exports")


def flatten_report(data, parent_key=""):
    """
    Convert a nested report dictionary into rows
    that can be written to a CSV file.
    """

    rows = []

    for key, value in data.items():
        full_key = f"{parent_key}.{key}" if parent_key else key

        if isinstance(value, dict):
            rows.extend(flatten_report(value, full_key))

        elif isinstance(value, list):
            if all(not isinstance(item, (dict, list)) for item in value):
                rows.append({
                    "Metric": full_key,
                    "Value": ", ".join(str(item) for item in value),
                })
            else:
                rows.append({
                    "Metric": full_key,
                    "Value": json.dumps(value, ensure_ascii=False),
                })

        else:
            rows.append({
                "Metric": full_key,
                "Value": value,
            })

    return rows


def export_report(report, filename, export_format):
    """
    Export a festival report as JSON or CSV.

    Returns the path to the exported file.
    """

    if not isinstance(report, dict):
        raise ValueError("The report must be a dictionary.")

    if not report:
        raise ValueError("There is no report data to export.")

    export_format = export_format.strip().lower()

    if export_format not in ("json", "csv"):
        raise ValueError("Choose either JSON or CSV.")

    filename = Path(filename).stem

    if not filename:
        raise ValueError("Please provide a valid filename.")

    EXPORT_FOLDER.mkdir(parents=True, exist_ok=True)

    file_path = EXPORT_FOLDER / f"{filename}.{export_format}"

    if export_format == "json":
        with file_path.open("w", encoding="utf-8") as file:
            json.dump(
                report,
                file,
                indent=4,
                ensure_ascii=False,
                default=str,
            )

    else:
        rows = flatten_report(report)

        with file_path.open(
            "w",
            newline="",
            encoding="utf-8",
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=["Metric", "Value"],
            )

            writer.writeheader()
            writer.writerows(rows)

    return file_path