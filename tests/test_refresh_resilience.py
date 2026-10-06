import json
import tempfile
import unittest
from collections import Counter
from copy import deepcopy
from pathlib import Path
from unittest import mock

from scripts import audit_review_datasets
from scripts import build_reviews_company
from scripts import merge_refresh_artifacts


def google_row():
    return {
        "id": "rvw-000001",
        "source_website": "google.com",
        "source_label": "Google Business Profile (Test Auction)",
        "source_url": "https://www.google.com/maps/place/Test/data=!1s0x0:0x7b",
        "author": "Test User",
        "review_date": "2026-08-20",
        "rating": 5,
        "sentiment": "positive",
        "review_text": "Staff clearly explained the auction fees and pickup process.",
        "tier1": "Customer Service & Communication",
        "tier2": "Staff Helpfulness and Professionalism",
        "tier3": "Helpful / Professional Staff",
        "geo_validation": "google_business_us_profile",
    }


def google_profile():
    return {
        "feature_id": "0x0:0x7b",
        "cid": "123",
        "place_id": "",
        "name": "Test Auction",
        "address": "Dallas, TX",
        "website": "https://example.com",
        "rating": 4.5,
        "review_count": 100,
    }


def baseline_payload():
    return {
        "meta": {
            "until_date": "2026-08-31",
            "google_business_profiles": [google_profile()],
            "source_audit": [
                {
                    "source_website": "google.com",
                    "status": "ok",
                    "attempted": True,
                    "candidate_reviews_seen": 1,
                    "errors": [],
                }
            ],
        },
        "reviews": [google_row()],
    }


class GoogleRefreshResilienceTests(unittest.TestCase):
    def make_collector(self, replace_google=False):
        temp_dir = tempfile.TemporaryDirectory()
        payload_path = Path(temp_dir.name) / "reviews.json"
        csv_path = Path(temp_dir.name) / "reviews.csv"
        payload_path.write_text(json.dumps(baseline_payload()), encoding="utf-8")
        output_patch = mock.patch.object(build_reviews_company, "OUTPUT_JSON", payload_path)
        csv_patch = mock.patch.object(build_reviews_company, "OUTPUT_CSV", csv_path)
        output_patch.start()
        csv_patch.start()
        self.addCleanup(output_patch.stop)
        self.addCleanup(csv_patch.stop)
        self.addCleanup(temp_dir.cleanup)
        collector = build_reviews_company.Collector(
            target=0,
            since="2023-01-01",
            until="2026-09-30",
            max_output=100,
            replace_source_websites={"google.com"} if replace_google else set(),
        )
        collector._test_output_path = payload_path
        return collector

    def test_failed_google_refresh_rolls_back_partial_state_and_continues(self):
        collector = self.make_collector()
        baseline_records = deepcopy(collector.records)
        baseline_seen = set(collector._seen)
        baseline_profiles = deepcopy(collector.google_business_profiles)

        def failing_google():
            collector.note_source_attempt(
                "google.com",
                pages=3,
                candidates=7,
                error="newest review RPC did not load",
            )
            collector.records.append({**google_row(), "id": "", "author": "Partial User"})
            collector._seen.add("partial-fingerprint")
            collector.google_business_profiles.append(
                {**google_profile(), "cid": "456", "feature_id": "0x0:0x1c8"}
            )
            collector.geo_validation_counts["google_business_us_profile"] += 1
            raise RuntimeError("Google Business Profile coverage incomplete")

        collector.collect_google_business = failing_google
        later_collector_ran = []

        def succeeding_trustpilot():
            later_collector_ran.append(True)

        collector.collect_trustpilot = succeeding_trustpilot
        with mock.patch.multiple(
            build_reviews_company,
            GOOGLE_PLAY_APPS=[],
            TRUSTPILOT_SLUGS=["test"],
            REVIEWSIO_ROOT=None,
            REDDIT_QUERIES=[],
            REDDIT_SUBREDDITS=[],
            BBB_SEARCH_TEXT="",
            BBB_FALLBACK_PROFILES=[],
            RIPOFF_SEARCH_URL=None,
            SMARTCUSTOMER_ROOT=None,
            BIRDEYE_PAGES=[],
            COMPLAINTSBOARD_ROOT=None,
            APPLE_APP_IDS=[],
        ):
            collector.run_collectors()

        self.assertEqual(collector.records, baseline_records)
        self.assertEqual(collector._seen, baseline_seen)
        self.assertEqual(collector.google_business_profiles, baseline_profiles)
        self.assertEqual(collector.geo_validation_counts, Counter())
        self.assertTrue(collector.collector_failures[0]["retained_previous_data"])
        self.assertEqual(later_collector_ran, [True])

        audit = collector.build_source_health_audit(
            Counter(row["source_website"] for row in collector.records),
            collector.records,
        )
        google_audit = next(row for row in audit if row["source_website"] == "google.com")
        self.assertEqual(google_audit["status"], "retained_after_failed_refresh")
        self.assertEqual(google_audit["review_count"], google_audit["existing_review_count"])
        self.assertTrue(google_audit["errors"])
        self.assertEqual(google_audit["last_successful_refresh_until"], "2026-08-31")

        collector.finalize()
        written = json.loads(collector._test_output_path.read_text(encoding="utf-8"))
        written_google = next(
            row for row in written["meta"]["source_audit"]
            if row["source_website"] == "google.com"
        )
        self.assertEqual(written_google["status"], "retained_after_failed_refresh")
        self.assertEqual(written["reviews"], baseline_records)

    def test_failed_destructive_google_rebuild_remains_fatal(self):
        collector = self.make_collector(replace_google=True)

        def failing_google():
            raise RuntimeError("schema changed")

        collector.collect_google_business = failing_google
        with self.assertRaisesRegex(RuntimeError, "schema changed"):
            collector.run_collectors(only_collector="google_business")

    def test_existing_profile_uses_previous_window_with_overlap(self):
        collector = self.make_collector()
        self.assertEqual(
            collector._google_profile_floor_date(google_profile()),
            "2026-08-17",
        )
        collector.existing_source_audit["google.com"].update(
            {
                "status": "retained_after_failed_refresh",
                "last_successful_refresh_until": "2026-08-31",
            }
        )
        collector.existing_meta["until_date"] = "2026-09-30"
        self.assertEqual(
            collector._google_profile_floor_date(google_profile()),
            "2026-08-17",
        )
        self.assertEqual(
            collector._google_profile_floor_date(
                {**google_profile(), "cid": "999", "feature_id": "0x0:0x3e7"}
            ),
            "2023-01-01",
        )

    def test_retained_google_status_passes_only_when_rows_are_preserved(self):
        payload = baseline_payload()
        audit = payload["meta"]["source_audit"][0]
        audit.update(
            {
                "status": "retained_after_failed_refresh",
                "review_count": 1,
                "existing_review_count": 1,
                "errors": ["newest review RPC did not load"],
                "last_successful_refresh_until": "2026-08-31",
            }
        )
        business = {"google_business_search_names": ["Test Auction"]}
        self.assertEqual(
            audit_review_datasets.validate_google_business("Test", business, payload),
            [],
        )

        audit["review_count"] = 0
        errors = audit_review_datasets.validate_google_business("Test", business, payload)
        self.assertTrue(any("dropped below" in error for error in errors))


class CoverageMergeTests(unittest.TestCase):
    def test_merge_carries_source_audit_into_coverage_note(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            data_dir = root / "data"
            artifact_dir = root / "artifacts" / "test-company"
            data_dir.mkdir()
            artifact_dir.mkdir(parents=True)
            config_path = data_dir / "businesses.json"
            coverage_path = data_dir / "coverage-note.json"
            config = {
                "business_order": ["test"],
                "businesses": {
                    "test": {
                        "display_name": "Test Auction",
                        "output_json": "reviews.json",
                        "output_csv": "reviews.csv",
                    }
                },
            }
            config_path.write_text(json.dumps(config), encoding="utf-8")
            source_audit = [
                {
                    "source_website": "google.com",
                    "status": "retained_after_failed_refresh",
                    "review_count": 1,
                    "existing_review_count": 1,
                    "errors": ["RPC failed"],
                    "last_successful_refresh_until": "2026-08-31",
                }
            ]
            (artifact_dir / "reviews.json").write_text(
                json.dumps(
                    {
                        "meta": {
                            "since_date": "2023-01-01",
                            "until_date": "2026-09-30",
                            "review_count": 1,
                            "source_counts": {"google.com": 1},
                            "source_audit": source_audit,
                        },
                        "reviews": [google_row()],
                    }
                ),
                encoding="utf-8",
            )
            (artifact_dir / "reviews.csv").write_text("id\nrvw-000001\n", encoding="utf-8")
            (artifact_dir / "status.json").write_text(
                json.dumps({"company": "test", "success": True}),
                encoding="utf-8",
            )

            with (
                mock.patch.object(merge_refresh_artifacts, "DATA_DIR", data_dir),
                mock.patch.object(merge_refresh_artifacts, "BUSINESSES_PATH", config_path),
                mock.patch.object(merge_refresh_artifacts, "COVERAGE_NOTE_PATH", coverage_path),
                mock.patch(
                    "sys.argv",
                    [
                        "merge_refresh_artifacts.py",
                        "--artifacts-dir",
                        str(root / "artifacts"),
                        "--since",
                        "2023-01-01",
                        "--until",
                        "2026-09-30",
                    ],
                ),
            ):
                merge_refresh_artifacts.main()

            coverage = json.loads(coverage_path.read_text(encoding="utf-8"))
            self.assertEqual(coverage["refreshed"][0]["source_audit"], source_audit)


if __name__ == "__main__":
    unittest.main()
