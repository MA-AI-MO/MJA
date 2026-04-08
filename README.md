# Copart / IAA External Review Analysis Tool

Interactive review/problem explorer for Copart and IAA with Tier 1 / Tier 2 / Tier 3 drill-down, date filters, website filters, top topics, and CSV export.

## Included In This Package

- App files: `index.html`, `app.js`, `styles.css`
- Data files: `data/reviews.json`, `data/reviews.csv`, `data/reviews-data.js`, `data/tiers-data.js`
- Build scripts: `scripts/`
- One-click launcher: `RUN_APP.bat`
- Optional rebuild script: `REBUILD_DATA.bat`

## Build Verification

When you receive a shared package, verify it is the latest by checking:

- App title in browser switches between:
  - `Copart External Review Analysis Tool`
  - `IAA External Review Analysis Tool`
- Header has a website switcher with Copart and IAA logos
- Header color includes `#2661D9`
- Bottom section label is `Collected Sources` as a dropdown
- Filter dropdowns support multi-select toggles and `Select all ...`

## Easiest Way To Run (Recommended)

1. Double-click `RUN_APP.bat`
2. Browser opens automatically at `http://localhost:8080/index.html`
3. Keep the server window open while using the app

## Filter Behavior

- Website, Year, and Month are dropdown filters with multi-select support.
- Use `Select all ...` in each dropdown to select all values.
- Selecting an already-selected value toggles it off.

## Manual Run

```powershell
python -m http.server 8080
```

Then open `http://localhost:8080/index.html`

## Rebuild Data (Optional)

Use `REBUILD_DATA.bat` or run manually:

```powershell
python -m pip install -r requirements.txt
python scripts/refresh_review_data.py --until 2026-03-31
```

Without `--until`, the refresh script automatically builds through the last day of the previous month.

## GitHub Pages

The live site is published from the repository root with GitHub Pages:

- [https://abdullah9498.github.io/MJA/](https://abdullah9498.github.io/MJA/)

## Monthly Automation

The repository includes a GitHub Actions workflow at `.github/workflows/monthly-review-refresh.yml`.

- Scheduled run: monthly on the 2nd day of the month
- Manual run: GitHub repo `Actions` > `Monthly review data refresh` > `Run workflow`
- Default behavior: refreshes data through the last completed month, commits the updated `data/` files back to `main`, and deploys the site to GitHub Pages in the same workflow

## Share With Someone Else

1. Send the entire folder or the generated zip package.
2. Recipient unzips.
3. Recipient double-clicks `RUN_APP.bat`.

That is all they need if Python 3 is already installed.
