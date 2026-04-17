import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
COMPANY = "manheim"


def main() -> None:
    args = [sys.executable, "scripts/build_reviews_company.py", "--company", COMPANY, *sys.argv[1:]]
    subprocess.run(args, check=True, cwd=BASE_DIR)


if __name__ == "__main__":
    main()
