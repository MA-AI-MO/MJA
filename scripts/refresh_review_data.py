import argparse
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]


def default_until_date() -> str:
    first_of_month = date.today().replace(day=1)
    last_completed_day = first_of_month - timedelta(days=1)
    return last_completed_day.isoformat()


def run_step(args: list[str]) -> None:
    print("Running:", " ".join(args))
    subprocess.run(args, check=True, cwd=BASE_DIR)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Refresh Copart and IAA review data through the last completed month."
    )
    parser.add_argument("--since", default="2023-01-01", help="Include reviews on/after this date (YYYY-MM-DD)")
    parser.add_argument(
        "--until",
        default=None,
        help="Include reviews on/before this date (YYYY-MM-DD). Defaults to the last day of the previous month.",
    )
    parser.add_argument("--target", type=int, default=0, help="Minimum number of reviews to collect")
    parser.add_argument("--max-output", type=int, default=120000, help="Maximum number of rows to keep in output")
    args = parser.parse_args()

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
    ]

    print(f"Refreshing datasets through {until}")
    run_step([sys.executable, "scripts/build_reviews.py", *common_args])
    run_step([sys.executable, "scripts/build_reviews_iaa.py", *common_args])
    run_step([sys.executable, "scripts/build_js_data.py"])
    print("Data refresh complete.")


if __name__ == "__main__":
    main()
