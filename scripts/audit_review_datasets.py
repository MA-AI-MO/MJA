import argparse
import json
from collections import defaultdict
from datetime import date
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
BUSINESSES_PATH = DATA_DIR / "businesses.json"
SENTIMENTS = ("negative", "positive")


def validate_google_business(label: str, business: dict, payload: dict) -> list[str]:
    if not business.get("google_business_search_names"):
        return []

    meta = payload.get("meta") or {}
    reviews = [
        row for row in payload.get("reviews") or []
        if str(row.get("source_website") or "").strip().lower() == "google.com"
    ]
    registry = meta.get("google_business_profiles") or []
    audit = next((
        row for row in meta.get("source_audit") or []
        if str(row.get("source_website") or "").strip().lower() == "google.com"
    ), {})
    excluded_terms = {
        str(term).strip().lower()
        for term in business.get("google_business_name_exclude_terms") or []
        if str(term).strip()
    }
    errors = []
    if not reviews:
        errors.append(f"{label}: Google Business Profile source has no accepted reviews")
    if not registry:
        errors.append(f"{label}: Google Business Profile registry is empty")
    audit_status = audit.get("status")
    if audit_status not in {
        "ok",
        "retained_after_failed_refresh",
        "partial_profile_retention",
    }:
        errors.append(f"{label}: Google Business Profile source audit status is {audit.get('status') or 'missing'}")
    if audit_status == "ok" and int(audit.get("candidate_reviews_seen") or 0) <= 0:
        errors.append(f"{label}: Google Business Profile source audit has no candidate count")
    if audit_status == "retained_after_failed_refresh":
        if int(audit.get("review_count") or 0) < int(audit.get("existing_review_count") or 0):
            errors.append(f"{label}: retained Google rows dropped below the existing verified count")
        if not audit.get("errors"):
            errors.append(f"{label}: retained Google status has no recorded refresh error")
        if not audit.get("last_successful_refresh_until"):
            errors.append(f"{label}: retained Google status has no last successful refresh checkpoint")
    if audit_status == "partial_profile_retention":
        if int(audit.get("review_count") or 0) < int(audit.get("existing_review_count") or 0):
            errors.append(f"{label}: profile-level Google refresh dropped existing verified rows")
        if int(audit.get("profiles_completed") or 0) <= 0:
            errors.append(f"{label}: profile-level Google refresh completed no profiles")
        if (
            int(audit.get("profiles_failed") or 0) <= 0
            and int(audit.get("profiles_skipped_after_circuit_breaker") or 0) <= 0
        ):
            errors.append(f"{label}: profile-level Google retention has no failed or skipped profiles")
        if not audit.get("errors"):
            errors.append(f"{label}: profile-level Google retention has no recorded refresh error")

    seen_content = set()
    for row in reviews:
        source_label = str(row.get("source_label") or "")
        source_url = str(row.get("source_url") or "")
        if not source_label.startswith("Google Business Profile ("):
            errors.append(f"{label}: malformed Google source label on {row.get('id')}")
        if excluded_terms and any(term in source_label.lower() for term in excluded_terms):
            errors.append(f"{label}: excluded Google business name admitted on {row.get('id')}")
        if "google.com/maps/" not in source_url:
            errors.append(f"{label}: malformed Google review URL on {row.get('id')}")
        if row.get("geo_validation") != "google_business_us_profile":
            errors.append(f"{label}: Google row lacks U.S. profile validation on {row.get('id')}")
        content_key = (
            str(row.get("author") or "").strip().lower(),
            " ".join(str(row.get("review_text") or "").lower().split()),
        )
        if content_key in seen_content:
            errors.append(f"{label}: duplicate Google author/text content on {row.get('id')}")
        seen_content.add(content_key)

    return errors


def list_month_keys(since_date: str, until_date: str) -> list[str]:
    if not since_date or not until_date:
        return []
    current = date.fromisoformat(f"{since_date[:7]}-01")
    end = date.fromisoformat(f"{until_date[:7]}-01")
    keys: list[str] = []
    while current <= end:
        keys.append(current.strftime("%Y-%m"))
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1)
        else:
            current = current.replace(month=current.month + 1)
    return keys


def month_label(month_key: str) -> str:
    year, month = month_key.split("-")
    month_names = {
        "01": "Jan",
        "02": "Feb",
        "03": "Mar",
        "04": "Apr",
        "05": "May",
        "06": "Jun",
        "07": "Jul",
        "08": "Aug",
        "09": "Sep",
        "10": "Oct",
        "11": "Nov",
        "12": "Dec",
    }
    return f"{month_names.get(month, month)} {year}"


def summarize_business(label: str, payload: dict) -> None:
    meta = payload.get("meta") or {}
    reviews = payload.get("reviews") or []
    since_date = meta.get("since_date")
    until_date = meta.get("until_date")
    months = list_month_keys(since_date, until_date)
    sources = sorted({str(row.get("source_website") or "").strip() for row in reviews if row.get("source_website")})
    source_audit = meta.get("source_audit") or []

    company_month_counts = {
        sentiment: {month_key: 0 for month_key in months}
        for sentiment in SENTIMENTS
    }
    source_month_counts = defaultdict(int)

    for row in reviews:
        sentiment = str(row.get("sentiment") or "").strip().lower()
        review_date = str(row.get("review_date") or "").strip()
        source = str(row.get("source_website") or "").strip()
        if sentiment not in SENTIMENTS or len(review_date) < 7 or not source:
            continue
        month_key = review_date[:7]
        if month_key not in company_month_counts[sentiment]:
            continue
        company_month_counts[sentiment][month_key] += 1
        source_month_counts[(source, sentiment, month_key)] += 1

    print(f"{label}: since={since_date} until={until_date} reviews={len(reviews)} sources={len(sources)}")

    if source_audit:
        print("  - source health:")
        for row in source_audit:
            source = row.get("source_website")
            status = row.get("status", "unknown")
            review_count = int(row.get("review_count") or 0)
            new_count = int(row.get("new_reviews_added") or 0)
            latest_review = row.get("latest_review_date") or "n/a"
            latest_candidate = row.get("latest_candidate_date") or "n/a"
            fallback = " fallback" if row.get("fallback_used") else ""
            print(
                f"    * {source}: status={status}{fallback} reviews={review_count} "
                f"new={new_count} latest_review={latest_review} latest_candidate={latest_candidate}"
            )

    for sentiment in SENTIMENTS:
        gap_months = [month_key for month_key in months if company_month_counts[sentiment][month_key] <= 0]
        if gap_months:
            gap_text = ", ".join(month_label(month_key) for month_key in gap_months)
            print(f"  - {sentiment} company-level zero months: {gap_text}")
        else:
            print(f"  - {sentiment} company-level zero months: none")

    gap_rows = []
    years = sorted({month_key[:4] for month_key in months}, reverse=True)
    for source in sources:
        for sentiment in SENTIMENTS:
            for year in years:
                year_months = [month_key for month_key in months if month_key.startswith(f"{year}-")]
                if not year_months:
                    continue
                counts = [source_month_counts[(source, sentiment, month_key)] for month_key in year_months]
                total = sum(counts)
                if total <= 0:
                    continue
                missing = [month_key for month_key, count in zip(year_months, counts) if count <= 0]
                if missing:
                    gap_rows.append((source, sentiment, year, missing, total))

    if gap_rows:
        print("  - source/year/month gaps:")
        for source, sentiment, year, missing, total in gap_rows:
            gap_text = ", ".join(month_label(month_key) for month_key in missing)
            print(f"    * {source} | {sentiment} | {year} | total={total} | missing={gap_text}")
    else:
        print("  - source/year/month gaps: none")


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit review dataset coverage by company, source, year, and month.")
    parser.add_argument(
        "--warn-only",
        action="store_true",
        help="Print inconsistent date windows as a warning instead of failing.",
    )
    args = parser.parse_args()

    config = json.loads(BUSINESSES_PATH.read_text(encoding="utf-8"))
    business_order = config.get("business_order") or list(config["businesses"].keys())

    windows = {}
    payloads = {}
    google_errors = []
    for key in business_order:
        business = config["businesses"][key]
        path = DATA_DIR / business["output_json"]
        if not path.exists():
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        payloads[business["display_name"]] = payload
        google_errors.extend(validate_google_business(business["display_name"], business, payload))
        meta = payload.get("meta") or {}
        review_count = int(meta.get("review_count") or 0)
        if review_count <= 0:
            continue
        windows[business["display_name"]] = {
            "since": meta.get("since_date"),
            "until": meta.get("until_date"),
            "review_count": review_count,
        }

    unique_windows = {
        (row["since"], row["until"])
        for row in windows.values()
        if row["since"] and row["until"]
    }

    if len(unique_windows) > 1:
        details = "\n".join(
            f"- {name}: since={row['since']} until={row['until']} reviews={row['review_count']}"
            for name, row in windows.items()
        )
        message = f"Inconsistent dataset date windows detected:\n{details}"
        if args.warn_only:
            print(f"WARNING: {message}")
        else:
            raise SystemExit(message)
    else:
        print("Dataset windows are consistent.")

    if google_errors:
        raise SystemExit("Google Business Profile audit failed:\n" + "\n".join(f"- {error}" for error in google_errors))
    print("Google Business Profile source checks passed for all configured companies.")

    for name, row in windows.items():
        print(f"- {name}: since={row['since']} until={row['until']} reviews={row['review_count']}")

    print("\nCoverage summary")
    for name in [config["businesses"][key]["display_name"] for key in business_order]:
        payload = payloads.get(name)
        if not payload:
            continue
        summarize_business(name, payload)


if __name__ == "__main__":
    main()
