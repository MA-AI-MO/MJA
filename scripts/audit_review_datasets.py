import json
from collections import defaultdict
from datetime import date
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
BUSINESSES_PATH = DATA_DIR / "businesses.json"
SENTIMENTS = ("negative", "positive")


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
    config = json.loads(BUSINESSES_PATH.read_text(encoding="utf-8"))
    business_order = config.get("business_order") or list(config["businesses"].keys())

    windows = {}
    payloads = {}
    for key in business_order:
        business = config["businesses"][key]
        path = DATA_DIR / business["output_json"]
        if not path.exists():
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        payloads[business["display_name"]] = payload
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
        raise SystemExit(f"Inconsistent dataset date windows detected:\n{details}")

    print("Dataset windows are consistent.")
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
