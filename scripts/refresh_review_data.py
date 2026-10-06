import argparse
import json
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
BUSINESSES_PATH = BASE_DIR / "data" / "businesses.json"
COVERAGE_NOTE_PATH = BASE_DIR / "data" / "coverage-note.json"
MIN_RETAIN_RATIO = 0.90
BUILDERS = {
    "copart": "scripts/build_reviews.py",
    "iaa": "scripts/build_reviews_iaa.py",
    "manheim": "scripts/build_reviews_manheim.py",
    "adesa": "scripts/build_reviews_adesa.py",
    "openlane": "scripts/build_reviews_openlane.py",
    "acv": "scripts/build_reviews_acv.py",
    "americas_auto_auction": "scripts/build_reviews_americas_auto_auction.py",
}


def default_until_date() -> str:
    first_of_month = date.today().replace(day=1)
    last_completed_day = first_of_month - timedelta(days=1)
    return last_completed_day.isoformat()


def run_step(args: list[str]) -> None:
    print("Running:", " ".join(args))
    subprocess.run(args, check=True, cwd=BASE_DIR)


def audit_dataset(relative_path: str, label: str) -> None:
    payload = json.loads((BASE_DIR / relative_path).read_text(encoding="utf-8"))
    meta = payload.get("meta", {})
    source_counts = meta.get("source_counts") or {}
    source_audit = meta.get("source_audit") or []
    required_sources = meta.get("required_source_websites") or []
    collector_failures = meta.get("collector_failures") or []

    fatal_collector_failures = [
        row for row in collector_failures
        if not row.get("retained_previous_data")
    ]
    if fatal_collector_failures:
        raise RuntimeError(f"{label}: collector failures present: {fatal_collector_failures}")

    missing_required = [source for source in required_sources if int(source_counts.get(source, 0)) <= 0]
    if missing_required:
        raise RuntimeError(f"{label}: required sources missing after refresh: {missing_required}")

    unhealthy_required = []
    for row in source_audit:
        source = row.get("source_website")
        status = row.get("status")
        if source in required_sources and status in {"blocked", "missing", "not_attempted"}:
            unhealthy_required.append({"source": source, "status": status, "notes": row.get("notes", [])})
    if unhealthy_required:
        raise RuntimeError(f"{label}: required sources unhealthy after refresh: {unhealthy_required}")

    present_sources = [row["source_website"] for row in source_audit if int(row.get("review_count", 0)) > 0]
    zero_count_sources = [row["source_website"] for row in source_audit if int(row.get("review_count", 0)) <= 0]
    partial_sources = [
        {
            "source": row.get("source_website"),
            "status": row.get("status"),
            "latest_candidate_date": row.get("latest_candidate_date"),
            "latest_review_date": row.get("latest_review_date"),
            "notes": row.get("notes", []),
        }
        for row in source_audit
        if row.get("status") in {
            "partial",
            "stale_or_no_recent_candidates",
            "parsed_no_new_rows",
            "retained_after_failed_refresh",
            "partial_profile_retention",
        }
    ]

    print(f"{label} source audit present: {present_sources}")
    if zero_count_sources:
        print(f"{label} source audit zero-count: {zero_count_sources}")
    if partial_sources:
        print(f"{label} source audit warnings: {partial_sources}")


def load_baseline_outputs(config_payload: dict) -> dict[str, dict[str, bytes]]:
    baselines: dict[str, dict[str, bytes]] = {}
    for business_key, business in config_payload["businesses"].items():
        outputs: dict[str, bytes] = {}
        for rel in [f"data/{business['output_json']}", f"data/{business['output_csv']}"]:
            path = BASE_DIR / rel
            if path.exists():
                outputs[rel] = path.read_bytes()
        baselines[business_key] = outputs
    return baselines


def restore_baseline_outputs(baselines: dict[str, dict[str, bytes]]) -> None:
    for outputs in baselines.values():
        for rel, content in outputs.items():
            (BASE_DIR / rel).write_bytes(content)


def review_count_for(relative_path: str) -> int:
    payload = json.loads((BASE_DIR / relative_path).read_text(encoding="utf-8"))
    return int((payload.get("meta") or {}).get("review_count") or 0)


def write_coverage_note(config_payload: dict, since: str, until: str) -> None:
    refreshed = []
    business_order = config_payload.get("business_order") or list(config_payload["businesses"].keys())
    for business_key in business_order:
        business = config_payload["businesses"][business_key]
        payload = json.loads((BASE_DIR / "data" / business["output_json"]).read_text(encoding="utf-8"))
        meta = payload.get("meta") or {}
        refreshed.append(
            {
                "key": business_key,
                "display_name": business["display_name"],
                "since_date": meta.get("since_date"),
                "until_date": meta.get("until_date"),
                "review_count": int(meta.get("review_count") or 0),
                "source_counts": meta.get("source_counts") or {},
                "source_audit": meta.get("source_audit") or [],
            }
        )

    coverage_note = {
        "generated_at": date.today().isoformat(),
        "target_since": since,
        "target_until": until,
        "refreshed": refreshed,
        "stale": [],
    }
    COVERAGE_NOTE_PATH.write_text(json.dumps(coverage_note, indent=2), encoding="utf-8")
    print(f"Wrote {COVERAGE_NOTE_PATH}")


def is_context_enriched_reddit_comment(source_website: str, review_text: str = "") -> bool:
    if str(source_website or "").strip().lower() != "reddit.com":
        return False
    text = str(review_text or "")
    return "Thread context:" in text


def is_intentionally_excluded_review(row: dict) -> bool:
    source_website = str(row.get("source_website") or "").strip().lower()
    if source_website == "pissedconsumer.com":
        return True
    return is_context_enriched_reddit_comment(
        source_website,
        row.get("review_text"),
    )


def allowed_baseline_review_count(relative_path: str) -> int:
    payload = json.loads((BASE_DIR / relative_path).read_text(encoding="utf-8"))
    reviews = payload.get("reviews") or []
    return sum(1 for row in reviews if not is_intentionally_excluded_review(row))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Refresh review data for all configured businesses through the last completed month."
    )
    parser.add_argument("--since", default="2023-01-01", help="Include reviews on/after this date (YYYY-MM-DD)")
    parser.add_argument(
        "--until",
        default=None,
        help="Include reviews on/before this date (YYYY-MM-DD). Defaults to the last day of the previous month.",
    )
    parser.add_argument("--target", type=int, default=0, help="Minimum number of reviews to collect")
    parser.add_argument("--max-output", type=int, default=120000, help="Maximum number of rows to keep in output")
    parser.add_argument(
        "--reddit-time-budget",
        type=int,
        default=900,
        help="Maximum seconds to spend in each Reddit collector per business.",
    )
    parser.add_argument(
        "--allow-count-regression",
        action="store_true",
        help="Allow a business review count to fall below the previous approved dataset count.",
    )
    args = parser.parse_args()

    config_payload = json.loads(BUSINESSES_PATH.read_text(encoding="utf-8"))
    business_order = config_payload.get("business_order") or list(config_payload["businesses"].keys())
    baselines = load_baseline_outputs(config_payload)
    baseline_counts = {
        business_key: allowed_baseline_review_count(f"data/{config_payload['businesses'][business_key]['output_json']}")
        for business_key in business_order
        if (BASE_DIR / f"data/{config_payload['businesses'][business_key]['output_json']}").exists()
    }

    until = args.until or default_until_date()
    common_args = [
        "--since",
        args.since,
        "--until",
        until,
        "--target",
        str(args.target),
        "--max-output",
        str(args.max_output),
        "--reddit-time-budget",
        str(args.reddit_time_budget),
    ]

    print(f"Refreshing datasets through {until}")
    try:
        for business_key in business_order:
            builder = BUILDERS.get(business_key)
            if not builder:
                raise RuntimeError(f"No build pipeline registered for {business_key}")
            run_step([sys.executable, builder, *common_args])

        run_step([sys.executable, "scripts/build_js_data.py"])
        run_step([sys.executable, "scripts/audit_review_datasets.py"])

        for business_key in business_order:
            business = config_payload["businesses"][business_key]
            relative_json = f"data/{business['output_json']}"
            audit_dataset(relative_json, business["display_name"])

            baseline_count = baseline_counts.get(business_key, 0)
            current_count = review_count_for(relative_json)
            threshold = int(baseline_count * MIN_RETAIN_RATIO)
            if (
                baseline_count > 0
                and current_count < threshold
                and not args.allow_count_regression
            ):
                raise RuntimeError(
                    f"{business['display_name']}: refreshed count {current_count} dropped below safe threshold "
                    f"{threshold} from baseline {baseline_count}"
                )

        write_coverage_note(config_payload, args.since, until)
        run_step([sys.executable, "scripts/build_js_data.py"])

        print("Data refresh complete.")
    except Exception:
        restore_baseline_outputs(baselines)
        run_step([sys.executable, "scripts/build_js_data.py"])
        raise


if __name__ == "__main__":
    main()
