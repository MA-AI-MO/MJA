import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
BUSINESSES_PATH = DATA_DIR / "businesses.json"
TIERS_PATH = DATA_DIR / "tier-hierarchy.json"
APP_CONFIG_JS = DATA_DIR / "app-config.js"
REVIEW_DATASETS_JS = DATA_DIR / "reviews-data-all.js"


def empty_payload():
    return {
        "meta": {
            "description": "Dataset not built yet.",
            "review_count": 0,
            "source_counts": {},
            "source_audit": [],
            "sentiments": {"positive": 0, "negative": 0},
            "source_urls": []
        },
        "reviews": []
    }


def main() -> None:
    config_payload = json.loads(BUSINESSES_PATH.read_text(encoding="utf-8"))
    tiers_payload = json.loads(TIERS_PATH.read_text(encoding="utf-8"))

    business_order = config_payload.get("business_order") or list(config_payload["businesses"].keys())
    public_businesses = {}
    datasets = {}

    for key in business_order:
      business = config_payload["businesses"][key]
      public_businesses[key] = {
          "display_name": business["display_name"],
          "switch_label": business.get("switch_label", business["display_name"]),
          "title": business["title"],
          "logo_src": business["logo_src"],
          "logo_alt": business["logo_alt"],
          "csv_prefix": business["csv_prefix"],
          "theme": business.get("theme", {}),
          "output_json": business["output_json"]
      }

      data_path = DATA_DIR / business["output_json"]
      if data_path.exists():
          datasets[key] = json.loads(data_path.read_text(encoding="utf-8"))
      else:
          datasets[key] = empty_payload()

    APP_CONFIG_JS.write_text(
        "window.REVIEW_APP_CONFIG = "
        + json.dumps(
            {
                "businessOrder": business_order,
                "businesses": public_businesses,
                "tierHierarchy": tiers_payload,
            },
            ensure_ascii=False,
            indent=2,
        )
        + ";\n",
        encoding="utf-8",
    )

    REVIEW_DATASETS_JS.write_text(
        "window.REVIEW_DATASETS = " + json.dumps(datasets, ensure_ascii=False, indent=2) + ";\n",
        encoding="utf-8",
    )

    print(f"Wrote {APP_CONFIG_JS}")
    print(f"Wrote {REVIEW_DATASETS_JS}")


if __name__ == "__main__":
    main()
