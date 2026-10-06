import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
BUSINESSES_PATH = DATA_DIR / "businesses.json"
COVERAGE_NOTE_PATH = DATA_DIR / "coverage-note.json"


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def dataset_summary(business: dict) -> dict:
    payload = load_json(DATA_DIR / business["output_json"])
    meta = payload.get("meta") or {}
    return {
        "until_date": meta.get("until_date"),
        "since_date": meta.get("since_date"),
        "review_count": int(meta.get("review_count") or 0),
        "source_counts": meta.get("source_counts") or {},
        "source_audit": meta.get("source_audit") or [],
    }


def find_statuses(artifacts_dir: Path) -> dict[str, tuple[Path, dict]]:
    statuses: dict[str, tuple[Path, dict]] = {}
    for status_path in artifacts_dir.rglob("status.json"):
        status = load_json(status_path)
        company = str(status.get("company") or "").strip()
        if company:
            statuses[company] = (status_path.parent, status)
    return statuses


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge successful per-company refresh artifacts.")
    parser.add_argument("--artifacts-dir", required=True, help="Downloaded artifact directory.")
    parser.add_argument("--since", required=True, help="Target refresh start date.")
    parser.add_argument("--until", required=True, help="Target refresh end date.")
    args = parser.parse_args()

    artifacts_dir = Path(args.artifacts_dir)
    config = load_json(BUSINESSES_PATH)
    business_order = config.get("business_order") or list(config["businesses"].keys())
    statuses = find_statuses(artifacts_dir)

    refreshed = []
    stale = []
    successful_count = 0

    for key in business_order:
        business = config["businesses"][key]
        label = business["display_name"]
        artifact_dir, status = statuses.get(key, (None, {}))
        success = bool(status.get("success"))

        if success and artifact_dir:
            json_src = artifact_dir / business["output_json"]
            csv_src = artifact_dir / business["output_csv"]
            if json_src.exists() and csv_src.exists():
                shutil.copy2(json_src, DATA_DIR / business["output_json"])
                shutil.copy2(csv_src, DATA_DIR / business["output_csv"])
                summary = dataset_summary(business)
                refreshed.append({"key": key, "display_name": label, **summary})
                successful_count += 1
                print(f"Merged {label}: {summary['review_count']} reviews through {summary['until_date']}")
                continue

        summary = dataset_summary(business)
        reason = "refresh failed"
        if not status:
            reason = "no artifact produced"
        elif status.get("missing_output"):
            reason = f"missing {status['missing_output']}"
        stale.append({"key": key, "display_name": label, "reason": reason, **summary})
        print(f"Kept existing {label}: {summary['review_count']} reviews through {summary['until_date']} ({reason})")

    if successful_count <= 0:
        raise SystemExit("No company refresh artifacts succeeded; refusing to deploy unchanged monthly data.")

    coverage_note = {
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "target_since": args.since,
        "target_until": args.until,
        "refreshed": refreshed,
        "stale": stale,
    }
    COVERAGE_NOTE_PATH.write_text(json.dumps(coverage_note, indent=2), encoding="utf-8")
    print(f"Wrote {COVERAGE_NOTE_PATH}")


if __name__ == "__main__":
    main()
