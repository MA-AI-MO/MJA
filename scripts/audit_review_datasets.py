import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
BUSINESSES_PATH = DATA_DIR / "businesses.json"


def main() -> None:
    config = json.loads(BUSINESSES_PATH.read_text(encoding="utf-8"))
    business_order = config.get("business_order") or list(config["businesses"].keys())

    windows = {}
    for key in business_order:
        business = config["businesses"][key]
        path = DATA_DIR / business["output_json"]
        if not path.exists():
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
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


if __name__ == "__main__":
    main()
