import argparse
import csv
from copy import deepcopy
import hashlib
from html import unescape
import json
import math
import re
import time
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import parse_qs, quote, unquote, urlencode, urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from google_play_scraper import Sort, reviews as gp_reviews
try:
    from playwright.sync_api import sync_playwright
except Exception:
    sync_playwright = None

try:
    from langdetect import DetectorFactory, detect as detect_lang
    DetectorFactory.seed = 0
except Exception:
    detect_lang = None

BASE_DIR = Path(__file__).resolve().parents[1]
HIERARCHY_PATH = BASE_DIR / "data" / "tier-hierarchy.json"
DEFAULT_CONFIG_PATH = BASE_DIR / "data" / "businesses.json"


def bootstrap_settings():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--company", default="copart")
    parser.add_argument("--config-path", default=str(DEFAULT_CONFIG_PATH))
    args, _ = parser.parse_known_args()
    payload = json.loads(Path(args.config_path).read_text(encoding="utf-8"))
    business = payload["businesses"][args.company]
    return args.company, business


COMPANY_KEY, BUSINESS_SETTINGS = bootstrap_settings()
DISPLAY_NAME = BUSINESS_SETTINGS["display_name"]
OUTPUT_JSON = BASE_DIR / "data" / BUSINESS_SETTINGS["output_json"]
OUTPUT_CSV = BASE_DIR / "data" / BUSINESS_SETTINGS["output_csv"]

TARGET_DEFAULT = 0
MAX_OUTPUT_DEFAULT = 120000
SINCE_DEFAULT = "2023-01-01"

GOOGLE_PLAY_APPS = BUSINESS_SETTINGS.get("google_play_apps", [])
GOOGLE_PLAY_MARKETS = [tuple(row) for row in BUSINESS_SETTINGS.get("google_play_markets", [
    ["us", "en"],
    ["us", "es"],
    ["us", "fr"],
    ["us", "de"],
    ["us", "pt"],
    ["us", "ru"],
    ["us", "ar"],
    ["us", "it"],
    ["us", "nl"],
    ["us", "tr"],
    ["us", "pl"],
    ["us", "ja"],
    ["us", "ko"],
])]
TRUSTPILOT_SLUGS = BUSINESS_SETTINGS.get("trustpilot_slugs", [])
APPLE_APP_IDS = BUSINESS_SETTINGS.get("apple_app_ids", [])
APPLE_COUNTRIES = BUSINESS_SETTINGS.get("apple_countries", ["us", "gb", "ca"])
REVIEWSIO_ROOT = BUSINESS_SETTINGS.get("reviewsio_root")
COMPLAINTSBOARD_ROOT = BUSINESS_SETTINGS.get("complaintsboard_root")
SMARTCUSTOMER_ROOT = BUSINESS_SETTINGS.get("smartcustomer_root")
BIRDEYE_PAGES = BUSINESS_SETTINGS.get("birdeye_pages", [])
GOOGLE_BUSINESS_SEARCH_NAMES = BUSINESS_SETTINGS.get("google_business_search_names", [])
GOOGLE_BUSINESS_SEARCH_QUERIES = BUSINESS_SETTINGS.get("google_business_search_queries", [])
GOOGLE_BUSINESS_NAME_PREFIXES = [
    str(value).strip().lower()
    for value in BUSINESS_SETTINGS.get("google_business_name_prefixes", [])
    if str(value).strip()
]
GOOGLE_BUSINESS_NAME_EXCLUDE_TERMS = {
    str(value).strip().lower()
    for value in BUSINESS_SETTINGS.get("google_business_name_exclude_terms", [])
    if str(value).strip()
}
GOOGLE_BUSINESS_DOMAINS = {
    str(value).strip().lower().removeprefix("www.")
    for value in BUSINESS_SETTINGS.get("google_business_domains", [])
    if str(value).strip()
}
BBB_SEARCH_TEXT = BUSINESS_SETTINGS.get("bbb_search_text", DISPLAY_NAME)
BBB_FALLBACK_PROFILES = BUSINESS_SETTINGS.get("bbb_fallback_profiles", [])
BBB_PROFILE_TOKENS = {token.lower() for token in BUSINESS_SETTINGS.get("bbb_profile_tokens", [])}
RIPOFF_SEARCH_URL = (
    f"https://www.ripoffreport.com/reports/specific_search/{BUSINESS_SETTINGS['ripoff_search_term']}"
    if BUSINESS_SETTINGS.get("ripoff_search_term")
    else None
)
REDDIT_QUERIES = [tuple(row) for row in BUSINESS_SETTINGS.get("reddit_queries", [])]
REDDIT_SUBREDDITS = BUSINESS_SETTINGS.get("reddit_subreddits", [])
DEFAULT_REDDIT_SEARCH_SUBREDDITS = ["askcarsales", "carflipping"]
REDDIT_SEARCH_SUBREDDITS = BUSINESS_SETTINGS.get("reddit_search_subreddits", DEFAULT_REDDIT_SEARCH_SUBREDDITS)

BASE_US_GEO_MARKERS = {
    " usa ", " united states ", " us yard ", " us lot ", " us auction ",
    " buying from the us ", " bought from the us ", " shipped from the us ",
    " shipping to the us ", " imported from the us ", " dmv ", " salvage title ",
    " texas ", " dallas ", " houston ", " florida ", " miami ", " california ",
    " los angeles ", " new jersey ", " new york ", " chicago ", " arizona ",
    " nevada ", " georgia ", " north carolina ", " south carolina ", " illinois ",
    " pennsylvania ", " ohio ", " washington state ", " united states yard ",
}
BASE_STRONG_US_GEO_MARKERS = {
    " us yard ", " us lot ", " us auction ",
    " buying from the us ", " bought from the us ", " purchased from the us ",
    " purchase from the us ", " shipped from the us ", " shipped to the us ",
    " shipping to the us ", " imported from the us ", " imported to the us ",
    " import into the us ", " export to the us ", " exported to the us ",
    " texas ", " dallas ", " houston ", " florida ", " miami ", " california ",
    " los angeles ", " new jersey ", " new york ", " chicago ", " arizona ",
    " nevada ", " north carolina ", " south carolina ", " illinois ", " pennsylvania ",
    " ohio ", " washington state ",
}
BASE_NON_US_GEO_MARKERS = {
    " uk ", " united kingdom ", " england ", " scotland ", " wales ", " northern ireland ",
    " london ", " bristol ", " manchester ", " wolverhampton ", " rochford ", " westbury ",
    " whitburn ", " dvla ", " mot ", " v5c ", " vat ", " biba ", " cat s ", " cat n ",
    " ireland ", " dublin ", " germany ", " berlin ", " france ", " spain ", " netherlands ",
    " italy ", " canada ", " ontario ", " british columbia ", " australia ", " new zealand ",
    " india ", " mumbai ", " delhi ", " bangalore ", " bengaluru ", " lpa ", " ctc ",
    " £", " ł",
}

US_GEO_MARKERS = BASE_US_GEO_MARKERS | {f" {token.lower()} " for token in BUSINESS_SETTINGS.get("us_geo_markers", [])}
STRONG_US_GEO_MARKERS = BASE_STRONG_US_GEO_MARKERS | {f" {token.lower()} " for token in BUSINESS_SETTINGS.get("strong_us_geo_markers", [])}
NON_US_GEO_MARKERS = BASE_NON_US_GEO_MARKERS | {f" {token.lower()} " for token in BUSINESS_SETTINGS.get("non_us_geo_markers", [])}

MIXED_SOURCE_WEBSITES = {"reddit.com", "smartcustomer.com", "ripoffreport.com", "complaintsboard.com", "reviews.io"}
EXPECTED_SOURCE_WEBSITES = ["reddit.com"]
if GOOGLE_PLAY_APPS:
    EXPECTED_SOURCE_WEBSITES.append("play.google.com")
if APPLE_APP_IDS:
    EXPECTED_SOURCE_WEBSITES.append("apps.apple.com")
if BBB_SEARCH_TEXT or BBB_FALLBACK_PROFILES:
    EXPECTED_SOURCE_WEBSITES.append("bbb.org")
if TRUSTPILOT_SLUGS:
    EXPECTED_SOURCE_WEBSITES.append("trustpilot.com")
if REVIEWSIO_ROOT:
    EXPECTED_SOURCE_WEBSITES.append("reviews.io")
if RIPOFF_SEARCH_URL:
    EXPECTED_SOURCE_WEBSITES.append("ripoffreport.com")
if SMARTCUSTOMER_ROOT:
    EXPECTED_SOURCE_WEBSITES.append("smartcustomer.com")
if COMPLAINTSBOARD_ROOT:
    EXPECTED_SOURCE_WEBSITES.append("complaintsboard.com")
if BIRDEYE_PAGES:
    EXPECTED_SOURCE_WEBSITES.append("birdeye.com")
if GOOGLE_BUSINESS_SEARCH_NAMES:
    EXPECTED_SOURCE_WEBSITES.append("google.com")
REQUIRED_SOURCE_WEBSITES = []
if GOOGLE_PLAY_APPS:
    REQUIRED_SOURCE_WEBSITES.append("play.google.com")
if APPLE_APP_IDS:
    REQUIRED_SOURCE_WEBSITES.append("apps.apple.com")
if BBB_SEARCH_TEXT or BBB_FALLBACK_PROFILES:
    REQUIRED_SOURCE_WEBSITES.append("bbb.org")

ENGLISH_COMMON_WORDS = {
    "the", "and", "for", "that", "with", "this", "was", "are", "but", "have", "not", "you",
    "they", "from", "been", "had", "all", "their", "there", "would", "could", "should",
    "very", "when", "what", "where", "which", "about", "after", "before", "because", "into",
    "while", "than", "then", "only", "also", "just", "your", "our", "his", "her", "them",
    "will", "cant", "cannot", "did", "didnt", "dont", "does", "doesnt", "too", "more",
    "review", "service", "customer", "auction", "vehicle", "car", "cars", "fees",
    "problem", "issue", "support", "help", "good", "bad", "great", "worst", "easy", "hard",
}

POSITIVE_WORDS = {
    "good", "great", "excellent", "awesome", "amazing", "easy", "smooth", "love",
    "helpful", "quick", "fast", "best", "worked", "works", "nice", "reliable", "perfect",
    "pro", "recommend", "happy", "satisfied", "professional", "friendly", "responsive",
    "resolved", "transparent", "fair", "legit", "legitimate", "efficient",
}

NEGATIVE_WORDS = {
    "bad", "worst", "awful", "terrible", "scam", "fraud", "hate", "broken", "problem",
    "issue", "issues", "slow", "delay", "delayed", "damaged", "damage", "missing",
    "refund", "fee", "fees", "overcharge", "rude", "unhelpful", "unable", "cannot", "cant",
    "locked", "suspend", "suspended", "declined", "error", "dispute", "not working",
    "deceptive", "misleading", "bait", "switch", "extortion", "nightmare",
    "stolen", "stole", "theft", "thief", "scammers", "misrepresentation", "misrepresented",
    "lied", "lying", "stress", "horrible", "inoperable",
}

for term in BUSINESS_SETTINGS.get("terms", []):
    for token in re.findall(r"[a-z0-9']+", term.lower()):
        ENGLISH_COMMON_WORDS.add(token)

COMPANY_TERMS = {term.lower() for term in BUSINESS_SETTINGS.get("terms", [])}
BASE_CONTEXT_TERMS = {
    "auction", "bid", "bidding", "buyer", "seller", "salvage", "lot", "yard", "title",
    "pickup", "delivery", "dispatch", "tow", "storage", "gate pass", "membership",
    "deposit", "fee", "fees", "refund", "payment", "wire", "account", "login", "app",
    "support", "customer service", "representative", "agent", "listing", "vehicle",
}
COMPANY_CONTEXT_TERMS = BASE_CONTEXT_TERMS | {
    term.lower() for term in BUSINESS_SETTINGS.get("context_terms", [])
}
BASE_OFFTOPIC_TERMS = {
    "stock", "share price", "ticker", "cprt", "earnings call", "quarterly earnings",
    "investor", "market cap", "dividend", "trading", "options chain",
    "i'm building an ai platform", "building an ai platform", "ai platform specifically",
    "save hours and hundreds", "analyses vehicle damage",
}
OFFTOPIC_TERMS = BASE_OFFTOPIC_TERMS | {
    term.lower() for term in BUSINESS_SETTINGS.get("offtopic_terms", [])
}


def build_exoneration_patterns():
    patterns = [r"\bnot their fault\b", r"\binsurance(?: company)? fault\b", r"\btow (?:company|provider) fault\b", r"\bseller'?s fault\b"]
    for alias in COMPANY_TERMS:
        escaped = re.escape(alias)
        patterns.append(rf"\bnot {escaped}'?s fault\b")
        patterns.append(rf"\bnot {escaped}\b")
    return patterns


EXONERATION_PATTERNS = build_exoneration_patterns()
TRUSTPILOT_LABEL_TOKENS = [f"({slug.lower()})" for slug in TRUSTPILOT_SLUGS]
TRUSTPILOT_URL_TOKENS = [slug.lower() for slug in TRUSTPILOT_SLUGS]
NON_US_TRUSTPILOT_SUFFIXES = (".co.uk", ".de", ".ie", ".es", ".fr", ".nl", ".it", ".ca")
TRUSTPILOT_US_SLUGS = BUSINESS_SETTINGS.get("trustpilot_us_slugs")
if TRUSTPILOT_US_SLUGS is None:
    TRUSTPILOT_US_SLUGS = [
        slug for slug in TRUSTPILOT_SLUGS
        if not any(str(slug).lower().endswith(suffix) for suffix in NON_US_TRUSTPILOT_SUFFIXES)
    ]
TRUSTPILOT_US_LABEL_TOKENS = [f"({slug.lower()})" for slug in TRUSTPILOT_US_SLUGS]
TRUSTPILOT_US_URL_TOKENS = [slug.lower() for slug in TRUSTPILOT_US_SLUGS]
TRUSTPILOT_NON_US_LABEL_TOKENS = [
    f"({slug.lower()})" for slug in TRUSTPILOT_SLUGS if slug not in TRUSTPILOT_US_SLUGS
]
TRUSTPILOT_NON_US_URL_TOKENS = [
    slug.lower() for slug in TRUSTPILOT_SLUGS if slug not in TRUSTPILOT_US_SLUGS
]
REVIEWSIO_URL_TOKENS = [token.lower() for token in BUSINESS_SETTINGS.get("reviewsio_url_tokens", [])]
if not REVIEWSIO_URL_TOKENS and REVIEWSIO_ROOT:
    parsed_root = requests.utils.urlparse(REVIEWSIO_ROOT).path.lower().rstrip("/")
    if parsed_root:
        REVIEWSIO_URL_TOKENS.append(parsed_root.split("/")[-1])
COMPLAINTSBOARD_PATH_TOKEN = ""
if COMPLAINTSBOARD_ROOT:
    COMPLAINTSBOARD_PATH_TOKEN = requests.utils.urlparse(COMPLAINTSBOARD_ROOT).path.rstrip("/").lower()

S = requests.Session()
S.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json,text/plain,*/*",
    "Accept-Language": "en-US,en;q=0.9",
})

READER_PREFIX = "https://r.jina.ai/http://"
CHALLENGE_TERMS = (
    "verifying connection",
    "just a moment",
    "captcha",
    "access denied",
    "cloudflare",
    "enable javascript",
)

GOOGLE_MAPS_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
GOOGLE_BUSINESS_SEARCH_REGIONS = (
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado",
    "Connecticut", "Delaware", "District of Columbia", "Florida", "Georgia",
    "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky",
    "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota",
    "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire",
    "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota",
    "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island",
    "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont",
    "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming",
    "Puerto Rico", "United States",
)
US_GOOGLE_ADDRESS_RE = re.compile(
    r",\s*(?:AL|AK|AZ|AR|CA|CO|CT|DE|DC|FL|GA|HI|ID|IL|IN|IA|KS|KY|LA|ME|MD|MA|"
    r"MI|MN|MS|MO|MT|NE|NV|NH|NJ|NM|NY|NC|ND|OH|OK|OR|PA|RI|SC|SD|TN|TX|UT|VT|"
    r"VA|WA|WV|WI|WY|PR)\s+\d{5}(?:-\d{4})?(?:\b|$)",
    re.I,
)


def unique_preserve(items):
    seen = set()
    ordered = []
    for item in items or []:
        clean = str(item or "").strip()
        if not clean:
            continue
        key = clean.lower()
        if key in seen:
            continue
        seen.add(key)
        ordered.append(clean)
    return ordered


def is_reddit_comment_reference(source_website: str, source_url: str, review_text: str = "") -> bool:
    if str(source_website or "").strip().lower() != "reddit.com":
        return False
    text = str(review_text or "")
    if "Thread context:" in text:
        return True
    try:
        parsed = requests.utils.urlparse(str(source_url or "").strip())
        parts = [part for part in (parsed.path or "").split("/") if part]
    except Exception:
        return False
    return len(parts) >= 6 and len(parts) > 2 and parts[0].lower() == "r" and parts[2].lower() == "comments"


def is_context_enriched_reddit_comment(source_website: str, review_text: str = "") -> bool:
    return (
        str(source_website or "").strip().lower() == "reddit.com"
        and "Thread context:" in str(review_text or "")
    )


class Collector:
    def __init__(
        self,
        target: int,
        since: str,
        until: str | None,
        max_output: int,
        reddit_time_budget: int = 900,
        google_business_query_limit: int = 0,
        google_business_location_limit: int = 0,
        replace_source_websites: set[str] | None = None,
    ):
        self.target = max(0, int(target))
        self.max_output = max(1, int(max_output))
        self.reddit_time_budget = max(60, int(reddit_time_budget))
        self.google_business_query_limit = max(0, int(google_business_query_limit))
        self.google_business_location_limit = max(0, int(google_business_location_limit))
        self.replace_source_websites = {
            str(source).strip().lower()
            for source in (replace_source_websites or set())
            if str(source).strip()
        }
        self.since = self.normalize_date(since)
        self.until = self.normalize_date(until) if until else None
        self.since_date_obj = datetime.strptime(self.since, "%Y-%m-%d").date()
        self.until_date_obj = datetime.strptime(self.until, "%Y-%m-%d").date() if self.until else None
        self.since_ts = int(datetime(self.since_date_obj.year, self.since_date_obj.month, self.since_date_obj.day, tzinfo=timezone.utc).timestamp())
        self.allowed_paths = self._load_allowed_paths()
        self.records = []
        self._seen = set()
        self.collector_failures = []
        self.geo_validation_counts = Counter()
        self.geo_excluded_counts = Counter()
        self.geo_excluded_examples = []
        self.existing_latest_by_source = {}
        self.existing_counts_by_source = Counter()
        self.existing_review_count = 0
        self.existing_meta = {}
        self.existing_source_audit = {}
        self.google_business_profiles = []
        self.existing_google_profile_cids = set()
        self.google_latest_by_cid = {}
        self.source_health = {}
        self.reddit_verified = False
        self.reddit_verification_attempted = False
        self.reddit_browser_ready = False
        self.reddit_browser_attempted = False
        self.reddit_playwright = None
        self.reddit_browser = None
        self.reddit_browser_context = None
        self.reddit_browser_page = None
        self.reddit_post_context_cache = {}
        self._build_path_constants()
        self._load_existing_rows()

    def _load_allowed_paths(self):
        payload = json.loads(HIERARCHY_PATH.read_text(encoding="utf-8"))
        return {
            (row["tier1"], row["tier2"], row["tier3"])
            for row in payload["allowed_paths"]
        }

    def _load_existing_rows(self):
        if not OUTPUT_JSON.exists():
            return
        try:
            payload = json.loads(OUTPUT_JSON.read_text(encoding="utf-8"))
        except Exception:
            return

        self.existing_meta = dict(payload.get("meta") or {})
        self.existing_source_audit = {
            str(row.get("source_website") or "").strip(): dict(row)
            for row in self.existing_meta.get("source_audit") or []
            if isinstance(row, dict) and str(row.get("source_website") or "").strip()
        }
        self.google_business_profiles = [
            dict(row)
            for row in self.existing_meta.get("google_business_profiles") or []
            if isinstance(row, dict) and row.get("feature_id") and row.get("cid")
        ]

        existing_rows = []
        profile_registry = {
            str(row["cid"]): dict(row)
            for row in self.google_business_profiles
            if row.get("feature_id") and row.get("cid")
        }
        for row in payload.get("reviews", []):
            if not isinstance(row, dict):
                continue
            clean_row = dict(row)
            source_website_lower = str(clean_row.get("source_website") or "").strip().lower()
            if source_website_lower in self.replace_source_websites:
                continue
            if source_website_lower == "pissedconsumer.com":
                continue
            review_text = f" {str(clean_row.get('review_text') or '').lower()} "
            if any(self._term_in_text(term, review_text) for term in OFFTOPIC_TERMS):
                continue
            if is_context_enriched_reddit_comment(
                clean_row.get("source_website"),
                clean_row.get("review_text"),
            ):
                continue
            existing_rows.append(clean_row)
            self._remember_existing_key(clean_row)

            source_website = str(clean_row.get("source_website") or "").strip()
            review_date = self.normalize_date(clean_row.get("review_date"))
            if source_website:
                self.existing_counts_by_source[source_website] += 1
            if source_website and review_date > self.existing_latest_by_source.get(source_website, ""):
                self.existing_latest_by_source[source_website] = review_date

            if source_website_lower == "google.com":
                source_url = str(clean_row.get("source_url") or "")
                cid, suffix = self._google_cid_from_source_url(source_url)
                if cid:
                    current_latest = self.google_latest_by_cid.get(cid)
                    if not current_latest or review_date > current_latest:
                        self.google_latest_by_cid[cid] = review_date
                    label = str(clean_row.get("source_label") or "")
                    name_match = re.fullmatch(r"Google Business Profile \((.+)\)", label)
                    if cid not in profile_registry and name_match:
                        profile_registry[cid] = {
                            "feature_id": f"0x0:0x{suffix}",
                            "cid": cid,
                            "place_id": "",
                            "name": name_match.group(1),
                            "address": "Previously validated U.S. Google Business Profile",
                            "website": "",
                            "rating": None,
                            "review_count": 0,
                        }

        self.records.extend(existing_rows)
        self.existing_review_count = len(existing_rows)
        self.google_business_profiles = list(profile_registry.values())
        self.existing_google_profile_cids = set(profile_registry)

    @staticmethod
    def _google_cid_from_source_url(source_url: str) -> tuple[str, str]:
        text = str(source_url or "")
        match = re.search(r"!1s0x0:0x([0-9a-f]+)", text, re.I)
        if match:
            suffix = match.group(1).lower()
            return str(int(suffix, 16)), suffix
        try:
            cid = str(parse_qs(urlparse(text).query).get("cid", [""])[0]).strip()
            if cid.isdigit():
                return cid, format(int(cid), "x")
        except Exception:
            pass
        return "", ""

    def _source_health_entry(self, source_website: str) -> dict:
        source = str(source_website or "").strip()
        if source not in self.source_health:
            self.source_health[source] = {
                "source_website": source,
                "attempted": False,
                "direct_pages": 0,
                "fallback_pages": 0,
                "direct_statuses": {},
                "blocked": False,
                "fallback_used": False,
                "candidate_reviews_seen": 0,
                "new_reviews_added": 0,
                "advertised_total": None,
                "latest_candidate_date": None,
                "notes": [],
                "errors": [],
            }
        return self.source_health[source]

    def note_source_attempt(self, source_website: str, *, status_code=None, blocked=False, fallback=False, pages=0, candidates=0, added=0, latest_date=None, advertised_total=None, note=None, error=None):
        entry = self._source_health_entry(source_website)
        entry["attempted"] = True
        if fallback:
            entry["fallback_used"] = True
            entry["fallback_pages"] += int(pages or 0)
        else:
            entry["direct_pages"] += int(pages or 0)
        if status_code is not None:
            key = str(status_code)
            entry["direct_statuses"][key] = int(entry["direct_statuses"].get(key, 0)) + 1
        if blocked:
            entry["blocked"] = True
        if candidates:
            entry["candidate_reviews_seen"] += int(candidates)
        if added:
            entry["new_reviews_added"] += int(added)
        if advertised_total is not None:
            try:
                entry["advertised_total"] = int(advertised_total)
            except Exception:
                entry["advertised_total"] = advertised_total
        normalized_latest = self.normalize_date(latest_date) if latest_date else None
        if normalized_latest and normalized_latest != "1970-01-01":
            current = entry.get("latest_candidate_date")
            if not current or normalized_latest > current:
                entry["latest_candidate_date"] = normalized_latest
        if note and note not in entry["notes"]:
            entry["notes"].append(str(note)[:300])
        if error:
            entry["errors"].append(str(error)[:300])

    def source_run_start(self, source_website: str) -> int:
        self.note_source_attempt(source_website)
        return len(self.records)

    def source_run_finish(self, source_website: str, start_count: int, *, candidates=0, latest_date=None, advertised_total=None, note=None):
        self.note_source_attempt(
            source_website,
            candidates=candidates,
            added=max(0, len(self.records) - int(start_count)),
            latest_date=latest_date,
            advertised_total=advertised_total,
            note=note,
        )

    @staticmethod
    def is_challenge_response(status_code, text: str) -> bool:
        lowered = str(text or "").lower()
        return int(status_code or 0) in {401, 403, 429, 503} or any(term in lowered[:20000] for term in CHALLENGE_TERMS)

    @staticmethod
    def reader_url(url: str) -> str:
        target = re.sub(r"^https?://", "", str(url or "").strip())
        return f"{READER_PREFIX}{target}"

    def fetch_reader_text(self, url: str, source_website: str) -> str:
        reader = self.reader_url(url)
        try:
            resp = S.get(reader, timeout=60, headers={"Accept": "text/plain,*/*"})
            self.note_source_attempt(source_website, status_code=resp.status_code, fallback=True, pages=1)
            if resp.status_code != 200:
                self.note_source_attempt(source_website, fallback=True, error=f"reader status {resp.status_code} for {url}")
                return ""
            text = resp.text or ""
            if self.is_challenge_response(resp.status_code, text):
                self.note_source_attempt(source_website, fallback=True, blocked=True, note=f"reader challenge for {url}")
                return ""
            return text
        except Exception as exc:
            self.note_source_attempt(source_website, fallback=True, error=f"reader error for {url}: {exc}")
            return ""

    def parse_trustpilot_reader_reviews(self, markdown: str) -> list[dict]:
        lines = str(markdown or "").splitlines()
        heading_re = re.compile(r"^## \[(?P<title>.+?)\]\((?P<url>https?://www\.trustpilot\.com/reviews/(?P<id>[^)]+))\)")
        date_re = re.compile(
            r"^(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},\s+\d{4}$"
            r"|^\d{1,2}/\d{1,2}/\d{4}$",
            re.I,
        )
        noise_lines = {
            "unprompted review",
            "invited review",
            "verified review",
            "discover more",
            "advertisement",
            "autos & vehicles",
            "auto",
            "used vehicles",
            "auctions",
        }

        entries = []
        idx = 0
        while idx < len(lines):
            match = heading_re.match(lines[idx].strip())
            if not match:
                idx += 1
                continue

            title = self.normalize_text(unescape(match.group("title")))
            review_url = match.group("url")
            review_id = match.group("id")
            block = []
            idx += 1
            while idx < len(lines) and not heading_re.match(lines[idx].strip()):
                block.append(lines[idx].strip())
                idx += 1

            review_date = "1970-01-01"
            body_lines = []
            for raw_line in block:
                line = self.normalize_text(unescape(raw_line))
                if not line:
                    continue
                if date_re.match(line):
                    review_date = self.normalize_date(line)
                    break
                lowered = line.lower()
                if lowered in noise_lines or lowered.startswith("![image") or lowered.startswith("see if a website"):
                    continue
                if lowered == title.lower():
                    continue
                body_lines.append(line)

            review_text = self.normalize_text(f"{title}. {' '.join(body_lines)}")
            if review_date == "1970-01-01" or not review_text:
                continue
            entries.append({
                "id": review_id,
                "title": title,
                "text": review_text,
                "date": review_date,
                "url": review_url,
            })
        return entries

    def parse_bbb_reader_customer_reviews(self, markdown: str) -> list[dict]:
        text = str(markdown or "")
        matches = list(re.finditer(r"^\*\s+### Review from (?P<author>.+?)\s*$", text, flags=re.M))
        entries = []
        for idx, match in enumerate(matches):
            block = text[match.end(): matches[idx + 1].start() if idx + 1 < len(matches) else len(text)]
            date_match = re.search(r"\*\*Date:\*\*\s*(?P<date>\d{1,2}/\d{1,2}/\d{4})", block)
            if not date_match:
                continue
            body = block[date_match.end():]
            body = re.split(r"\n\s*\*\*Date:\*\*", body, maxsplit=1)[0]
            body = re.split(r"\s+####\s+", body, maxsplit=1)[0]
            body = self.normalize_text(body)
            rating = None
            rating_match = re.search(r"\b([1-5])\s+stars?\b", body, flags=re.I)
            if rating_match:
                rating = int(rating_match.group(1))
                body = self.normalize_text(re.sub(r"^\s*[1-5]\s+stars?\s+", "", body, flags=re.I))
            if not body:
                continue
            entries.append({
                "author": self.normalize_text(match.group("author")) or "BBB reviewer",
                "date": self.normalize_date(date_match.group("date")),
                "rating": rating,
                "text": body,
                "url_fragment": f"review-{idx + 1}",
            })
        return entries

    def parse_bbb_reader_complaints(self, markdown: str) -> list[dict]:
        text = str(markdown or "")
        matches = list(re.finditer(r"^\*\s+### \[Initial Complaint\]\((?P<url>[^)]+)\)", text, flags=re.M))
        entries = []
        for idx, match in enumerate(matches):
            block = text[match.end(): matches[idx + 1].start() if idx + 1 < len(matches) else len(text)]
            date_match = re.search(r"\*\*Date:\*\*\s*(?P<date>(?:\d{1,2}/\d{1,2}/\d{4}|[A-Za-z]+\s+\d{1,2},\s+\d{4}))", block)
            if not date_match:
                continue
            type_match = re.search(r"\*\*Type:\*\*\s*(?P<type>.*?)\s+\*\*Status:\*\*\s*(?P<status>.*?)(?:\s+More info|\n)", block, flags=re.S)
            complaint_type = self.normalize_text(type_match.group("type") if type_match else "BBB complaint")
            status = self.normalize_text(type_match.group("status") if type_match else "")

            body_start = type_match.end() if type_match else date_match.end()
            body = block[body_start:]
            body = re.split(r"\s+####\s+Business Response", body, maxsplit=1)[0]
            body = re.sub(r"^.*?Complaint statuses\s*", "", body, flags=re.S)
            complaint_match = re.search(r"Complaint:\s*(?P<body>.*)", body, flags=re.S)
            if complaint_match:
                body = complaint_match.group("body")
            body = re.split(r"Desired Resolution:", body, maxsplit=1)[0]
            body = re.sub(
                r"Resolved:The complainant.*?Unpursuable:BBB is unable to locate the business\.\s*",
                "",
                body,
                flags=re.S,
            )
            body = re.sub(r"\*\*Type:\*\*.*?(?:More info)?", "", body, flags=re.S)
            body = self.normalize_text(body)
            if not body:
                continue

            label = f"{complaint_type} complaint".strip()
            if status:
                label = f"{label} ({status})"
            entries.append({
                "author": "BBB complainant",
                "date": self.normalize_date(date_match.group("date")),
                "rating": 1,
                "text": self.normalize_text(f"{label}. {body}"),
                "url": requests.compat.urljoin("https://www.bbb.org", match.group("url")),
            })
        return entries

    def build_source_health_audit(self, source_counts: Counter, rows: list[dict]) -> list[dict]:
        latest_by_source = {}
        for row in rows:
            source = row.get("source_website")
            review_date = self.normalize_date(row.get("review_date"))
            if source and review_date > latest_by_source.get(source, ""):
                latest_by_source[source] = review_date

        audit = []
        for source in EXPECTED_SOURCE_WEBSITES:
            entry = dict(
                self.source_health.get(source)
                or self.existing_source_audit.get(source)
                or {"source_website": source}
            )
            review_count = int(source_counts.get(source, 0))
            existing_count = int(self.existing_counts_by_source.get(source, 0))
            entry.update({
                "source_website": source,
                "review_count": review_count,
                "existing_review_count": existing_count,
                "present": bool(review_count),
                "latest_review_date": latest_by_source.get(source),
                "existing_latest_date": self.existing_latest_by_source.get(source),
            })

            if entry.get("retained_after_failed_refresh"):
                status = "retained_after_failed_refresh"
            elif entry.get("blocked") and not entry.get("fallback_used"):
                status = "blocked"
            elif not entry.get("attempted"):
                status = "not_attempted"
            elif entry.get("candidate_reviews_seen", 0) > 0:
                status = "ok" if review_count > 0 else "parsed_no_new_rows"
            elif review_count > 0:
                notes_text = " ".join(str(note) for note in entry.get("notes", []))
                if "candidate count is not separately tracked" in notes_text:
                    status = "ok"
                else:
                    status = "stale_or_no_recent_candidates"
            else:
                status = "missing"

            if entry.get("advertised_total") and review_count:
                try:
                    total = int(entry["advertised_total"])
                    if total > review_count * 2:
                        entry.setdefault("notes", []).append(
                            f"Advertised total {total} is much larger than accepted rows {review_count}; source is likely partially covered after filters/pagination."
                        )
                        if status == "ok":
                            status = "partial"
                except Exception:
                    pass

            entry["status"] = status
            audit.append(entry)
        return audit

    def _remember_existing_key(self, row: dict):
        source_website = str(row.get("source_website") or "").strip()
        author = row.get("author") or "Anonymous"
        review_date = row.get("review_date") or "1970-01-01"
        review_text = row.get("review_text") or ""
        source_url = row.get("source_url") or ""
        fingerprints = self._content_fingerprints(
            source_website=source_website,
            source_url=source_url,
            author=author,
            review_date=review_date,
            review_text=review_text,
        )
        for fingerprint in fingerprints:
            self._seen.add(fingerprint)

    def _content_fingerprints(self, *, source_website: str, source_url: str, author: str, review_date: str, review_text: str):
        normalized_source = str(source_website or "").strip().lower()
        normalized_url = str(source_url or "").strip()
        normalized_author = self.normalize_text(author).lower()
        normalized_date = self.normalize_date(review_date)
        normalized_text = self.normalize_text(review_text).lower()
        if not normalized_source or not normalized_text:
            return []

        primary = hashlib.sha1(
            json.dumps(
                [normalized_source, normalized_url, normalized_author, normalized_date, normalized_text],
                ensure_ascii=False,
            ).encode("utf-8")
        ).hexdigest()
        fallback = hashlib.sha1(
            json.dumps(
                [normalized_source, normalized_author, normalized_date, normalized_text],
                ensure_ascii=False,
            ).encode("utf-8")
        ).hexdigest()
        return [primary, fallback]

    def source_floor_date(self, source_website: str, overlap_days: int = 21):
        latest = self.existing_latest_by_source.get(source_website)
        if not latest:
            return self.since_date_obj
        try:
            latest_date = datetime.strptime(latest, "%Y-%m-%d").date()
        except Exception:
            return self.since_date_obj
        floor = latest_date - timedelta(days=max(0, int(overlap_days)))
        if floor < self.since_date_obj:
            return self.since_date_obj
        return floor

    def _assert_path(self, path):
        if path not in self.allowed_paths:
            raise ValueError(f"Tier path not allowed: {path}")
        return path

    def _build_path_constants(self):
        self.PATHS = {
            "app_login": self._assert_path(("Account / Access / Login", "Password Reset & Login Troubleshooting", "App Login Troubleshooting")),
            "unable_signin": self._assert_path(("Account / Access / Login", "Account Access Issues", "Unable to sign in")),
            "account_locked": self._assert_path(("Account / Access / Login", "Account Access Issues", "Account Locked")),
            "upload_trouble": self._assert_path(("Account / Access / Login", "Document Upload & Verification", "Upload Troubleshooting")),
            "unable_bid": self._assert_path(("Membership / Licensing / Fees & Bidding Policies", "Auction Eligibility & Licensing", "Unable to Bid")),
            "bid_limit": self._assert_path(("Membership / Licensing / Fees & Bidding Policies", "Bidding Limits & Buying Power", "Buy/Bid Limits Reached")),
            "fees": self._assert_path(("Membership / Licensing / Fees & Bidding Policies", "Bidding Process, Rules and Fees", "Fees")),
            "relist_fee": self._assert_path(("Membership / Licensing / Fees & Bidding Policies", "Bidding Process, Rules and Fees", "Bid Cancellation & Relist Fees")),
            "deposit_refund": self._assert_path(("Payment Refunds, Transaction Issues and Deposits", "Refunds & Membership Billing", "Deposit Refund Status")),
            "buyer_fee": self._assert_path(("Payment Refunds, Transaction Issues and Deposits", "Fees & Charges Disputes", "Buyer Fees Explanation")),
            "card_declined": self._assert_path(("Payment Refunds, Transaction Issues and Deposits", "Payment Methods & Limits", "Card Payment Declined")),
            "wire_delay": self._assert_path(("Payment Refunds, Transaction Issues and Deposits", "Wire Transfer Payments", "Wire Pending/Posting Delay")),
            "title_not_received": self._assert_path(("Title, Ownership, POA and Documentation", "Title Delivery & Status", "Title Not Received")),
            "poa_requirements": self._assert_path(("Title, Ownership, POA and Documentation", "Power of Attorney (POA) Handling", "POA Requirements Clarification")),
            "lot_damage": self._assert_path(("Lot Condition, Listing Status and related", "Lot Condition Reporting", "Lot Damage")),
            "inspection": self._assert_path(("Lot Condition, Listing Status and related", "Third-Party Inspection Authorization & Scheduling", "Previewing/ Inspecting Vehicles")),
            "belongings": self._assert_path(("Lot Condition, Listing Status and related", "Personal belongings/ items", "Removal / Retrieval of items left in vehicle")),
            "pickup_delay": self._assert_path(("Vehicle Pickup, Delivery and Scheduling", "Scheduled Pickup Status", "Missed/ Delayed Pickup and Dispatch Window")),
            "pickup_reschedule": self._assert_path(("Vehicle Pickup, Delivery and Scheduling", "Scheduled Pickup Status", "Schedule/ Reschedule Pickup")),
            "delivery_eta": self._assert_path(("Vehicle Pickup, Delivery and Scheduling", "Delivery Coordination & Handoffs", "Delivery Status and ETA")),
            "gate_pass": self._assert_path(("Vehicle Pickup, Delivery and Scheduling", "Pickup Order Management", "Gate Pass Assistance")),
            "pickup_hold": self._assert_path(("Vehicle Pickup, Delivery and Scheduling", "Pickup Order Management", "Pickup Status/Holds")),
            "tow_storage": self._assert_path(("Vehicle Pickup, Delivery and Scheduling", "Tow and Storage Charges", "Tow and Storage Fees")),
            "helpful_support": self._assert_path(("Customer Service & Communication", "Agent Professionalism & Responsiveness", "Helpful Support Experience")),
            "rude_support": self._assert_path(("Customer Service & Communication", "Agent Professionalism & Responsiveness", "Rude/Unhelpful Support")),
            "followup_good": self._assert_path(("Customer Service & Communication", "Communication Follow-up & Escalation", "Proactive Follow-up")),
            "followup_bad": self._assert_path(("Customer Service & Communication", "Communication Follow-up & Escalation", "No Callback / Unresolved Case")),
            "support_wait_bad": self._assert_path(("Customer Service & Communication", "Support Access & Response Time", "Long Hold Time / Hard to Reach Support")),
            "support_delay_bad": self._assert_path(("Customer Service & Communication", "Support Access & Response Time", "Delayed Email/Phone Response")),
            "support_quick_good": self._assert_path(("Customer Service & Communication", "Support Access & Response Time", "Quick Support Response")),
            "case_unresolved": self._assert_path(("Customer Service & Communication", "Case Resolution Quality", "Issue Not Resolved")),
            "case_resolved": self._assert_path(("Customer Service & Communication", "Case Resolution Quality", "Issue Resolved")),
            "case_escalation": self._assert_path(("Customer Service & Communication", "Case Resolution Quality", "Escalation Required")),
            "bid_howto": self._assert_path(("Membership / Licensing / Fees & Bidding Policies", "Bidding Process, Rules and Fees", "How to Bid (First Time)")),
            "pickup_hours": self._assert_path(("Vehicle Pickup, Delivery and Scheduling", "Scheduled Pickup Status", "Pickup Hours and Cutoff")),
            "listing_sell": self._assert_path(("Lot Condition, Listing Status and related", "Listing Status", "Selling/ Relisting vehicle or Parts purchase")),
        }

        self.rules = [
            (["password", "reset", "login", "log in", "otp", "verification code", "2fa"], self.PATHS["app_login"]),
            (["unable to sign in", "cannot sign in", "cant sign in", "cannot login", "cant login", "login failed"], self.PATHS["unable_signin"]),
            (["account locked", "locked out", "suspended account", "account suspended"], self.PATHS["account_locked"]),
            (["upload", "document", "verification", "kyc", "license photo", "id check"], self.PATHS["upload_trouble"]),
            (["unable to bid", "cannot bid", "cant bid", "not eligible", "dealer license", "bidding restriction"], self.PATHS["unable_bid"]),
            (["buying power", "bid limit", "limit reached", "cannot increase"], self.PATHS["bid_limit"]),
            (["relist", "re-list", "cancel bid", "cancellation fee"], self.PATHS["relist_fee"]),
            (["buyer fee", "hidden fee", "extra fee", "fees too high", "charged fee", "auction fee"], self.PATHS["buyer_fee"]),
            (["refund", "deposit back", "return deposit", "membership refund"], self.PATHS["deposit_refund"]),
            (["card declined", "payment declined", "card not accepted"], self.PATHS["card_declined"]),
            (["wire", "bank transfer", "pending transfer"], self.PATHS["wire_delay"]),
            (["title not received", "no title", "title pending", "waiting title"], self.PATHS["title_not_received"]),
            (["power of attorney", "poa"], self.PATHS["poa_requirements"]),
            (["damaged", "damage", "missing parts", "not as described", "condition issue", "frame damage", "run and drive", "run and drives", "misrepresentation", "misrepresented", "not disclosed", "did not mention"], self.PATHS["lot_damage"]),
            (["personal belongings", "belongings left", "items left", "left in vehicle", "retrieve items", "belongings", "stolen items", "items missing", "property missing", "contents missing", "stolen from vehicle"], self.PATHS["belongings"]),
            (["inspection", "inspect", "preview"], self.PATHS["inspection"]),
            (["reschedule pickup", "schedule pickup", "pickup appointment"], self.PATHS["pickup_reschedule"]),
            (["pickup delay", "missed pickup", "dispatch window", "pickup hold"], self.PATHS["pickup_delay"]),
            (["delivery delay", "late delivery", "eta", "shipping delay"], self.PATHS["delivery_eta"]),
            (["gate pass", "lot release", "release pass"], self.PATHS["gate_pass"]),
            (["pickup hold", "pickup on hold", "release hold"], self.PATHS["pickup_hold"]),
            (["tow", "storage fee", "storage charge", "impound"], self.PATHS["tow_storage"]),
            (["yard directions", "directions", "address", "yard hours", "pickup hours", "cutoff"], self.PATHS["pickup_hours"]),
            (["inventory", "vehicle availability", "listing missing", "not posted", "not listed"], self.PATHS["listing_sell"]),
            (["fee", "fees", "charge", "charged", "overcharge", "cost"], self.PATHS["fees"]),
        ]

    @staticmethod
    def normalize_text(text: str) -> str:
        text = str(text or "").replace("\x00", " ")
        replacements = {
            "â€™": "'",
            "â€˜": "'",
            "â€œ": '"',
            "â€": '"',
            "â€": '"',
            "â€¦": "...",
            "â€“": "-",
            "â€”": "-",
            "Â": "",
        }
        for bad, good in replacements.items():
            text = text.replace(bad, good)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    @staticmethod
    def normalize_date(value: str) -> str:
        s = str(value or "").strip()
        if not s:
            return "1970-01-01"
        m = re.search(r"(\d{4}-\d{2}-\d{2})", s)
        if m:
            return m.group(1)
        m = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", s)
        if m:
            try:
                d = datetime.strptime(m.group(0), "%m/%d/%Y")
                return d.date().isoformat()
            except Exception:
                try:
                    d = datetime.strptime(m.group(0), "%d/%m/%Y")
                    return d.date().isoformat()
                except Exception:
                    pass
        for fmt in ("%b %d, %Y", "%B %d, %Y"):
            try:
                d = datetime.strptime(s, fmt)
                return d.date().isoformat()
            except Exception:
                pass
        try:
            d = datetime.fromisoformat(s.replace("Z", "+00:00"))
            return d.date().isoformat()
        except Exception:
            return "1970-01-01"

    @staticmethod
    def normalize_us_date(value: str) -> str:
        s = str(value or "").strip()
        m = re.search(r"(\d{2}/\d{2}/\d{4})", s)
        if not m:
            return "1970-01-01"
        try:
            d = datetime.strptime(m.group(1), "%m/%d/%Y")
            return d.date().isoformat()
        except Exception:
            return "1970-01-01"

    @staticmethod
    def normalize_relative_date(value: str) -> str:
        text = str(value or "").strip().lower()
        if not text:
            return "1970-01-01"
        if text in {"today", "just now"}:
            return datetime.now(timezone.utc).date().isoformat()
        if text == "yesterday":
            return (datetime.now(timezone.utc).date() - timedelta(days=1)).isoformat()

        match = re.search(r"\b(a|an|\d+)\s+(minute|hour|day|week|month|year)s?\s+ago\b", text)
        if not match:
            return "1970-01-01"

        amount_raw = match.group(1)
        amount = 1 if amount_raw in {"a", "an"} else int(amount_raw)
        unit = match.group(2)
        if unit in {"minute", "hour"}:
            return datetime.now(timezone.utc).date().isoformat()
        days = {
            "day": amount,
            "week": amount * 7,
            "month": amount * 30,
            "year": amount * 365,
        }[unit]
        return (datetime.now(timezone.utc).date() - timedelta(days=days)).isoformat()

    @staticmethod
    def geo_haystack(source_label: str, source_url: str, text: str) -> str:
        return f" {source_label or ''} {source_url or ''} {text or ''} ".lower()

    @staticmethod
    def has_geo_marker(haystack: str, markers: set[str]) -> bool:
        for marker in markers:
            cleaned = str(marker or "").strip().lower()
            if not cleaned:
                continue
            if re.fullmatch(r"[a-z0-9 ]+", cleaned):
                pattern = rf"(?<![a-z0-9]){re.escape(cleaned)}(?![a-z0-9])"
                if re.search(pattern, haystack):
                    return True
            elif cleaned in haystack:
                return True
        return False

    def validate_us_scope(self, source_website: str, source_label: str, source_url: str, text: str):
        label_lower = str(source_label or "").lower()
        url_lower = str(source_url or "").lower()
        text_haystack = f" {text or ''} ".lower()
        has_strong_us_marker = self.has_geo_marker(text_haystack, STRONG_US_GEO_MARKERS)
        has_non_us_marker = self.has_geo_marker(text_haystack, NON_US_GEO_MARKERS)

        if source_website == "bbb.org":
            if has_non_us_marker and not has_strong_us_marker:
                return False, "bbb_us_profile_non_us_marker"
            return True, "bbb_us_business"

        if source_website == "play.google.com":
            if "gl=us" in url_lower:
                if has_non_us_marker and not has_strong_us_marker:
                    return False, "google_play_us_store_non_us_marker"
                return True, "google_play_us_store"
            if has_strong_us_marker:
                return True, "google_play_us_exception"
            return False, "google_play_non_us_store"

        if source_website == "apps.apple.com":
            if "/us/" in url_lower:
                if has_non_us_marker and not has_strong_us_marker:
                    return False, "apple_us_store_non_us_marker"
                return True, "apple_us_store"
            if has_strong_us_marker:
                return True, "apple_us_exception"
            return False, "apple_non_us_store"

        if source_website == "reviews.io":
            if any(token in url_lower for token in REVIEWSIO_URL_TOKENS):
                if has_non_us_marker and not has_strong_us_marker:
                    return False, "reviewsio_us_store_non_us_marker"
                return True, "reviewsio_us_store"
            if has_strong_us_marker:
                return True, "reviewsio_us_exception"
            return False, "reviewsio_non_us_store"

        if source_website == "complaintsboard.com":
            if has_non_us_marker and not has_strong_us_marker:
                return False, "complaintsboard_us_profile_non_us_marker"
            return True, "complaintsboard_us_profile"

        if source_website == "birdeye.com":
            if has_non_us_marker and not has_strong_us_marker:
                return False, "birdeye_us_profile_non_us_marker"
            return True, "birdeye_us_profile"

        if source_website == "google.com":
            # The Google collector admits only profiles whose street address is
            # independently validated as US-based before any reviews are read.
            return True, "google_business_us_profile"

        if source_website == "trustpilot.com":
            is_us_slug = (
                any(token in label_lower for token in TRUSTPILOT_US_LABEL_TOKENS)
                or any(token in url_lower for token in TRUSTPILOT_US_URL_TOKENS)
            )
            is_non_us_slug = (
                any(token in label_lower for token in TRUSTPILOT_NON_US_LABEL_TOKENS)
                or any(token in url_lower for token in TRUSTPILOT_NON_US_URL_TOKENS)
            )
            if is_us_slug:
                if has_non_us_marker and not has_strong_us_marker:
                    return False, "trustpilot_us_slug_non_us_marker"
                return True, "trustpilot_us_slug"
            if is_non_us_slug and not has_strong_us_marker:
                return False, "trustpilot_non_us_slug"
            if has_strong_us_marker:
                return True, "trustpilot_us_exception"
            return False, "trustpilot_non_us_slug"

        if source_website in MIXED_SOURCE_WEBSITES:
            if has_non_us_marker and not has_strong_us_marker:
                return False, "mixed_source_non_us_marker"
            return True, "mixed_source_ok"

        if has_non_us_marker and not has_strong_us_marker:
            return False, "default_non_us_marker"
        return True, "default_ok"

    @staticmethod
    def word_count(text: str) -> int:
        return len(re.findall(r"[a-z0-9']+", str(text or "").lower()))

    def is_on_or_after_since(self, date_value: str) -> bool:
        d = self.normalize_date(date_value)
        try:
            current = datetime.strptime(d, "%Y-%m-%d").date()
        except Exception:
            return False
        return current >= self.since_date_obj

    def is_on_or_before_until(self, date_value: str) -> bool:
        if not self.until_date_obj:
            return True
        d = self.normalize_date(date_value)
        try:
            current = datetime.strptime(d, "%Y-%m-%d").date()
        except Exception:
            return False
        return current <= self.until_date_obj

    @staticmethod
    def source_requires_explicit_copart(source_website: str) -> bool:
        return source_website in {"reddit.com"}

    def is_copart_subreddit(self, source_website: str, source_label: str) -> bool:
        if source_website != "reddit.com":
            return False
        lbl = str(source_label or "").lower()
        return any(f"r/{subreddit.lower()}" in lbl for subreddit in REDDIT_SUBREDDITS)

    def is_reddit_comment_review_candidate(self, body: str, source_label: str, source_url: str = "") -> bool:
        text = self.normalize_text(body)
        lowered = f" {text.lower()} "
        if not text or lowered.strip() in {"[deleted]", "[removed]"}:
            return False
        if self.word_count(text) < 8:
            return False
        if any(term in lowered for term in OFFTOPIC_TERMS):
            return False

        generic_reply_patterns = [
            r"^\W*(same|same here|me too|following|subscribed|this|yes|no|yep|nope|thanks|thank you|good luck|lol|lmao)\W*$",
            r"^\W*(call|email|ask|contact) (them|support|customer service)\W*$",
            r"^\W*(try|just) (calling|emailing|contacting) (them|support|customer service)\W*$",
        ]
        if any(re.search(pattern, lowered.strip()) for pattern in generic_reply_patterns):
            return False

        dedicated_subreddit = self.is_copart_subreddit("reddit.com", source_label)
        has_company_in_body = self.mentions_company(lowered)
        if not has_company_in_body and not dedicated_subreddit:
            return False
        if not dedicated_subreddit and COMPANY_KEY not in {"copart", "iaa"}:
            return False

        has_context = any(self._term_in_text(term, lowered) for term in COMPANY_CONTEXT_TERMS)
        first_person_or_case = bool(re.search(
            r"\b(i|i'm|ive|i've|my|me|we|we're|weve|we've|our|customer|buyer|seller|dealer|member|account)\b",
            lowered,
        ))

        strong_operational_signal_terms = {
            "bought", "buying", "won", "bid", "bidding", "paid", "payment", "charged",
            "fee", "fees", "refund", "deposit", "title", "paperwork", "listing", "lot",
            "damage", "damaged", "condition", "misrepresented", "pickup", "pick up",
            "picked up", "delivery", "delivered", "transport", "tow", "storage", "yard",
            "gate pass", "membership", "license", "account", "login", "app", "support",
            "customer service", "representative", "agent", "arbitration", "invoice",
            "condition report", "inspection report", "auctionaccess", "if sale", "simulcast",
            "green light", "seller guard", "autocheck",
        }
        broad_only_signal_terms = strong_operational_signal_terms | {
            "seller", "buyer", "dealer", "auction", "vehicle", "car", "truck",
        }

        if dedicated_subreddit:
            has_operational_signal = any(self._term_in_text(term, lowered) for term in broad_only_signal_terms)
            if not (has_context and has_operational_signal and (first_person_or_case or has_company_in_body)):
                return False
            return self.is_copart_relevant("reddit.com", source_label, text)

        # Broad Reddit searches are noisy for names like Manheim/Openlane/ACV, so a comment
        # must describe a concrete auction-company interaction, not merely mention a place,
        # stock ticker, software project, or general car-shopping advice.
        has_strong_operational_signal = any(self._term_in_text(term, lowered) for term in strong_operational_signal_terms)
        strong_company_phrase = any(
            len(re.findall(r"[a-z0-9']+", term)) > 1 and self._term_in_text(term, lowered)
            for term in COMPANY_TERMS
        )
        configured_context_phrase = any(
            self._term_in_text(term, lowered)
            for term in BUSINESS_SETTINGS.get("context_terms", [])
            if len(re.findall(r"[a-z0-9']+", str(term))) > 1
        )
        if COMPANY_KEY != "copart" and not (strong_company_phrase or configured_context_phrase or has_strong_operational_signal):
            return False
        if not (has_context and has_strong_operational_signal and first_person_or_case):
            return False

        return self.is_copart_relevant("reddit.com", source_label, text)

    @staticmethod
    def _term_in_text(term: str, haystack: str) -> bool:
        cleaned = str(term or "").strip().lower()
        if not cleaned:
            return False
        if re.fullmatch(r"[a-z0-9 ]+", cleaned):
            return bool(re.search(rf"(?<![a-z0-9]){re.escape(cleaned)}(?![a-z0-9])", haystack))
        return cleaned in haystack

    def mentions_company(self, haystack: str) -> bool:
        return any(self._term_in_text(term, haystack) for term in COMPANY_TERMS)

    def is_copart_relevant(self, source_website: str, source_label: str, text: str) -> bool:
        t = str(text or "").lower()

        if not t:
            return False
        if any(term in t for term in OFFTOPIC_TERMS):
            return False

        has_copart = self.mentions_company(f" {text or ''} ".lower())
        has_context = any(term in t for term in COMPANY_CONTEXT_TERMS)
        has_experience_signal = any(term in t for term in {
            "i ", "my ", "me ", "we ", "our ", "called", "emailed", "bought", "won",
            "lost", "charged", "refunded", "delivered", "picked up", "support", "agent",
            "customer service", "app", "account", "login", "title", "damage", "fee",
        })

        if self.source_requires_explicit_copart(source_website):
            if not has_copart and not self.is_copart_subreddit(source_website, source_label):
                return False
            if self.word_count(t) < 6:
                return False
            if not (has_context or has_experience_signal):
                return False
            return True

        # For dedicated review endpoints (app stores, Trustpilot, BBB, etc.), explicit mention
        # is not always present, but review text still needs operational context. Do not count
        # the source label itself as a company mention; otherwise off-topic Trustpilot posts
        # such as hiring/interview complaints can be incorrectly admitted.
        return has_context or has_copart or has_experience_signal

    @staticmethod
    def is_probably_english(text: str) -> bool:
        t = str(text or "").strip().lower()
        if len(t) < 6:
            return False

        # Primary language check.
        if detect_lang is not None:
            probe = t[:1400]
            try:
                if detect_lang(probe) == "en":
                    return True
                return False
            except Exception:
                pass

        # Conservative fallback when language model is unavailable.
        letters = re.findall(r"[a-z]", t)
        if len(letters) < 3:
            return False

        ascii_chars = sum(1 for ch in t if ord(ch) < 128)
        if ascii_chars / max(1, len(t)) < 0.85:
            return False

        tokens = re.findall(r"[a-z']+", t)
        if not tokens:
            return False

        hits = sum(1 for tok in tokens if tok in ENGLISH_COMMON_WORDS)
        ratio = hits / len(tokens)
        return hits >= 2 or ratio >= 0.08

    def infer_sentiment(self, text: str, rating, source_website: str):
        t = text.lower()
        pos_hits = sum(1 for w in POSITIVE_WORDS if w in t)
        neg_hits = sum(1 for w in NEGATIVE_WORDS if w in t)
        exonerated = any(re.search(pattern, t) for pattern in EXONERATION_PATTERNS)

        if source_website == "complaintsboard.com":
            if neg_hits == 0 and any(k in t for k in {"resolved to the customer's satisfaction", "issue resolved", "highly recommend", "very satisfied"}):
                return "positive"
            return "negative"

        if rating is not None:
            try:
                r = float(rating)
            except Exception:
                r = None
            if r is not None:
                if r >= 4:
                    return "positive"
                if r <= 2:
                    if source_website == "reddit.com" and exonerated:
                        return None
                    return "negative"

        if source_website == "reddit.com" and exonerated and neg_hits >= pos_hits:
            return None

        if pos_hits == 0 and neg_hits == 0:
            return None
        if neg_hits > pos_hits:
            return "negative"
        if pos_hits > neg_hits:
            return "positive"

        # Tie-breakers.
        if any(k in t for k in {"scam", "fraud", "ripoff", "rip off"}):
            return "negative"
        if any(k in t for k in {"recommend", "highly recommend", "great", "excellent"}):
            return "positive"
        if any(self._term_in_text(f"love {term}", t) for term in COMPANY_TERMS):
            return "positive"
        return None

    def classify(self, text: str, sentiment: str):
        t = text.lower()

        service_triggers = [
            "customer service", "support", "agent", "representative", "staff", "team",
            "communication", "communicat", "response", "respond", "callback", "call back",
            "follow up", "follow-up", "email", "contact", "manager", "management",
            "unprofessional", "professional", "courteous", "helpful", "unhelpful", "rude",
            "call center", "service desk", "customer focused", "no answer", "nobody answered",
            "front desk", "frontdesk", "desk clerk", "disrespected", "distrespected",
            "servicio al cliente", "atencion al cliente", "sin respuesta", "no responden",
            "no contestan", "soporte",
        ]

        if any(k in t for k in service_triggers):
            if any(k in t for k in ["escalat", "escalation"]):
                return self.PATHS["case_escalation"]

            if any(k in t for k in [
                "quick response", "fast response", "prompt response", "responded quickly",
                "quick support", "rapid response", "resolved quickly", "atencion rapida",
            ]):
                return self.PATHS["support_quick_good"]

            if any(k in t for k in [
                "wait on hold", "on hold", "hard to reach", "unable to reach", "cant reach",
                "can't reach", "long wait", "no answer", "nobody answered", "busy line",
                "get ahold", "get a hold", "can't get ahold", "cannot get ahold",
                "answer call", "push 1", "transferred", "transfered",
            ]):
                return self.PATHS["support_wait_bad"]

            if any(k in t for k in [
                "no response", "did not respond", "didnt respond", "never responded",
                "no reply", "did not reply", "didnt reply", "delayed response",
                "late response", "no callback", "no call back", "sin respuesta",
                "no responden", "no contestan",
            ]):
                return self.PATHS["support_delay_bad"]

            if any(k in t for k in [
                "not resolved", "unresolved", "did not resolve", "didnt resolve",
                "could not resolve", "couldn't resolve", "no help", "unable to help",
                "could not help", "couldn't help", "problem persists", "still waiting",
            ]):
                return self.PATHS["case_unresolved"]

            if any(k in t for k in [
                "issue resolved", "resolved", "problem solved", "sorted", "fixed",
                "helped me", "got it done",
            ]) and sentiment == "positive":
                return self.PATHS["case_resolved"]

            if any(k in t for k in [
                "callback", "call back", "follow up", "follow-up", "reply", "respond",
            ]):
                return self.PATHS["followup_good"] if sentiment == "positive" else self.PATHS["followup_bad"]

            if sentiment == "positive":
                return self.PATHS["helpful_support"]
            return self.PATHS["rude_support"]

        best_path = None
        best_score = 0
        for keywords, path in self.rules:
            score = sum(1 for kw in keywords if kw in t)
            if score > best_score:
                best_score = score
                best_path = path
        if best_path and best_score > 0:
            return best_path

        if any(re.search(pattern, t) for pattern in [
            r"\bapp\b", r"\bapplication\b", r"\bcrash(?:ed|es|ing)?\b", r"\bfreeze(?:s|d|ing)?\b",
            r"\bglitch(?:es|y)?\b", r"\bbug(?:s)?\b", r"\bupdate(?:d|s)?\b", r"\bloading\b",
            r"\bload(?:ing|s|ed)?\b", r"\blog[\s-]?in\b", r"\bpassword\b",
        ]):
            return self.PATHS["app_login"]
        if any(k in t for k in ["title", "poa", "ownership", "registration"]):
            return self.PATHS["title_not_received"] if sentiment == "negative" else self.PATHS["poa_requirements"]
        if any(k in t for k in ["pickup", "dispatch", "delivery", "transport", "tow", "gate pass", "storage"]):
            return self.PATHS["pickup_delay"] if sentiment == "negative" else self.PATHS["pickup_reschedule"]
        if any(k in t for k in ["damaged", "damage", "not as described", "condition", "parts missing"]):
            return self.PATHS["lot_damage"]
        if any(k in t for k in ["bid", "bidding", "auction", "fees", "fee", "charge", "charged", "buying power", "membership", "license"]):
            return self.PATHS["fees"] if sentiment == "negative" else self.PATHS["bid_howto"]
        if any(k in t for k in ["listing", "listed", "inventory", "vehicle availability", "relist"]):
            return self.PATHS["listing_sell"]

        # If we cannot confidently map to a tier path, drop this row instead of forcing it.
        return None

    def add_review(self, *, source_website, source_label, source_url, author, review_date, rating, review_text, external_id):
        txt = self.normalize_text(review_text)
        if len(txt) < 12:
            return False
        if self.word_count(txt) < 4:
            return False
        if not self.is_probably_english(txt):
            return False

        normalized_date = self.normalize_date(review_date)
        if not self.is_on_or_after_since(normalized_date):
            return False
        if not self.is_on_or_before_until(normalized_date):
            return False
        if not self.is_copart_relevant(source_website, source_label, txt):
            return False

        is_us_scope, geo_reason = self.validate_us_scope(source_website, source_label, source_url, txt)
        if not is_us_scope:
            self.geo_excluded_counts[f"{source_website}:{geo_reason}"] += 1
            if len(self.geo_excluded_examples) < 20:
                self.geo_excluded_examples.append({
                    "source_website": source_website,
                    "source_label": source_label,
                    "source_url": source_url,
                    "review_date": normalized_date,
                    "reason": geo_reason,
                    "review_text": txt[:240],
                })
            return False

        key_id = None
        if external_id:
            key_id = f"ext:{source_website}:{external_id}"
            if key_id in self._seen:
                return False

        content_fingerprints = self._content_fingerprints(
            source_website=source_website,
            source_url=source_url,
            author=author,
            review_date=normalized_date,
            review_text=txt,
        )
        if any(fingerprint in self._seen for fingerprint in content_fingerprints):
            return False

        sentiment = self.infer_sentiment(txt, rating, source_website)
        if sentiment not in {"positive", "negative"}:
            return False

        path = self.classify(txt, sentiment)
        if not path:
            return False
        tier1, tier2, tier3 = path

        if key_id:
            self._seen.add(key_id)
        for fingerprint in content_fingerprints:
            self._seen.add(fingerprint)

        row = {
            "source_website": source_website,
            "source_label": source_label,
            "source_url": source_url,
            "author": self.normalize_text(author)[:120] or "Anonymous",
            "review_date": normalized_date,
            "rating": rating if rating is not None else None,
            "sentiment": sentiment,
            "review_text": txt,
            "geo_validation": geo_reason,
            "tier1": tier1,
            "tier2": tier2,
            "tier3": tier3,
        }
        self.geo_validation_counts[geo_reason] += 1
        self.records.append(row)
        return True

    @staticmethod
    def _nested_get(value, *path, default=None):
        try:
            for index in path:
                value = value[index]
            return value
        except (IndexError, KeyError, TypeError):
            return default

    @staticmethod
    def _google_review_count(place_node) -> int | None:
        raw = Collector._nested_get(place_node, 4, 8)
        if raw is None:
            raw = Collector._nested_get(place_node, 4, 3, 1)
        if isinstance(raw, (int, float)):
            return max(0, int(raw))
        match = re.search(r"([\d,]+)\s+reviews?", str(raw or ""), re.I)
        return int(match.group(1).replace(",", "")) if match else None

    @staticmethod
    def _google_cid(feature_id: str) -> str | None:
        match = re.fullmatch(r"0x[0-9a-f]+:0x([0-9a-f]+)", str(feature_id or "").lower())
        if not match:
            return None
        try:
            return str(int(match.group(1), 16))
        except ValueError:
            return None

    @staticmethod
    def _google_feature_suffix(feature_id: str) -> str:
        return str(feature_id or "").strip().lower().split(":")[-1]

    @staticmethod
    def _is_us_google_address(address: str) -> bool:
        text = str(address or "").strip()
        return bool(
            US_GOOGLE_ADDRESS_RE.search(text)
            or re.search(r"\bUnited States\b", text, re.I)
            or re.search(r"\bPuerto Rico\b", text, re.I)
        )

    @staticmethod
    def _google_business_domain_matches(website: str) -> bool:
        if not website or not GOOGLE_BUSINESS_DOMAINS:
            return False
        candidate = str(website).strip()
        if "://" not in candidate:
            candidate = f"https://{candidate}"
        host = (urlparse(candidate).hostname or "").lower().removeprefix("www.")
        return any(host == domain or host.endswith(f".{domain}") for domain in GOOGLE_BUSINESS_DOMAINS)

    @staticmethod
    def _google_business_name_matches(name: str) -> bool:
        normalized = re.sub(r"\s+", " ", str(name or "").strip().lower())
        if any(term in normalized for term in GOOGLE_BUSINESS_NAME_EXCLUDE_TERMS):
            return False
        return any(
            re.match(rf"^{re.escape(prefix)}(?:\b|\s|[-–—/&,.])", normalized)
            for prefix in GOOGLE_BUSINESS_NAME_PREFIXES
        )

    def _parse_google_business_search_response(self, body: str) -> list[dict]:
        raw = str(body or "")
        if raw.startswith(")]}'"):
            raw = raw.split("\n", 1)[1] if "\n" in raw else ""
        root = json.loads(raw)
        result_rows = self._nested_get(root, 64, default=[])
        if result_rows is None:
            return []
        if not isinstance(result_rows, list):
            raise ValueError("Google Maps search response no longer contains the calibrated result list")

        places = []
        for result in result_rows:
            node = self._nested_get(result, 1)
            if not isinstance(node, list):
                continue
            feature_id = self._nested_get(node, 10)
            cid = self._google_cid(feature_id)
            name = self.normalize_text(self._nested_get(node, 11, default=""))
            address = self.normalize_text(
                self._nested_get(node, 39, default="")
                or self._nested_get(node, 18, default="")
            )
            website = str(self._nested_get(node, 7, 0, default="") or "").strip()
            if not cid or not name or not self._is_us_google_address(address):
                continue
            normalized_name = re.sub(r"\s+", " ", name.strip().lower())
            if any(term in normalized_name for term in GOOGLE_BUSINESS_NAME_EXCLUDE_TERMS):
                continue
            if not (
                self._google_business_domain_matches(website)
                or self._google_business_name_matches(name)
            ):
                continue
            places.append({
                "feature_id": feature_id,
                "cid": cid,
                "place_id": (
                    self._nested_get(node, 78)
                    or self._nested_get(node, 227, 4)
                    or ""
                ),
                "name": name,
                "address": address,
                "website": website,
                "rating": self._nested_get(node, 4, 7),
                "review_count": self._google_review_count(node),
            })
        return places

    def _google_maps_search_places(self, query: str) -> tuple[list[dict], bool]:
        search_url = f"https://www.google.com/maps/search/{quote(query, safe='')}?hl=en&gl=us"
        headers = {
            "User-Agent": GOOGLE_MAPS_USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }
        last_error = None
        for attempt in range(1, 4):
            try:
                landing = S.get(search_url, timeout=45, headers=headers)
                self.note_source_attempt("google.com", status_code=landing.status_code, pages=1)
                if self.is_challenge_response(landing.status_code, landing.text):
                    last_error = f"search challenge ({landing.status_code}) for {query}"
                    time.sleep(attempt * 1.5)
                    continue

                soup = BeautifulSoup(landing.text, "html.parser")
                map_href = next((
                    unescape(link.get("href") or "")
                    for link in soup.find_all("link", href=True)
                    if "tbm=map" in (link.get("href") or "")
                ), "")
                if not map_href:
                    last_error = f"Google Maps discovery link missing for {query}"
                    time.sleep(attempt * 1.5)
                    continue

                map_response = S.get(urljoin("https://www.google.com", map_href), timeout=45, headers=headers)
                self.note_source_attempt("google.com", status_code=map_response.status_code, pages=1)
                if self.is_challenge_response(map_response.status_code, map_response.text):
                    last_error = f"map search challenge ({map_response.status_code}) for {query}"
                    time.sleep(attempt * 1.5)
                    continue
                return self._parse_google_business_search_response(map_response.text), True
            except Exception as exc:
                last_error = f"Google Maps search failed for {query}: {exc}"
                time.sleep(attempt * 1.5)

        self.note_source_attempt("google.com", error=last_error)
        return [], False

    def discover_google_business_places(self) -> list[dict]:
        queue = [
            (f"{search_name} {region}", search_name, region, False)
            for search_name in GOOGLE_BUSINESS_SEARCH_NAMES
            for region in GOOGLE_BUSINESS_SEARCH_REGIONS
        ]
        queue.extend(
            (str(query), str(query), "", True)
            for query in GOOGLE_BUSINESS_SEARCH_QUERIES
            if str(query).strip()
        )
        discovered = {
            str(row["cid"]): dict(row)
            for row in self.google_business_profiles
            if row.get("feature_id") and row.get("cid")
        }
        successful_queries = 0
        attempted_queries = 0
        failed_queries = []
        queued_queries = {query.lower() for query, _, _, _ in queue}

        while queue:
            if self.google_business_query_limit and attempted_queries >= self.google_business_query_limit:
                break
            query, search_name, region, is_refinement = queue.pop(0)
            attempted_queries += 1
            rows, succeeded = self._google_maps_search_places(query)
            if succeeded:
                successful_queries += 1
            else:
                failed_queries.append(query)
            for row in rows:
                cid = str(row["cid"])
                discovered[cid] = {**discovered.get(cid, {}), **row}

            # The search endpoint returns at most about 20 profiles. Refine a
            # saturated state query so large state networks are not truncated.
            if succeeded and not is_refinement and len(rows) >= 18 and region != "United States":
                for direction in ("North", "South", "East", "West", "Central"):
                    refined = f"{search_name} {direction} {region}"
                    key = refined.lower()
                    if key not in queued_queries:
                        queued_queries.add(key)
                        queue.append((refined, search_name, region, True))
            time.sleep(0.08)

        if successful_queries == 0:
            self.note_source_attempt(
                "google.com",
                blocked=True,
                error="Google Business Profile discovery failed for every query",
            )
            raise RuntimeError("Google Business Profile discovery failed for every query")
        if failed_queries:
            failure_preview = ", ".join(failed_queries[:5])
            self.note_source_attempt(
                "google.com",
                error=(
                    f"Google Business Profile discovery remained incomplete after retries: "
                    f"{len(failed_queries)}/{attempted_queries} queries failed ({failure_preview})"
                ),
            )
            raise RuntimeError(
                "Google Business Profile discovery was incomplete after retries; "
                "refusing to write a partial company artifact"
            )

        places = sorted(
            discovered.values(),
            key=lambda row: (row["name"].lower(), row["address"].lower(), row["feature_id"]),
        )
        if self.google_business_location_limit:
            places = places[:self.google_business_location_limit]
        self.google_business_profiles = [dict(row) for row in places]
        self.note_source_attempt(
            "google.com",
            note=(
                f"Google Business Profile discovery completed: {successful_queries}/{attempted_queries} "
                f"queries succeeded and {len(places)} unique validated US profiles were selected."
            ),
        )
        return places

    def _google_profile_floor_date(self, place: dict, overlap_days: int = 14) -> str:
        cid = str(place.get("cid") or "")
        checkpoint = str(place.get("last_successful_scan_date") or "").strip()
        prior_google_audit = self.existing_source_audit.get("google.com") or {}
        if not checkpoint and cid in self.existing_google_profile_cids:
            if prior_google_audit.get("status") == "ok":
                checkpoint = str(self.existing_meta.get("until_date") or "").strip()
            elif prior_google_audit.get("status") == "retained_after_failed_refresh":
                checkpoint = str(
                    prior_google_audit.get("last_successful_refresh_until") or ""
                ).strip()
        if not checkpoint:
            checkpoint = str(self.google_latest_by_cid.get(cid) or "").strip()
        try:
            checkpoint_date = datetime.strptime(checkpoint, "%Y-%m-%d").date()
        except (TypeError, ValueError):
            return self.since
        return max(
            self.since_date_obj,
            checkpoint_date - timedelta(days=overlap_days),
        ).isoformat()

    @staticmethod
    def _parse_google_rpc_request(post_data: str) -> dict:
        form = parse_qs(str(post_data or ""))
        outer = json.loads(form["f.req"][0])
        inner = json.loads(outer[0][0][1])
        return {
            "feature_id": Collector._nested_get(inner, 0, 0, 0, default=""),
            "continuation": Collector._nested_get(inner, 1, 1),
            "sort_mode": Collector._nested_get(inner, -1, 0),
        }

    @staticmethod
    def _build_google_rpc_continuation(post_data: str, continuation: str) -> str:
        form = parse_qs(str(post_data or ""))
        outer = json.loads(form["f.req"][0])
        inner = json.loads(outer[0][0][1])
        inner[1][1] = continuation
        outer[0][0][1] = json.dumps(inner, separators=(",", ":"))
        return urlencode({"f.req": json.dumps(outer, separators=(",", ":"))}) + "&"

    @staticmethod
    def _parse_google_rpc_payload(body: str) -> tuple[list, str | None]:
        for line in str(body or "").splitlines():
            line = line.strip()
            if not line.startswith("[["):
                continue
            try:
                wrapper = json.loads(line)
            except Exception:
                continue
            for item in wrapper if isinstance(wrapper, list) else []:
                if not (isinstance(item, list) and len(item) >= 3 and item[0] == "wrb.fr" and item[1] == "qv9Egd"):
                    continue
                payload = json.loads(item[2])
                batches = payload[2] if len(payload) > 2 and isinstance(payload[2], list) else []
                rows = []
                for batch in batches:
                    candidate = batch[0] if isinstance(batch, list) and batch else None
                    if isinstance(candidate, list) and len(candidate) >= 3:
                        rows.append(candidate)
                return rows, payload[1] if len(payload) > 1 else None
        raise ValueError("Google review RPC response no longer matches the calibrated schema")

    @staticmethod
    def _google_timestamp(value) -> tuple[str, str]:
        try:
            numeric = float(value)
            if numeric > 10**14:
                numeric /= 1_000_000
            elif numeric > 10**11:
                numeric /= 1_000
            parsed = datetime.fromtimestamp(numeric, tz=timezone.utc)
            if not 2000 <= parsed.year <= 2100:
                raise ValueError("timestamp year out of range")
            return parsed.date().isoformat(), parsed.isoformat()
        except Exception:
            return "1970-01-01", "1970-01-01T00:00:00+00:00"

    def _parse_google_review_record(self, record: list, feature_id: str) -> dict | None:
        metadata = self._nested_get(record, 1)
        content = self._nested_get(record, 2)
        if not isinstance(metadata, list) or not isinstance(content, list):
            return None
        expected_entity = f"0x0:{str(feature_id).split(':')[-1].lower()}"
        entity = str(self._nested_get(metadata, 0, default="") or "").lower()
        if entity and entity != expected_entity:
            return None

        review_id = str(self._nested_get(record, 0, default="") or "").strip()
        author = self.normalize_text(self._nested_get(metadata, 4, 5, 0, default=""))
        created_date, created_at = self._google_timestamp(self._nested_get(metadata, 2))
        modified_date, modified_at = self._google_timestamp(self._nested_get(metadata, 3))
        rating = self._nested_get(content, 0, 0)
        language_metadata = self._nested_get(content, 14, default=[])
        original_language = (
            str(language_metadata[0]).strip().lower()
            if isinstance(language_metadata, list) and language_metadata
            else ""
        )
        fragments = self._nested_get(content, 15, default=[])
        # Google may return the original review followed by an English
        # translation. Keep only the original fragment so translated
        # non-English reviews cannot pass the English-only rule.
        review_text = self.normalize_text(
            next((
                str(fragment[0])
                for fragment in fragments
                if isinstance(fragment, list) and fragment and fragment[0]
            ), "")
        )
        permalink = str(self._nested_get(record, 4, 3, 0, default="") or "").strip()
        return {
            "review_id": review_id,
            "author": author or "Google user",
            "review_date": created_date,
            "created_at": created_at,
            "sort_date": modified_date if modified_date != "1970-01-01" else created_date,
            "modified_at": modified_at,
            "rating": rating,
            "original_language": original_language,
            "review_text": review_text,
            "permalink": permalink,
        }

    @staticmethod
    def _click_google_control(page, *, role: str, text_pattern: re.Pattern) -> bool:
        # Native buttons expose an implicit ARIA role and therefore do not
        # necessarily carry a literal role="button" attribute in the DOM.
        locator = page.locator("button") if role == "button" else page.locator(f"[role='{role}']")
        for index in range(locator.count()):
            control = locator.nth(index)
            try:
                label = f"{control.get_attribute('aria-label') or ''} {control.inner_text()}".strip()
                if text_pattern.search(label):
                    control.click(timeout=5000)
                    return True
            except Exception:
                continue
        return False

    def _scrape_google_business_place(
        self, page, place: dict, stop_before_date: str | None = None
    ) -> tuple[list[dict], bool, str]:
        feature_id = place["feature_id"]
        history_boundary = stop_before_date or self.since
        state = {"feature_id": feature_id, "newest": [], "relevant": [], "errors": []}

        def handle_response(response):
            if "rpcids=qv9Egd" not in response.url:
                return
            try:
                request_info = self._parse_google_rpc_request(response.request.post_data or "")
                if self._google_feature_suffix(request_info["feature_id"]) != self._google_feature_suffix(state["feature_id"]):
                    return
                body = response.body().decode("utf-8", "replace")
                rows, continuation = self._parse_google_rpc_payload(body)
                parsed = [
                    review for review in (
                        self._parse_google_review_record(row, feature_id) for row in rows
                    ) if review is not None
                ]
                request_headers = response.request.all_headers()
                entry = {
                    "reviews": parsed,
                    "continuation": continuation,
                    "request_url": response.request.url,
                    "post_data": response.request.post_data or "",
                    "bgkey": request_headers.get("x-maps-bgkey", ""),
                }
                target = "newest" if request_info["sort_mode"] == 2 else "relevant"
                state[target].append(entry)
                self.note_source_attempt("google.com", status_code=response.status, pages=1)
            except Exception as exc:
                state["errors"].append(str(exc))

        page.on("response", handle_response)
        maps_url = f"https://www.google.com/maps?cid={place['cid']}&hl=en&gl=us"
        completed = False
        failure_reason = ""

        try:
            for attempt in range(2):
                state["newest"].clear()
                state["relevant"].clear()
                state["errors"].clear()
                try:
                    page.goto(maps_url, wait_until="domcontentloaded", timeout=60000)
                    page.wait_for_timeout(4500)
                    opened = self._click_google_control(
                        page,
                        role="tab",
                        text_pattern=re.compile(r"^\s*Reviews\b", re.I),
                    )
                    if not opened:
                        opened = self._click_google_control(
                            page,
                            role="button",
                            text_pattern=re.compile(r"\bMore reviews\b", re.I),
                        )
                    if opened:
                        page.wait_for_timeout(5000)

                    sort_opened = self._click_google_control(
                        page,
                        role="button",
                        text_pattern=re.compile(r"\bSort reviews\b", re.I),
                    )
                    if sort_opened:
                        page.wait_for_timeout(500)
                        self._click_google_control(
                            page,
                            role="menuitemradio",
                            text_pattern=re.compile(r"^\s*Newest\s*$", re.I),
                        )
                        for _ in range(40):
                            if state["newest"]:
                                break
                            page.wait_for_timeout(250)

                    if state["newest"]:
                        break

                    advertised = int(place.get("review_count") or 0)
                    relevant_rows = sum(len(batch["reviews"]) for batch in state["relevant"])
                    if state["relevant"] and (advertised <= 10 or relevant_rows >= advertised):
                        state["newest"] = list(state["relevant"])
                        break
                    if advertised <= 0:
                        return [], True, "profile has no advertised reviews"

                    if attempt == 0:
                        bootstrap = quote(f"{place['name']} {place['address']}", safe="")
                        page.goto(
                            f"https://www.google.com/maps/search/{bootstrap}?hl=en&gl=us",
                            wait_until="domcontentloaded",
                            timeout=60000,
                        )
                        page.wait_for_timeout(2500)
                except Exception as exc:
                    failure_reason = str(exc)

            if not state["newest"]:
                detail = "; ".join(state["errors"][-3:]) or failure_reason or "newest review RPC did not load"
                return [], False, detail

            unique_reviews = {}
            processed_batches = 0
            idle_rounds = 0
            stop_by_date = False
            terminal_page = False
            advertised = int(place.get("review_count") or 0)

            while processed_batches < len(state["newest"]):
                batch = state["newest"][processed_batches]
                processed_batches += 1
                for review in batch["reviews"]:
                    key = review["review_id"] or hashlib.sha1(
                        f"{review['author']}|{review['created_at']}|{review['review_text']}".encode("utf-8")
                    ).hexdigest()
                    unique_reviews[key] = review

                sort_dates = [
                    review["sort_date"] for review in batch["reviews"]
                    if review["sort_date"] != "1970-01-01"
                ]
                if sort_dates and max(sort_dates) < history_boundary:
                    stop_by_date = True
                    break
                if not batch["continuation"] or len(batch["reviews"]) < 10:
                    terminal_page = True
                    break

            # Replay Google's signed continuation request directly. This keeps
            # the browser-established session and exact RPC schema but avoids
            # the Maps UI's roughly 500-card virtual-scroll ceiling.
            direct_template = next((
                batch for batch in state["newest"]
                if batch.get("post_data") and batch.get("request_url") and batch.get("bgkey")
            ), None)
            seen_continuations = set()
            direct_failed = False
            while not (stop_by_date or terminal_page):
                last_batch = state["newest"][-1]
                continuation = last_batch.get("continuation")
                if not continuation:
                    terminal_page = True
                    break
                if continuation in seen_continuations:
                    direct_failed = True
                    state["errors"].append("Google review RPC repeated a continuation token")
                    break
                seen_continuations.add(continuation)
                if direct_template is None:
                    direct_failed = True
                    state["errors"].append("Google review RPC signing header was unavailable")
                    break
                try:
                    request_body = self._build_google_rpc_continuation(
                        direct_template["post_data"], continuation
                    )
                    api_response = page.context.request.post(
                        direct_template["request_url"],
                        data=request_body,
                        headers={
                            "content-type": "application/x-www-form-urlencoded;charset=UTF-8",
                            "origin": "https://www.google.com",
                            "referer": "https://www.google.com/",
                            "x-maps-bgkey": direct_template["bgkey"],
                            "x-same-domain": "1",
                        },
                        timeout=60000,
                    )
                    self.note_source_attempt(
                        "google.com", status_code=api_response.status, pages=1
                    )
                    rpc_rows, next_continuation = self._parse_google_rpc_payload(api_response.text())
                    parsed = [
                        review for review in (
                            self._parse_google_review_record(row, feature_id) for row in rpc_rows
                        ) if review is not None
                    ]
                    if not parsed:
                        raise ValueError("Google continuation RPC returned no review records")
                    batch = {"reviews": parsed, "continuation": next_continuation}
                    state["newest"].append(batch)
                    processed_batches += 1
                    for review in parsed:
                        key = review["review_id"] or hashlib.sha1(
                            f"{review['author']}|{review['created_at']}|{review['review_text']}".encode("utf-8")
                        ).hexdigest()
                        unique_reviews[key] = review
                    sort_dates = [
                        review["sort_date"] for review in parsed
                        if review["sort_date"] != "1970-01-01"
                    ]
                    if sort_dates and max(sort_dates) < history_boundary:
                        stop_by_date = True
                        break
                    if not next_continuation or len(parsed) < 10:
                        terminal_page = True
                        break
                    if advertised and len(unique_reviews) >= advertised:
                        terminal_page = True
                        break
                    time.sleep(0.08)
                except Exception as exc:
                    direct_failed = True
                    state["errors"].append(f"direct continuation failed: {exc}")
                    break

            while direct_failed and not (stop_by_date or terminal_page):
                if advertised and len(unique_reviews) >= advertised:
                    terminal_page = True
                    break
                before = len(state["newest"])
                scroll_state = page.evaluate("""
                    () => {
                      const panels = Array.from(document.querySelectorAll('div')).filter((node) =>
                        node.scrollHeight > node.clientHeight + 200 &&
                        node.clientHeight > 250 &&
                        node.getBoundingClientRect().left < 650
                      ).sort((a, b) => b.scrollHeight - a.scrollHeight);
                      if (!panels.length) return { moved: false, x: 300, y: 600 };
                      const panel = panels[0];
                      const previous = panel.scrollTop;
                      panel.scrollTop = Math.min(
                        panel.scrollHeight,
                        panel.scrollTop + Math.round(panel.clientHeight * 0.8)
                      );
                      const box = panel.getBoundingClientRect();
                      return {
                        moved: panel.scrollTop > previous + 5,
                        x: Math.max(1, Math.min(window.innerWidth - 2, box.left + box.width / 2)),
                        y: Math.max(1, Math.min(window.innerHeight - 2, box.top + box.height / 2))
                      };
                    }
                """)
                page.wait_for_timeout(1800)
                if len(state["newest"]) == before:
                    idle_rounds += 1
                    if idle_rounds >= 8:
                        break
                    if not scroll_state.get("moved"):
                        page.mouse.move(scroll_state["x"], scroll_state["y"])
                        page.mouse.wheel(0, 6000)
                        page.keyboard.press("PageDown")
                    continue
                idle_rounds = 0
                while processed_batches < len(state["newest"]):
                    batch = state["newest"][processed_batches]
                    processed_batches += 1
                    for review in batch["reviews"]:
                        key = review["review_id"] or hashlib.sha1(
                            f"{review['author']}|{review['created_at']}|{review['review_text']}".encode("utf-8")
                        ).hexdigest()
                        unique_reviews[key] = review
                    sort_dates = [
                        review["sort_date"] for review in batch["reviews"]
                        if review["sort_date"] != "1970-01-01"
                    ]
                    if sort_dates and max(sort_dates) < history_boundary:
                        stop_by_date = True
                        break
                    if not batch["continuation"] or len(batch["reviews"]) < 10:
                        terminal_page = True
                        break

            completed = stop_by_date or terminal_page or (advertised and len(unique_reviews) >= advertised)
            if not completed:
                failure_reason = (
                    f"pagination stopped before the {history_boundary} boundary/terminal page "
                    f"({len(unique_reviews)} RPC reviews; advertised={advertised or 'unknown'})"
                )
            return list(unique_reviews.values()), bool(completed), failure_reason
        finally:
            page.remove_listener("response", handle_response)

    def collect_google_business(self):
        print("[collect] Google Business Profile reviews")
        start_count = self.source_run_start("google.com")
        places = self.discover_google_business_places()
        if not places:
            self.source_run_finish(
                "google.com",
                start_count,
                note="No matching US Google Business Profiles were discoverable for this company.",
            )
            raise RuntimeError(
                "Google Business Profile discovery returned zero validated profiles; "
                "refusing to write a partial company artifact"
            )
        if sync_playwright is None:
            raise RuntimeError("Playwright is required for Google Business Profile review pagination")

        candidates_seen = 0
        latest_candidate_date = None
        failed_profiles = []
        completed_profiles = 0
        existing_author_text = {
            hashlib.sha1(
                f"{self.normalize_text(row.get('author')).lower()}|{self.normalize_text(row.get('review_text')).lower()}".encode("utf-8")
            ).hexdigest()
            for row in self.records
            if row.get("review_text")
        }

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(
                headless=True,
                args=["--disable-blink-features=AutomationControlled", "--lang=en-US"],
            )
            def new_google_page():
                new_context = browser.new_context(
                    user_agent=GOOGLE_MAPS_USER_AGENT,
                    viewport={"width": 1200, "height": 1800},
                    locale="en-US",
                    timezone_id="America/Chicago",
                )
                new_page = new_context.new_page()
                bootstrap = quote(f"{GOOGLE_BUSINESS_SEARCH_NAMES[0]} United States", safe="")
                new_page.goto(
                    f"https://www.google.com/maps/search/{bootstrap}?hl=en&gl=us",
                    wait_until="domcontentloaded",
                    timeout=60000,
                )
                new_page.wait_for_timeout(3000)
                return new_context, new_page

            context, page = new_google_page()

            for index, place in enumerate(places, start=1):
                floor_date = self._google_profile_floor_date(place)
                reviews, completed, error = self._scrape_google_business_place(
                    page, place, floor_date
                )
                if not completed:
                    context.close()
                    context, page = new_google_page()
                    reviews, completed, error = self._scrape_google_business_place(
                        page, place, floor_date
                    )
                if not completed:
                    failed_profiles.append(f"{place['name']} [{place['feature_id']}]: {error}")
                    break
                completed_profiles += 1
                place["last_successful_scan_date"] = (
                    self.until or datetime.now(timezone.utc).date().isoformat()
                )
                candidates_seen += len(reviews)
                for review in reviews:
                    if review.get("original_language") not in {"", "en"}:
                        continue
                    if review["review_date"] != "1970-01-01":
                        if latest_candidate_date is None or review["review_date"] > latest_candidate_date:
                            latest_candidate_date = review["review_date"]
                    cross_source_key = hashlib.sha1(
                        f"{self.normalize_text(review['author']).lower()}|{self.normalize_text(review['review_text']).lower()}".encode("utf-8")
                    ).hexdigest()
                    if cross_source_key in existing_author_text:
                        continue
                    source_url = review["permalink"] or (
                        f"https://www.google.com/maps?cid={place['cid']}&hl=en&gl=us"
                        f"#review-{quote(review['review_id'], safe='')}"
                    )
                    added = self.add_review(
                        source_website="google.com",
                        source_label=f"Google Business Profile ({place['name']})",
                        source_url=source_url,
                        author=review["author"],
                        review_date=review["review_date"],
                        rating=review["rating"],
                        review_text=review["review_text"],
                        external_id=f"google_business_{review['review_id']}",
                    )
                    if added:
                        existing_author_text.add(cross_source_key)

                if index % 10 == 0 or index == len(places):
                    print(
                        f"  - Google profiles {index}/{len(places)}; "
                        f"RPC candidates {candidates_seen}; added {len(self.records) - start_count}"
                    )

            self.google_business_profiles = [dict(row) for row in places]
            context.close()
            browser.close()

        if failed_profiles:
            for error in failed_profiles[:20]:
                self.note_source_attempt("google.com", error=error)
            raise RuntimeError(
                f"Google Business Profile coverage incomplete: {len(failed_profiles)}/{len(places)} "
                f"profiles failed pagination; first failure: {failed_profiles[0]}"
            )

        self.source_run_finish(
            "google.com",
            start_count,
            candidates=candidates_seen,
            latest_date=latest_candidate_date,
            note=(
                f"Validated {completed_profiles} US Google Business Profiles; paginated newest-first "
                f"with exact RPC timestamps through per-profile incremental overlap boundaries."
            ),
        )
        self._source_health_entry("google.com")["last_successful_refresh_until"] = (
            self.until or datetime.now(timezone.utc).date().isoformat()
        )
        print(f"  - Added {len(self.records) - start_count} Google Business Profile reviews")

    def collect_google_play(self):
        print("[collect] Google Play reviews")
        start_count = self.source_run_start("play.google.com")
        candidates_seen = 0
        latest_candidate_date = None
        for app_id in GOOGLE_PLAY_APPS:
            for country, lang in GOOGLE_PLAY_MARKETS:
                continuation = None
                pages = 0
                while pages < 70:
                    kwargs = {
                        "lang": lang,
                        "country": country,
                        "sort": Sort.NEWEST,
                        "count": 200,
                    }
                    if continuation:
                        kwargs["continuation_token"] = continuation

                    try:
                        batch, continuation = gp_reviews(app_id, **kwargs)
                    except Exception:
                        break

                    if not batch:
                        break

                    batch_oldest_date = None
                    for item in batch:
                        dt = item.get("at")
                        if isinstance(dt, datetime):
                            date_iso = dt.date().isoformat()
                        else:
                            date_iso = "1970-01-01"
                        if batch_oldest_date is None or date_iso < batch_oldest_date:
                            batch_oldest_date = date_iso
                        candidates_seen += 1
                        if date_iso != "1970-01-01" and (latest_candidate_date is None or date_iso > latest_candidate_date):
                            latest_candidate_date = date_iso

                        self.add_review(
                            source_website="play.google.com",
                            source_label=f"Google Play ({app_id})",
                            source_url=f"https://play.google.com/store/apps/details?id={app_id}&hl={lang}&gl={country}",
                            author=item.get("userName") or "Google Play user",
                            review_date=date_iso,
                            rating=item.get("score"),
                            review_text=item.get("content") or "",
                            external_id=item.get("reviewId"),
                        )

                    pages += 1
                    if pages % 6 == 0:
                        print(f"  - {app_id} {country}/{lang}: {len(self.records)} collected")

                    if batch_oldest_date and batch_oldest_date < self.since:
                        break
                    if not continuation:
                        break
        self.source_run_finish("play.google.com", start_count, candidates=candidates_seen, latest_date=latest_candidate_date)

    @staticmethod
    def _decode_apple_html_value(value: str) -> str:
        text = str(value or "")
        try:
            text = json.loads(f'"{text}"')
        except Exception:
            pass
        if any(token in text for token in ("â", "Ã", "ā")):
            for source_encoding in ("latin-1", "cp1252"):
                try:
                    repaired = text.encode(source_encoding).decode("utf-8")
                    if repaired:
                        text = repaired
                        break
                except Exception:
                    continue
        return text

    @staticmethod
    def apple_get(url: str):
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json,text/plain,text/html,*/*",
            "Accept-Language": "en-US,en;q=0.9",
        }
        for attempt in range(3):
            try:
                resp = requests.get(url, timeout=35, headers=headers)
                if resp.status_code == 200:
                    return resp
                if resp.status_code in {400, 404}:
                    return resp
            except Exception:
                pass
            time.sleep(0.4 * (attempt + 1))
        return None

    def collect_apple_html_reviews(self, app_id: str, country: str) -> int:
        page_url = f"https://apps.apple.com/{country}/app/id{app_id}?see-all=reviews&platform=iphone"
        try:
            resp = self.apple_get(page_url)
            if not resp or resp.status_code != 200:
                return 0
            html = resp.text
        except Exception:
            return 0

        pattern = re.compile(
            r'"\$kind":"ProductReview".*?"review":\{"\$kind":"Review","id":"(?P<id>\d+)".*?"title":"(?P<title>(?:[^"\\]|\\.)*)".*?"date":"(?P<date>[^"]+)".*?"contents":"(?P<contents>(?:[^"\\]|\\.)*)".*?"rating":(?P<rating>\d+).*?"reviewerName":"(?P<author>(?:[^"\\]|\\.)*)"',
            re.S,
        )

        seen_review_ids = set()
        added = 0
        for match in pattern.finditer(html):
            review_id = match.group("id")
            if review_id in seen_review_ids:
                continue
            seen_review_ids.add(review_id)

            title = self._decode_apple_html_value(match.group("title"))
            contents = self._decode_apple_html_value(match.group("contents"))
            author = self._decode_apple_html_value(match.group("author")) or "Apple user"
            review_text = f"{title}. {contents}".strip(". ").strip()
            review_date = (match.group("date") or "1970-01-01")[:10]
            try:
                rating = int(match.group("rating"))
            except Exception:
                rating = None

            if self.add_review(
                source_website="apps.apple.com",
                source_label=f"Apple App Store ({app_id}, {country})",
                source_url=f"{page_url}&reviewId={review_id}",
                author=author,
                review_date=review_date,
                rating=rating,
                review_text=review_text,
                external_id=f"apple_{app_id}_{country}_{review_id}",
            ):
                added += 1
        return added

    def collect_apple(self):
        print("[collect] Apple App Store reviews")
        start_count = self.source_run_start("apps.apple.com")
        candidates_seen = 0
        latest_candidate_date = None
        for app_id in APPLE_APP_IDS:
            for country in APPLE_COUNTRIES:
                empty_streak = 0
                for page in range(1, 13):
                    url = f"https://itunes.apple.com/{country}/rss/customerreviews/page={page}/id={app_id}/sortby=mostrecent/json"
                    try:
                        resp = self.apple_get(url)
                        if not resp or resp.status_code == 400:
                            break
                        if resp.status_code != 200:
                            empty_streak += 1
                            if empty_streak >= 2:
                                break
                            continue
                        payload = resp.json()
                    except Exception:
                        empty_streak += 1
                        if empty_streak >= 2:
                            break
                        continue

                    entries = payload.get("feed", {}).get("entry", [])
                    if isinstance(entries, dict):
                        entries = [entries]

                    if len(entries) <= 1:
                        empty_streak += 1
                        if empty_streak >= 2:
                            break
                        continue

                    empty_streak = 0
                    review_entries = entries[1:] if len(entries) > 1 else entries
                    page_oldest_date = None
                    for e in review_entries:
                        title = (e.get("title") or {}).get("label") or ""
                        text = (e.get("content") or {}).get("label") or ""
                        review_id = (e.get("id") or {}).get("label") or ""
                        rating_raw = (e.get("im:rating") or {}).get("label")
                        try:
                            rating = int(rating_raw)
                        except Exception:
                            rating = None

                        link_attrs = ((e.get("link") or {}).get("attributes")) or {}
                        review_url = link_attrs.get("href") or f"https://apps.apple.com/{country}/app/id{app_id}"
                        if review_id and "reviewid=" not in review_url.lower():
                            sep = "&" if "?" in review_url else "?"
                            review_url = f"{review_url}{sep}reviewId={review_id}"
                        author = ((e.get("author") or {}).get("name") or {}).get("label") or "Apple user"
                        updated = (e.get("updated") or {}).get("label") or "1970-01-01"
                        review_date = updated[:10]
                        candidates_seen += 1
                        if review_date != "1970-01-01" and (latest_candidate_date is None or review_date > latest_candidate_date):
                            latest_candidate_date = review_date
                        if page_oldest_date is None or review_date < page_oldest_date:
                            page_oldest_date = review_date

                        external_id = f"apple_{app_id}_{country}_{review_id}" if review_id else review_url
                        self.add_review(
                            source_website="apps.apple.com",
                            source_label=f"Apple App Store ({app_id}, {country})",
                            source_url=review_url,
                            author=author,
                            review_date=review_date,
                            rating=rating,
                            review_text=self.normalize_text(f"{title}. {text}"),
                            external_id=external_id,
                        )
                    if page_oldest_date and page_oldest_date < self.since:
                        break
                added = self.collect_apple_html_reviews(app_id, country)
                if added:
                    print(f"  - HTML supplement {app_id} {country}: +{added}")

        self.source_run_finish(
            "apps.apple.com",
            start_count,
            candidates=candidates_seen,
            latest_date=latest_candidate_date,
            note="Apple RSS can be sparse for some app IDs; HTML supplement captures visible App Store review cards only.",
        )

                    
    def collect_youtube_comments(self):
        print("[collect] YouTube comments: skipped (text-only mode)")

    def collect_reddit_pullpush(self):
        print("[collect] Reddit (PullPush submissions and body-only comments)")
        deadline = time.monotonic() + self.reddit_time_budget
        reddit_floor_date = self.source_floor_date("reddit.com", overlap_days=45)
        reddit_since_ts = int(datetime(reddit_floor_date.year, reddit_floor_date.month, reddit_floor_date.day, tzinfo=timezone.utc).timestamp())

        def time_remaining() -> bool:
            return time.monotonic() < deadline

        def deadline_reached() -> bool:
            if time_remaining():
                return False
            print(f"  - PullPush time budget reached for {DISPLAY_NAME}; keeping reviews collected so far.")
            return True

        def parse_ts(ts):
            try:
                return datetime.fromtimestamp(float(ts), tz=timezone.utc).date().isoformat()
            except Exception:
                return "1970-01-01"

        def fetch(endpoint: str, q: str, page_limit: int):
            before = None
            for page in range(page_limit):
                if deadline_reached():
                    return
                params = {
                    "q": q,
                    "size": 100,
                    "sort": "desc",
                    "sort_type": "created_utc",
                }
                if before is not None:
                    params["before"] = before

                url = f"https://api.pullpush.io/reddit/search/{endpoint}/"
                try:
                    resp = S.get(url, params=params, timeout=20)
                    if resp.status_code != 200:
                        time.sleep(0.4)
                        continue
                    payload = resp.json()
                except Exception:
                    time.sleep(0.4)
                    continue

                data = payload.get("data", [])
                if not data:
                    break

                min_ts = None
                reached_since_boundary = False
                for row in data:
                    source_label = f"Reddit r/{row.get('subreddit','unknown')}"
                    if endpoint == "comment":
                        body = self.normalize_text(row.get("body"))
                        if not body or body in {"[deleted]", "[removed]"}:
                            continue
                        if not self.is_reddit_comment_review_candidate(body, source_label, row.get("permalink") or ""):
                            continue
                        text = body
                        rid = f"c_{row.get('id','')}"
                    else:
                        title = self.normalize_text(row.get("title"))
                        selftext = self.normalize_text(row.get("selftext"))
                        text = self.normalize_text(f"{title} {selftext}")
                        if not text or text in {"[deleted]", "[removed]"}:
                            continue
                        rid = f"s_{row.get('id','')}"

                    if not self.mentions_company(f" {text} {row.get('subreddit','')} {row.get('url','')} "):
                        continue

                    permalink = row.get("permalink") or ""
                    if permalink.startswith("/"):
                        full_url = f"https://www.reddit.com{permalink}"
                    else:
                        full_url = row.get("url") or "https://www.reddit.com"

                    created_utc_raw = row.get("created_utc")
                    try:
                        created_utc = float(created_utc_raw)
                    except Exception:
                        created_utc = None

                    if created_utc is not None:
                        if min_ts is None or created_utc < min_ts:
                            min_ts = created_utc
                        if created_utc < reddit_since_ts:
                            reached_since_boundary = True

                    self.add_review(
                        source_website="reddit.com",
                        source_label=source_label,
                        source_url=full_url,
                        author=row.get("author") or "reddit_user",
                        review_date=parse_ts(created_utc if created_utc is not None else created_utc_raw),
                        rating=None,
                        review_text=text,
                        external_id=rid,
                    )

                if page % 10 == 0:
                    print(f"  - {endpoint} page {page + 1}: {len(self.records)} collected")

                if min_ts is None:
                    break
                before = int(min_ts) - 1
                if reached_since_boundary or before < reddit_since_ts:
                    break

                time.sleep(0.15)

        def fetch_subreddit(endpoint: str, subreddit: str, page_limit: int):
            before = None
            for page in range(page_limit):
                if deadline_reached():
                    return
                params = {
                    "subreddit": subreddit,
                    "size": 100,
                    "sort": "desc",
                    "sort_type": "created_utc",
                }
                if before is not None:
                    params["before"] = before

                url = f"https://api.pullpush.io/reddit/search/{endpoint}/"
                try:
                    resp = S.get(url, params=params, timeout=20)
                    if resp.status_code != 200:
                        time.sleep(0.4)
                        continue
                    payload = resp.json()
                except Exception:
                    time.sleep(0.4)
                    continue

                data = payload.get("data", [])
                if not data:
                    break

                min_ts = None
                reached_since_boundary = False
                for row in data:
                    source_label = f"Reddit r/{subreddit}"
                    if endpoint == "comment":
                        body = self.normalize_text(row.get("body"))
                        if not body or body in {"[deleted]", "[removed]"}:
                            continue
                        if not self.is_reddit_comment_review_candidate(body, source_label, row.get("permalink") or ""):
                            continue
                        text = body
                        rid = f"c_{row.get('id','')}"
                    else:
                        title = self.normalize_text(row.get("title"))
                        selftext = self.normalize_text(row.get("selftext"))
                        text = self.normalize_text(f"{title} {selftext}")
                        if not text or text in {"[deleted]", "[removed]"}:
                            continue
                        rid = f"s_{row.get('id','')}"

                    permalink = row.get("permalink") or ""
                    if permalink.startswith("/"):
                        full_url = f"https://www.reddit.com{permalink}"
                    else:
                        full_url = row.get("url") or "https://www.reddit.com"

                    created_utc_raw = row.get("created_utc")
                    try:
                        created_utc = float(created_utc_raw)
                    except Exception:
                        created_utc = None

                    if created_utc is not None:
                        if min_ts is None or created_utc < min_ts:
                            min_ts = created_utc
                        if created_utc < reddit_since_ts:
                            reached_since_boundary = True

                    self.add_review(
                        source_website="reddit.com",
                        source_label=source_label,
                        source_url=full_url,
                        author=row.get("author") or "reddit_user",
                        review_date=parse_ts(created_utc if created_utc is not None else created_utc_raw),
                        rating=None,
                        review_text=text,
                        external_id=rid,
                    )

                if page % 10 == 0:
                    print(f"  - {endpoint} subreddit r/{subreddit} page {page + 1}: {len(self.records)} collected")

                if min_ts is None:
                    break
                before = int(min_ts) - 1
                if reached_since_boundary or before < reddit_since_ts:
                    break
                time.sleep(0.15)

        for query, comment_limit, submission_limit in REDDIT_QUERIES:
            if deadline_reached():
                return
            fetch("comment", query, page_limit=comment_limit)
            if deadline_reached():
                return
            fetch("submission", query, page_limit=submission_limit)

        for subreddit in REDDIT_SUBREDDITS:
            if deadline_reached():
                return
            fetch_subreddit("comment", subreddit, page_limit=220)
            if deadline_reached():
                return
            fetch_subreddit("submission", subreddit, page_limit=140)

    @staticmethod
    def _reddit_is_json_response(resp: requests.Response | None) -> bool:
        if resp is None:
            return False
        content_type = (resp.headers.get("Content-Type") or "").lower()
        text = (resp.text or "").lstrip()
        return "application/json" in content_type or text.startswith("{") or text.startswith("[")

    @staticmethod
    def _reddit_is_verification_page(text: str) -> bool:
        lowered = str(text or "").lower()
        return (
            "please wait for verification" in lowered
            or "you've been blocked by network security" in lowered
            or "js_challenge" in lowered
        )

    @staticmethod
    def _reddit_challenge_seed(text: str) -> str:
        patterns = [
            r'await\(async e=>e\+e\)\("([0-9a-f]+)"\)',
            r'\)\("([0-9a-f]{8,})"\)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text or "")
            if match:
                return match.group(1)
        return ""

    def _reddit_bootstrap_subreddits(self) -> list[str]:
        ordered = []
        for subreddit in REDDIT_SUBREDDITS + ["help", "AskReddit"]:
            clean = str(subreddit or "").strip()
            if not clean:
                continue
            if clean.lower() in {item.lower() for item in ordered}:
                continue
            ordered.append(clean)
        return ordered[:6]

    def _close_reddit_browser(self):
        for attr in ("reddit_browser_page", "reddit_browser_context", "reddit_browser"):
            handle = getattr(self, attr, None)
            if handle is None:
                continue
            try:
                handle.close()
            except Exception:
                pass
            setattr(self, attr, None)
        if self.reddit_playwright is not None:
            try:
                self.reddit_playwright.stop()
            except Exception:
                pass
            self.reddit_playwright = None
        self.reddit_browser_ready = False

    def _sync_reddit_browser_cookies(self):
        if not self.reddit_browser_context:
            return
        try:
            cookies = self.reddit_browser_context.cookies()
        except Exception:
            return
        for cookie in cookies:
            name = cookie.get("name")
            value = cookie.get("value")
            if not name or value is None:
                continue
            S.cookies.set(
                name,
                value,
                domain=cookie.get("domain"),
                path=cookie.get("path") or "/",
            )

    def reddit_browser_fetch_text(self, url: str, params: dict | None = None):
        if not self.reddit_browser_page:
            return None

        try:
            result = self.reddit_browser_page.evaluate(
                """async ({ url, params }) => {
                    const target = new URL(url);
                    Object.entries(params || {}).forEach(([key, value]) => {
                        if (value === undefined || value === null || value === "") return;
                        target.searchParams.set(key, String(value));
                    });
                    const response = await fetch(target.toString(), {
                        credentials: "include",
                        headers: {
                            "Accept": "application/json,text/plain,*/*",
                            "X-Requested-With": "XMLHttpRequest"
                        }
                    });
                    return {
                        ok: response.ok,
                        status: response.status,
                        contentType: response.headers.get("content-type") || "",
                        text: await response.text()
                    };
                }""",
                {"url": url, "params": params or {}},
            )
        except Exception:
            return None

        self._sync_reddit_browser_cookies()
        if not isinstance(result, dict):
            return None
        return result

    def reddit_browser_json_get(self, url: str, params: dict | None = None):
        result = self.reddit_browser_fetch_text(url, params)
        if not isinstance(result, dict):
            return None
        text = str(result.get("text") or "")
        content_type = str(result.get("contentType") or "").lower()
        if "application/json" not in content_type and not text.lstrip().startswith(("{", "[")):
            return None
        try:
            return json.loads(text)
        except Exception:
            return None

    def ensure_reddit_verified_via_browser(self, subreddit: str, probe_url: str, probe_params: dict) -> bool:
        if sync_playwright is None:
            return False
        if self.reddit_browser_ready:
            return True

        self.reddit_browser_attempted = True
        self._close_reddit_browser()
        print(f"  - Trying browser-assisted Reddit verification via r/{subreddit}")

        try:
            self.reddit_playwright = sync_playwright().start()
            self.reddit_browser = self.reddit_playwright.chromium.launch(
                headless=True,
                args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
            )
            self.reddit_browser_context = self.reddit_browser.new_context(
                user_agent=S.headers.get("User-Agent"),
                locale="en-US",
                extra_http_headers={"Accept-Language": S.headers.get("Accept-Language", "en-US,en;q=0.9")},
            )
            self.reddit_browser_page = self.reddit_browser_context.new_page()
            self.reddit_browser_page.goto(
                f"https://www.reddit.com/r/{subreddit}/new/",
                wait_until="domcontentloaded",
                timeout=60000,
            )

            for _ in range(30):
                self.reddit_browser_page.wait_for_timeout(1000)
                result = self.reddit_browser_fetch_text(probe_url, probe_params)
                text = str((result or {}).get("text") or "")
                if result and str(result.get("contentType") or "").lower().find("application/json") >= 0:
                    self.reddit_browser_ready = True
                    return True
                if result and text.lstrip().startswith(("{", "[")):
                    self.reddit_browser_ready = True
                    return True
                if result and not self._reddit_is_verification_page(text):
                    break
        except Exception:
            self._close_reddit_browser()
            return False

        self._close_reddit_browser()
        return False

    def ensure_reddit_verified(self, force: bool = False) -> bool:
        if self.reddit_verified and not force:
            return True
        if self.reddit_verification_attempted and not force:
            return self.reddit_verified

        self.reddit_verification_attempted = True
        print("[collect] Reddit session verification")

        for subreddit in self._reddit_bootstrap_subreddits():
            probe_url = f"https://www.reddit.com/r/{subreddit}/new.json"
            probe_params = {"raw_json": 1, "limit": 1}
            html_url = f"https://www.reddit.com/r/{subreddit}/new/"
            try:
                probe = S.get(probe_url, params=probe_params, timeout=45)
            except Exception:
                continue

            if self._reddit_is_json_response(probe):
                self.reddit_verified = True
                print(f"  - Reddit session already open via r/{subreddit}")
                return True

            html = probe.text or ""
            if not self._reddit_is_verification_page(html):
                try:
                    html_resp = S.get(html_url, timeout=45)
                    html = html_resp.text or ""
                except Exception:
                    html = ""

            if not self._reddit_is_verification_page(html):
                continue

            action_match = re.search(r'<form hidden method="GET" action="([^"]+)"', html)
            token_match = re.search(r'name="token" value="([^"]+)"', html)
            seed = self._reddit_challenge_seed(html)
            if not action_match or not token_match or not seed:
                continue

            verify_url = urljoin("https://www.reddit.com", action_match.group(1))
            verify_params = {
                "solution": f"{seed}{seed}",
                "js_challenge": "1",
                "token": token_match.group(1),
            }

            try:
                S.get(verify_url, params=verify_params, timeout=45)
                probe = S.get(probe_url, params=probe_params, timeout=45)
                if self._reddit_is_json_response(probe):
                    self.reddit_verified = True
                    print(f"  - Reddit session verified via r/{subreddit}")
                    return True
            except Exception:
                continue

            if self.ensure_reddit_verified_via_browser(subreddit, probe_url, probe_params):
                self.reddit_verified = True
                print(f"  - Reddit session verified in browser via r/{subreddit}")
                return True

        print("  - Reddit session verification failed")
        return False

    def reddit_json_get(self, url: str, params: dict | None = None):
        query = dict(params or {})
        query.setdefault("raw_json", 1)
        if not self.ensure_reddit_verified():
            return None

        for attempt in range(2):
            try:
                resp = S.get(url, params=query, timeout=45)
            except Exception:
                resp = None

            if resp is not None and resp.status_code == 200 and not self._reddit_is_verification_page(resp.text or ""):
                try:
                    return resp.json()
                except Exception:
                    break

            if attempt == 0 and self.ensure_reddit_verified(force=True):
                continue

        browser_payload = self.reddit_browser_json_get(url, query)
        if browser_payload is not None:
            return browser_payload
        return None

    @staticmethod
    def _reddit_children(payload):
        return (payload or {}).get("data", {}).get("children", []) or []

    @staticmethod
    def _reddit_after(payload):
        return (payload or {}).get("data", {}).get("after")

    @staticmethod
    def _reddit_date(created_utc):
        try:
            return datetime.fromtimestamp(float(created_utc), tz=timezone.utc).date()
        except Exception:
            return None

    def _reddit_comment_walk(self, children):
        for child in children or []:
            if not isinstance(child, dict):
                continue
            if child.get("kind") != "t1":
                continue
            data = child.get("data") or {}
            yield data
            replies = data.get("replies")
            if isinstance(replies, dict):
                yield from self._reddit_comment_walk((replies.get("data") or {}).get("children") or [])

    def _reddit_add_submission(self, post: dict):
        title = self.normalize_text(post.get("title"))
        selftext = self.normalize_text(post.get("selftext"))
        text = self.normalize_text(f"{title} {selftext}")
        if not text or text in {"[deleted]", "[removed]"}:
            return False

        permalink = post.get("permalink") or ""
        source_url = f"https://www.reddit.com{permalink}" if permalink.startswith("/") else (post.get("url") or "https://www.reddit.com")
        source_label = f"Reddit r/{post.get('subreddit', 'unknown')}"
        created_date = self._reddit_date(post.get("created_utc"))
        if created_date and created_date < self.source_floor_date("reddit.com", overlap_days=45):
            return False

        return self.add_review(
            source_website="reddit.com",
            source_label=source_label,
            source_url=source_url,
            author=post.get("author") or "reddit_user",
            review_date=created_date.isoformat() if created_date else "1970-01-01",
            rating=None,
            review_text=text,
            external_id=f"reddit_json_submission_{post.get('id', '')}",
        )

    def _reddit_add_comments_for_submission(self, post: dict):
        post_id = str(post.get("id") or "").strip()
        if not post_id:
            return 0

        permalink = post.get("permalink") or ""
        if permalink.startswith("/"):
            comments_url = f"https://www.reddit.com{permalink}.json"
        else:
            comments_url = f"https://www.reddit.com/comments/{post_id}.json"

        payload = self.reddit_json_get(comments_url, {"sort": "new", "limit": 500})
        if not isinstance(payload, list) or len(payload) < 2:
            return 0

        source_label = f"Reddit r/{post.get('subreddit', 'unknown')}"
        added = 0

        for comment in self._reddit_comment_walk(self._reddit_children(payload[1])):
            body = self.normalize_text(comment.get("body"))
            if not body or body in {"[deleted]", "[removed]"}:
                continue
            if not self.is_reddit_comment_review_candidate(body, source_label, comment.get("permalink") or comments_url):
                continue
            created_date = self._reddit_date(comment.get("created_utc"))
            if created_date and created_date < self.source_floor_date("reddit.com", overlap_days=45):
                continue

            permalink = comment.get("permalink") or ""
            source_url = f"https://www.reddit.com{permalink}" if permalink.startswith("/") else comments_url

            added += int(self.add_review(
                source_website="reddit.com",
                source_label=source_label,
                source_url=source_url,
                author=comment.get("author") or "reddit_user",
                review_date=created_date.isoformat() if created_date else "1970-01-01",
                rating=None,
                review_text=body,
                external_id=f"reddit_json_comment_{comment.get('id', '')}",
            ))

        return added

    def collect_reddit_public_json(self):
        print("[collect] Reddit (public JSON submissions only)")
        if not self.ensure_reddit_verified():
            print("  - Reddit verification unavailable; skipping public JSON backfill")
            return
        reddit_floor_date = self.source_floor_date("reddit.com", overlap_days=45)
        processed_posts = set()

        def process_post(post: dict):
            post_id = str(post.get("id") or "").strip()
            if not post_id or post_id in processed_posts:
                return 0
            created_date = self._reddit_date(post.get("created_utc"))
            if created_date and created_date < reddit_floor_date:
                return -1
            processed_posts.add(post_id)
            return int(self._reddit_add_submission(post))

        def fetch_search(query: str, page_limit: int):
            after = None
            for page in range(page_limit):
                payload = self.reddit_json_get(
                    "https://www.reddit.com/search.json",
                    {
                        "q": query,
                        "sort": "new",
                        "t": "all",
                        "type": "link",
                        "limit": 100,
                        "after": after,
                    },
                )
                children = self._reddit_children(payload)
                if not children:
                    break

                reached_floor = False
                for child in children:
                    if child.get("kind") != "t3":
                        continue
                    result = process_post(child.get("data") or {})
                    if result == -1:
                        reached_floor = True
                        break

                after = self._reddit_after(payload)
                if reached_floor or not after:
                    break
                if page % 3 == 0:
                    print(f"  - Reddit search '{query}' page {page + 1}: {len(self.records)} collected")
                time.sleep(0.2)

        def fetch_subreddit(subreddit: str, page_limit: int):
            after = None
            for page in range(page_limit):
                payload = self.reddit_json_get(
                    f"https://www.reddit.com/r/{subreddit}/new.json",
                    {
                        "limit": 100,
                        "after": after,
                    },
                )
                children = self._reddit_children(payload)
                if not children:
                    break

                reached_floor = False
                for child in children:
                    if child.get("kind") != "t3":
                        continue
                    result = process_post(child.get("data") or {})
                    if result == -1:
                        reached_floor = True
                        break

                after = self._reddit_after(payload)
                if reached_floor or not after:
                    break
                if page % 2 == 0:
                    print(f"  - Reddit subreddit r/{subreddit} page {page + 1}: {len(self.records)} collected")
                time.sleep(0.2)

        for query, _comment_limit, submission_limit in REDDIT_QUERIES:
            fetch_search(query, page_limit=max(2, min(int(submission_limit or 1), 12)))

        for subreddit in REDDIT_SUBREDDITS:
            fetch_subreddit(subreddit, page_limit=12)

    def arctic_shift_json_get(self, url: str, params: dict | None = None):
        for attempt in range(3):
            try:
                resp = S.get(url, params=params or {}, timeout=60)
                if resp.status_code != 200:
                    time.sleep(0.4 + attempt * 0.4)
                    continue
                payload = resp.json()
            except Exception:
                time.sleep(0.4 + attempt * 0.4)
                continue

            if not isinstance(payload, dict):
                return None

            error = str(payload.get("error") or "").strip()
            if error:
                if "timeout" in error.lower():
                    time.sleep(1.2 + attempt * 0.8)
                    continue
                return None

            return payload
        return None

    def _reddit_add_arctic_post(self, post: dict):
        title = self.normalize_text(post.get("title"))
        selftext = self.normalize_text(post.get("selftext"))
        text = self.normalize_text(f"{title} {selftext}")
        if not text or text in {"[deleted]", "[removed]"}:
            return False

        created_date = self._reddit_date(post.get("created_utc"))
        if created_date and created_date < self.source_floor_date("reddit.com", overlap_days=45):
            return False

        subreddit = str(post.get("subreddit") or "unknown").strip() or "unknown"
        permalink = str(post.get("permalink") or "").strip()
        if permalink.startswith("/"):
            source_url = f"https://www.reddit.com{permalink}"
        else:
            source_url = str(post.get("url") or "https://www.reddit.com").strip()

        post_id = str(post.get("id") or "").strip()
        if post_id:
            self.reddit_post_context_cache[post_id] = {
                "subreddit": subreddit,
                "title": title,
                "selftext": selftext,
                "source_url": source_url,
            }

        return self.add_review(
            source_website="reddit.com",
            source_label=f"Reddit r/{subreddit}",
            source_url=source_url,
            author=post.get("author") or "reddit_user",
            review_date=created_date.isoformat() if created_date else "1970-01-01",
            rating=None,
            review_text=text,
            external_id=f"reddit_arctic_post_{post_id}",
        )

    def _reddit_add_arctic_comment(self, comment: dict):
        body = self.normalize_text(comment.get("body"))
        if not body or body in {"[deleted]", "[removed]"}:
            return False

        created_date = self._reddit_date(comment.get("created_utc"))
        if created_date and created_date < self.source_floor_date("reddit.com", overlap_days=45):
            return False

        subreddit = str(comment.get("subreddit") or "unknown").strip() or "unknown"
        permalink = str(comment.get("permalink") or "").strip()
        if permalink.startswith("/"):
            source_url = f"https://www.reddit.com{permalink}"
        else:
            source_url = "https://www.reddit.com"

        source_label = f"Reddit r/{subreddit}"
        if not self.is_reddit_comment_review_candidate(body, source_label, source_url):
            return False

        comment_id = str(comment.get("id") or "").strip()
        return self.add_review(
            source_website="reddit.com",
            source_label=source_label,
            source_url=source_url,
            author=comment.get("author") or "reddit_user",
            review_date=created_date.isoformat() if created_date else "1970-01-01",
            rating=None,
            review_text=body,
            external_id=f"reddit_arctic_comment_{comment_id}",
        )

    def collect_reddit_arctic_shift(self):
        print("[collect] Reddit (Arctic Shift current backfill)")
        deadline = time.monotonic() + self.reddit_time_budget
        floor_date = self.source_floor_date("reddit.com", overlap_days=45)
        floor_ts = int(datetime(floor_date.year, floor_date.month, floor_date.day, tzinfo=timezone.utc).timestamp())

        def time_remaining() -> bool:
            return time.monotonic() < deadline

        def deadline_reached() -> bool:
            if time_remaining():
                return False
            print(f"  - Arctic Shift time budget reached for {DISPLAY_NAME}; keeping reviews collected so far.")
            return True

        dedicated_subreddits = unique_preserve(REDDIT_SUBREDDITS)
        search_subreddits = [
            subreddit
            for subreddit in unique_preserve(REDDIT_SEARCH_SUBREDDITS)
            if subreddit.lower() not in {item.lower() for item in dedicated_subreddits}
        ]
        query_terms = unique_preserve([row[0] for row in REDDIT_QUERIES])[:4]

        def page_posts(base_params: dict, page_limit: int):
            before = None
            for _page in range(max(1, page_limit)):
                if deadline_reached():
                    return
                params = dict(base_params)
                params["limit"] = min(int(params.get("limit") or 50), 100)
                params["sort"] = "desc"
                if before is not None:
                    params["before"] = before
                payload = self.arctic_shift_json_get(
                    "https://arctic-shift.photon-reddit.com/api/posts/search",
                    params=params,
                )
                data = (payload or {}).get("data") or []
                if not data:
                    break

                oldest = None
                for post in data:
                    created_utc = post.get("created_utc")
                    try:
                        created_utc = int(float(created_utc))
                    except Exception:
                        created_utc = None
                    if created_utc is not None:
                        oldest = created_utc if oldest is None else min(oldest, created_utc)
                    self._reddit_add_arctic_post(post)

                if oldest is None or oldest < floor_ts or len(data) < params["limit"]:
                    break
                before = oldest - 1
                time.sleep(0.25)

        def page_comments(base_params: dict, page_limit: int):
            before = None
            for _page in range(max(1, page_limit)):
                if deadline_reached():
                    return
                params = dict(base_params)
                params["limit"] = min(int(params.get("limit") or 50), 100)
                params["sort"] = "desc"
                if before is not None:
                    params["before"] = before
                payload = self.arctic_shift_json_get(
                    "https://arctic-shift.photon-reddit.com/api/comments/search",
                    params=params,
                )
                data = (payload or {}).get("data") or []
                if not data:
                    break

                oldest = None
                for comment in data:
                    created_utc = comment.get("created_utc")
                    try:
                        created_utc = int(float(created_utc))
                    except Exception:
                        created_utc = None
                    if created_utc is not None:
                        oldest = created_utc if oldest is None else min(oldest, created_utc)
                    self._reddit_add_arctic_comment(comment)

                if oldest is None or oldest < floor_ts or len(data) < params["limit"]:
                    break
                before = oldest - 1
                time.sleep(0.25)

        for subreddit in dedicated_subreddits:
            if deadline_reached():
                return
            page_posts(
                {
                    "subreddit": subreddit,
                    "after": floor_date.isoformat(),
                    "limit": 100,
                },
                page_limit=12,
            )
            page_comments(
                {
                    "subreddit": subreddit,
                    "after": floor_date.isoformat(),
                    "limit": 100,
                },
                page_limit=16,
            )

        for subreddit in search_subreddits:
            for query in query_terms:
                if deadline_reached():
                    return
                page_posts(
                    {
                        "subreddit": subreddit,
                        "query": query,
                        "after": floor_date.isoformat(),
                        "limit": 50,
                    },
                    page_limit=6,
                )
                page_comments(
                    {
                        "subreddit": subreddit,
                        "query": query,
                        "after": floor_date.isoformat(),
                        "limit": 50,
                    },
                    page_limit=4,
                )

    def collect_trustpilot(self):
        print("[collect] Trustpilot reviews")
        start_count = self.source_run_start("trustpilot.com")
        candidates_seen = 0
        latest_candidate_date = None

        for slug in TRUSTPILOT_SLUGS:
            page = 1
            max_pages = 700
            while page <= max_pages:
                url = f"https://www.trustpilot.com/review/{slug}"
                if page > 1:
                    url += f"?page={page}"

                try:
                    resp = S.get(url, timeout=45)
                    self.note_source_attempt("trustpilot.com", status_code=resp.status_code, pages=1)
                    if resp.status_code != 200:
                        if self.is_challenge_response(resp.status_code, resp.text):
                            self.note_source_attempt("trustpilot.com", blocked=True, note=f"direct Trustpilot blocked for {slug}")
                            break
                        break
                    html = resp.text
                except Exception:
                    break

                m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html, re.S)
                if not m:
                    if self.is_challenge_response(resp.status_code, html):
                        self.note_source_attempt("trustpilot.com", blocked=True, note=f"direct Trustpilot challenge for {slug}")
                    break

                try:
                    data = json.loads(m.group(1))
                except Exception:
                    break

                pp = data.get("props", {}).get("pageProps", {})
                reviews = pp.get("reviews") or []
                if not reviews:
                    break

                if page == 1:
                    total_reviews = pp.get("businessUnit", {}).get("numberOfReviews") or len(reviews)
                    self.note_source_attempt("trustpilot.com", advertised_total=total_reviews)
                    try:
                        max_pages = min(1400, math.ceil(int(total_reviews) / 20) + 2)
                    except Exception:
                        max_pages = 700

                page_oldest_date = None
                for r in reviews:
                    rid = r.get("id")
                    title = self.normalize_text(r.get("title"))
                    body = self.normalize_text(r.get("text"))
                    review_text = self.normalize_text(f"{title}. {body}")
                    rating = r.get("rating")
                    published = (r.get("dates") or {}).get("publishedDate")
                    normalized_published = self.normalize_date(published)
                    if page_oldest_date is None or normalized_published < page_oldest_date:
                        page_oldest_date = normalized_published
                    if normalized_published != "1970-01-01" and (latest_candidate_date is None or normalized_published > latest_candidate_date):
                        latest_candidate_date = normalized_published
                    consumer = r.get("consumer") or {}
                    author = consumer.get("displayName") or "Trustpilot user"
                    review_url = f"https://www.trustpilot.com/reviews/{rid}" if rid else url

                    candidates_seen += 1
                    self.add_review(
                        source_website="trustpilot.com",
                        source_label=f"Trustpilot ({slug})",
                        source_url=review_url,
                        author=author,
                        review_date=normalized_published,
                        rating=rating,
                        review_text=review_text,
                        external_id=f"tp_{slug}_{rid}",
                    )

                if page % 25 == 0:
                    print(f"  - {slug} page {page}/{max_pages}: {len(self.records)} collected")

                if page_oldest_date and page_oldest_date < self.since:
                    break

                page += 1
                time.sleep(0.08)

            print(f"  - {slug} done at page {page - 1}")

            # Trustpilot often serves a challenge page to non-browser HTTP clients.
            # Reader fallback gives us the current public review markdown when direct
            # JSON is unavailable.
            if page == 1:
                fallback_added = self.collect_trustpilot_reader_slug(slug)
                if fallback_added:
                    print(f"  - reader fallback {slug}: +{fallback_added}")

        self.source_run_finish(
            "trustpilot.com",
            start_count,
            candidates=candidates_seen,
            latest_date=latest_candidate_date,
        )
        print(f"  - Added {len(self.records) - start_count} Trustpilot reviews")

    def collect_trustpilot_reader_slug(self, slug: str) -> int:
        source_start = len(self.records)
        candidates_seen = 0
        latest_candidate_date = None
        seen_page_signatures = set()

        for page in range(1, 80):
            url = f"https://www.trustpilot.com/review/{slug}"
            if page > 1:
                url += f"?page={page}"
            markdown = self.fetch_reader_text(url, "trustpilot.com")
            if not markdown:
                break

            entries = self.parse_trustpilot_reader_reviews(markdown)
            if not entries:
                break

            signature = tuple((entry["url"], entry["date"], entry["text"][:80]) for entry in entries[:8])
            if signature in seen_page_signatures:
                break
            seen_page_signatures.add(signature)

            page_oldest_date = None
            for entry in entries:
                review_date = self.normalize_date(entry["date"])
                candidates_seen += 1
                if page_oldest_date is None or review_date < page_oldest_date:
                    page_oldest_date = review_date
                if review_date != "1970-01-01" and (latest_candidate_date is None or review_date > latest_candidate_date):
                    latest_candidate_date = review_date
                self.add_review(
                    source_website="trustpilot.com",
                    source_label=f"Trustpilot ({slug})",
                    source_url=entry["url"],
                    author="Trustpilot user",
                    review_date=review_date,
                    rating=None,
                    review_text=entry["text"],
                    external_id=f"tp_reader_{slug}_{entry['id']}",
                )

            if page_oldest_date and page_oldest_date < self.since:
                break
            if len(entries) < 8:
                break
            time.sleep(0.12)

        self.note_source_attempt(
            "trustpilot.com",
            candidates=candidates_seen,
            latest_date=latest_candidate_date,
            fallback=True,
        )
        return max(0, len(self.records) - source_start)

    def collect_smartcustomer(self):
        print("[collect] SmartCustomer reviews")
        start_count = self.source_run_start("smartcustomer.com")
        candidates_seen = 0
        latest_candidate_date = None

        if not SMARTCUSTOMER_ROOT:
            return

        url = SMARTCUSTOMER_ROOT
        try:
            resp = S.get(url, timeout=35)
            html = resp.text
            self.note_source_attempt("smartcustomer.com", status_code=resp.status_code, pages=1)
        except Exception:
            return

        soup = BeautifulSoup(html, "html.parser")
        scripts = soup.find_all("script", type="application/ld+json")

        for script in scripts:
            txt = script.get_text(strip=True)
            if "\"review\"" not in txt:
                continue
            try:
                data = json.loads(txt)
            except Exception:
                continue

            reviews = data.get("review") if isinstance(data, dict) else None
            if not isinstance(reviews, list):
                continue

            for r in reviews:
                author = ((r.get("author") or {}).get("name")) or "SmartCustomer user"
                rating = ((r.get("reviewRating") or {}).get("ratingValue"))
                try:
                    rating = float(rating) if rating is not None else None
                except Exception:
                    rating = None
                date_raw = r.get("datePublished") or "1970-01-01"
                review_date = self.normalize_date(date_raw)
                candidates_seen += 1
                if review_date != "1970-01-01" and (latest_candidate_date is None or review_date > latest_candidate_date):
                    latest_candidate_date = review_date
                headline = self.normalize_text(r.get("headline") or "")
                body = self.normalize_text(r.get("reviewBody") or "")
                review_text = self.normalize_text(f"{headline}. {body}")
                review_url = r.get("url") or url

                self.add_review(
                    source_website="smartcustomer.com",
                    source_label="SmartCustomer",
                    source_url=review_url,
                    author=author,
                    review_date=review_date,
                    rating=rating,
                    review_text=review_text,
                    external_id=f"sc_{review_url}",
                )

        self.source_run_finish("smartcustomer.com", start_count, candidates=candidates_seen, latest_date=latest_candidate_date)
        print(f"  - Added {len(self.records) - start_count} SmartCustomer reviews")

    def collect_birdeye(self):
        print("[collect] Birdeye reviews")
        start_count = self.source_run_start("birdeye.com")
        candidates_seen = 0
        latest_candidate_date = None
        advertised_total = None

        if not BIRDEYE_PAGES:
            return

        for page_url in BIRDEYE_PAGES:
            seen_page_signatures = set()
            for page in range(1, 450):
                paged_url = page_url if page == 1 else f"{page_url}{'&' if '?' in page_url else '?'}page={page}"
                try:
                    resp = S.get(paged_url, timeout=35)
                    html = resp.text
                    self.note_source_attempt("birdeye.com", status_code=resp.status_code, pages=1)
                except Exception:
                    break

                soup = BeautifulSoup(html, "html.parser")
                if page == 1:
                    for script in soup.find_all("script", type="application/ld+json"):
                        try:
                            data = json.loads(script.get_text())
                        except Exception:
                            continue
                        candidates = data if isinstance(data, list) else [data]
                        for item in candidates:
                            if isinstance(item, dict):
                                rating = item.get("aggregateRating") or {}
                                if rating.get("reviewCount"):
                                    advertised_total = max(int(advertised_total or 0), int(rating.get("reviewCount")))
                if advertised_total:
                    self.note_source_attempt("birdeye.com", advertised_total=advertised_total)
                blocks = soup.find_all("div", class_=re.compile(r"CustomerReview_clientsReviews"))
                if not blocks:
                    break

                page_signature = []
                page_oldest_date = None
                for idx, block in enumerate(blocks, start=1):
                    text_node = block.find("p")
                    review_text = self.normalize_text(text_node.get_text(" ", strip=True) if text_node else "")
                    if not review_text:
                        continue

                    author = "Birdeye user"
                    author_img = block.find("img", alt=True)
                    if author_img:
                        author = self.normalize_text(re.sub(r"'s profile image$", "", author_img.get("alt") or "")) or author

                    summary_parts = [
                        self.normalize_text(part)
                        for part in block.get_text("|", strip=True).split("|")
                        if self.normalize_text(part)
                    ]
                    review_source = "Birdeye"
                    review_date_raw = ""
                    if "on" in summary_parts:
                        on_index = summary_parts.index("on")
                        if on_index + 1 < len(summary_parts):
                            review_source = summary_parts[on_index + 1]
                        if on_index + 2 < len(summary_parts):
                            review_date_raw = summary_parts[on_index + 2]

                    review_date = self.normalize_relative_date(review_date_raw)
                    candidates_seen += 1
                    if review_date != "1970-01-01":
                        if page_oldest_date is None or review_date < page_oldest_date:
                            page_oldest_date = review_date
                        if latest_candidate_date is None or review_date > latest_candidate_date:
                            latest_candidate_date = review_date

                    external_seed = f"{paged_url}|{author}|{review_date}|{review_text[:160]}"
                    external_id = hashlib.md5(external_seed.encode("utf-8")).hexdigest()[:16]
                    page_signature.append((author[:48], review_date, review_text[:96]))

                    self.add_review(
                        source_website="birdeye.com",
                        source_label=f"Birdeye ({review_source})",
                        source_url=f"{paged_url}#review-{idx}",
                        author=author,
                        review_date=review_date,
                        rating=None,
                        review_text=review_text,
                        external_id=f"birdeye_{external_id}",
                    )

                compact_signature = tuple(page_signature[:8])
                if compact_signature:
                    if compact_signature in seen_page_signatures:
                        break
                    seen_page_signatures.add(compact_signature)

                if page % 20 == 0:
                    print(f"  - {page_url} page {page}: {len(self.records)} collected")

                if page_oldest_date and page_oldest_date < self.since:
                    break

                if len(blocks) < 3:
                    break

        self.source_run_finish(
            "birdeye.com",
            start_count,
            candidates=candidates_seen,
            latest_date=latest_candidate_date,
            advertised_total=advertised_total,
            note="Birdeye advertised totals may include syndicated Google/Birdeye network reviews; accepted rows are visible textual review cards that pass filters.",
        )
        print(f"  - Added {len(self.records) - start_count} Birdeye reviews")

    def collect_reviewsio(self):
        print("[collect] Reviews.io reviews")
        start_count = self.source_run_start("reviews.io")
        candidates_seen = 0
        latest_candidate_date = None
        advertised_total = None

        if not REVIEWSIO_ROOT:
            return

        queue = [REVIEWSIO_ROOT]
        root_prefix = REVIEWSIO_ROOT.rstrip("/")
        seen_pages = set()
        seen_signatures = set()

        while queue and len(seen_pages) < 80:
            url = queue.pop(0).split("#")[0]
            if url in seen_pages or "questions" in url:
                continue
            seen_pages.add(url)

            try:
                resp = S.get(url, timeout=40)
                html = resp.text
                self.note_source_attempt("reviews.io", status_code=resp.status_code, pages=1)
            except Exception:
                continue

            soup = BeautifulSoup(html, "html.parser")
            script = soup.find("script", type="application/ld+json")
            if not script:
                continue

            try:
                data = json.loads(script.get_text())
            except Exception:
                continue

            try:
                advertised_total = (((data.get("aggregateRating") or {}).get("reviewCount")) or advertised_total)
            except Exception:
                pass

            reviews = data.get("review") if isinstance(data, dict) else None
            if not isinstance(reviews, list) or not reviews:
                continue

            signature = tuple(
                (
                    str((row.get("author") or {}).get("name") or ""),
                    str(row.get("datePublished") or ""),
                    self.normalize_text(unescape(str(row.get("reviewBody") or "")))[:80],
                )
                for row in reviews[:8]
            )
            if signature in seen_signatures:
                continue
            seen_signatures.add(signature)

            for idx, row in enumerate(reviews):
                author = self.normalize_text(((row.get("author") or {}).get("name")) or "Reviews.io user")
                rating = ((row.get("reviewRating") or {}).get("ratingValue"))
                try:
                    rating = float(rating) if rating is not None else None
                except Exception:
                    rating = None

                review_date = self.normalize_date(row.get("datePublished") or "1970-01-01")
                headline = self.normalize_text(unescape(str(row.get("name") or row.get("headline") or "")))
                body = self.normalize_text(unescape(str(row.get("reviewBody") or "")))
                review_text = self.normalize_text(f"{headline}. {body}")
                candidates_seen += 1
                if review_date != "1970-01-01" and (latest_candidate_date is None or review_date > latest_candidate_date):
                    latest_candidate_date = review_date

                review_url = row.get("url") or f"{url}#review-{idx + 1}"
                self.add_review(
                    source_website="reviews.io",
                    source_label=f"Reviews.io ({BUSINESS_SETTINGS.get('website_label', DISPLAY_NAME)})",
                    source_url=review_url,
                    author=author,
                    review_date=review_date,
                    rating=rating,
                    review_text=review_text,
                    external_id=f"reviewsio_{review_url}",
                )

            for a in soup.select("a[href]"):
                href = (a.get("href") or "").strip()
                if not href or "questions" in href:
                    continue
                href = requests.compat.urljoin("https://www.reviews.io", href).split("#")[0]
                if not href.startswith(root_prefix):
                    continue
                href = href.split("#")[0]
                if href not in seen_pages and href not in queue:
                    queue.append(href)

        self.source_run_finish(
            "reviews.io",
            start_count,
            candidates=candidates_seen,
            latest_date=latest_candidate_date,
            advertised_total=advertised_total,
        )
        print(f"  - Added {len(self.records) - start_count} Reviews.io reviews")

    def collect_complaintsboard(self):
        print("[collect] ComplaintsBoard reviews")
        start_count = self.source_run_start("complaintsboard.com")
        candidates_seen = 0
        latest_candidate_date = None
        advertised_total = None

        if not COMPLAINTSBOARD_ROOT:
            return

        queue = [COMPLAINTSBOARD_ROOT]
        page_path_prefix = f"{COMPLAINTSBOARD_PATH_TOKEN}/page/"
        seen_pages = set()
        seen_signatures = set()

        while queue and len(seen_pages) < 20:
            url = queue.pop(0).split("#")[0]
            if url in seen_pages:
                continue
            seen_pages.add(url)

            try:
                resp = S.get(url, timeout=45)
                html = resp.text
                self.note_source_attempt("complaintsboard.com", status_code=resp.status_code, pages=1)
            except Exception:
                continue

            soup = BeautifulSoup(html, "html.parser")
            if advertised_total is None:
                for script in soup.find_all("script", type="application/ld+json"):
                    try:
                        data = json.loads(script.get_text())
                    except Exception:
                        continue
                    if isinstance(data, dict):
                        advertised_total = data.get("reviewCount") or data.get("interactionCount") or advertised_total
                if advertised_total is not None:
                    self.note_source_attempt("complaintsboard.com", advertised_total=advertised_total)
            cards = soup.select(".complaint")
            if not cards:
                continue

            page_signature = []
            for card in cards:
                title_node = card.select_one(".complaint-main__header-name")
                body_node = card.select_one(".complaint-main__text[itemprop='reviewBody']")
                author_node = card.select_one(".author-header__name")
                location_node = card.select_one(".author-header__address")
                date_node = card.select_one(".author-header__date[itemprop='datePublished']")
                share_node = card.select_one(".js-share[data-url]")

                title = self.normalize_text(title_node.get_text(" ", strip=True) if title_node else "")
                body = self.normalize_text(body_node.get_text(" ", strip=True) if body_node else "")
                author = self.normalize_text(author_node.get_text(" ", strip=True) if author_node else "ComplaintsBoard user")
                location = self.normalize_text(location_node.get_text(" ", strip=True) if location_node else "")
                location = re.sub(r"^of\s+", "", location, flags=re.I).strip()
                review_date = self.normalize_date(date_node.get_text(" ", strip=True) if date_node else "1970-01-01")
                candidates_seen += 1
                if review_date != "1970-01-01" and (latest_candidate_date is None or review_date > latest_candidate_date):
                    latest_candidate_date = review_date
                country_map = {
                    "US": "United States",
                    "GB": "United Kingdom",
                    "AE": "United Arab Emirates",
                    "CA": "Canada",
                    "AU": "Australia",
                    "NZ": "New Zealand",
                    "IE": "Ireland",
                }
                location_hint = location
                country_match = re.search(r"(?:,\s*|^)([A-Z]{2})$", location)
                if country_match:
                    code = country_match.group(1)
                    if code in country_map:
                        location_hint = f"{location} ({country_map[code]})"

                extras = []
                for row in card.select(".complaint-new__charge-info-row"):
                    raw = self.normalize_text(row.get_text(" ", strip=True))
                    if not raw or raw.lower().startswith("confidential information hidden"):
                        continue
                    extras.append(raw)

                decoded_url = ""
                if share_node and share_node.get("data-url"):
                    decoded_url = unquote(share_node.get("data-url"))
                if decoded_url.startswith("/"):
                    decoded_url = f"https://www.complaintsboard.com{decoded_url}"
                review_url = decoded_url or url
                review_id_match = re.search(r"#c(\d+)", review_url)
                review_id = review_id_match.group(1) if review_id_match else None

                review_text = ". ".join(part for part in [
                    f"Reporter location: {location_hint}" if location_hint else "",
                    title,
                    body,
                    *extras,
                ] if part)

                if title or body:
                    page_signature.append((review_id or review_url, title[:60], review_date))

                self.add_review(
                    source_website="complaintsboard.com",
                    source_label="ComplaintsBoard",
                    source_url=review_url,
                    author=author,
                    review_date=review_date,
                    rating=None,
                    review_text=review_text,
                    external_id=f"complaintsboard_{review_id}" if review_id else review_url,
                )

            signature = tuple(page_signature[:8])
            if signature in seen_signatures:
                continue
            seen_signatures.add(signature)

            for a in soup.select("a[href]"):
                href = (a.get("href") or "").strip()
                if not href or page_path_prefix not in href.lower():
                    continue
                if href.startswith("/"):
                    href = f"https://www.complaintsboard.com{href}"
                href = href.split("#")[0]
                if href not in seen_pages and href not in queue:
                    queue.append(href)

        self.source_run_finish(
            "complaintsboard.com",
            start_count,
            candidates=candidates_seen,
            latest_date=latest_candidate_date,
            advertised_total=advertised_total,
        )
        print(f"  - Added {len(self.records) - start_count} ComplaintsBoard reviews")

    def discover_bbb_profiles(self):
        profiles = set(BBB_FALLBACK_PROFILES)
        if not BBB_SEARCH_TEXT and not BBB_FALLBACK_PROFILES:
            return sorted(profiles)

        try:
            html = S.get(
                "https://www.bbb.org/search",
                params={"find_country": "USA", "find_text": BBB_SEARCH_TEXT, "find_type": "business"},
                timeout=45,
            ).text
            soup = BeautifulSoup(html, "html.parser")
            for a in soup.select("a[href*='/profile/']"):
                href = (a.get("href") or "").strip()
                href_lower = href.lower()
                profile_ok = (
                    any(token in href_lower for token in BBB_PROFILE_TOKENS)
                    if BBB_PROFILE_TOKENS
                    else any(self._term_in_text(term, f" {href_lower} ") for term in COMPANY_TERMS)
                )
                if not href or not profile_ok:
                    continue
                if href.startswith("/"):
                    href = f"https://www.bbb.org{href}"
                href = href.split("?")[0]
                href = href.split("/addressId/")[0].rstrip("/")
                if href:
                    profiles.add(href)
        except Exception:
            pass

        return sorted(profiles)

    def collect_bbb_complaints(self):
        print("[collect] BBB complaints")
        start_count = self.source_run_start("bbb.org")
        candidates_seen = 0
        latest_candidate_date = None

        profiles = self.discover_bbb_profiles()
        for profile in profiles:
            complaints_root = f"{profile.rstrip('/')}/complaints"
            seen_page_signatures = set()
            for page in range(1, 70):
                url = complaints_root if page == 1 else f"{complaints_root}?page={page}"
                try:
                    resp = S.get(url, timeout=45)
                    html = resp.text
                    self.note_source_attempt("bbb.org", status_code=resp.status_code, pages=1)
                except Exception:
                    break

                soup = BeautifulSoup(html, "html.parser")
                cards = soup.select("li.card.bpr-complaint-grid")
                if not cards:
                    if self.is_challenge_response(getattr(resp, "status_code", 0), html):
                        self.note_source_attempt("bbb.org", blocked=True, note=f"direct BBB complaints blocked for {profile}")
                    markdown = self.fetch_reader_text(url, "bbb.org")
                    entries = self.parse_bbb_reader_complaints(markdown)
                    if not entries:
                        break
                    signature = tuple((entry["url"], entry["date"], entry["text"][:80]) for entry in entries[:8])
                    if signature in seen_page_signatures:
                        break
                    seen_page_signatures.add(signature)
                    page_oldest_date = None
                    for idx, entry in enumerate(entries, start=1):
                        review_date = self.normalize_date(entry["date"])
                        candidates_seen += 1
                        if page_oldest_date is None or review_date < page_oldest_date:
                            page_oldest_date = review_date
                        if review_date != "1970-01-01" and (latest_candidate_date is None or review_date > latest_candidate_date):
                            latest_candidate_date = review_date
                        self.add_review(
                            source_website="bbb.org",
                            source_label="BBB Complaints",
                            source_url=entry["url"] or f"{url}#complaint-{idx}",
                            author=entry["author"],
                            review_date=review_date,
                            rating=entry["rating"],
                            review_text=entry["text"],
                            external_id=f"bbb_reader_c_{profile}_{page}_{idx}_{review_date}",
                        )
                    if page_oldest_date and page_oldest_date < self.since:
                        break
                    if len(entries) < 8:
                        break
                    time.sleep(0.12)
                    continue

                for card in cards:
                    cid = (card.get("id") or "").strip()

                    date_node = card.select_one("p.bpr-complaint-date span")
                    date_raw = date_node.get_text(" ", strip=True) if date_node else ""
                    review_date = self.normalize_us_date(date_raw)

                    issue_node = card.select_one("div.bpr-complaint-type span")
                    issue_type = self.normalize_text(issue_node.get_text(" ", strip=True) if issue_node else "")

                    body_node = card.select_one("div.bpr-complaint-body")
                    body = self.normalize_text(body_node.get_text(" ", strip=True) if body_node else "")
                    if not body:
                        continue

                    body = re.split(r"Business response", body, maxsplit=1, flags=re.I)[0].strip()
                    review_text = self.normalize_text(f"{issue_type}. {body}" if issue_type and issue_type.lower() not in body.lower() else body)

                    candidates_seen += 1
                    if review_date != "1970-01-01" and (latest_candidate_date is None or review_date > latest_candidate_date):
                        latest_candidate_date = review_date
                    self.add_review(
                        source_website="bbb.org",
                        source_label="BBB Complaints",
                        source_url=f"{url}#{cid}" if cid else url,
                        author="BBB complainant",
                        review_date=review_date,
                        rating=1,
                        review_text=review_text,
                        external_id=f"bbb_c_{cid}" if cid else None,
                    )

                if page % 10 == 0:
                    print(f"  - complaints {profile} page {page}: {len(self.records)} collected")

                if len(cards) < 10:
                    break

                time.sleep(0.06)

        self.source_run_finish("bbb.org", start_count, candidates=candidates_seen, latest_date=latest_candidate_date)
        print(f"  - Added {len(self.records) - start_count} BBB complaints")

    def collect_bbb_customer_reviews(self):
        print("[collect] BBB customer reviews")
        start_count = self.source_run_start("bbb.org")
        candidates_seen = 0
        latest_candidate_date = None

        profiles = self.discover_bbb_profiles()
        for profile in profiles:
            reviews_root = f"{profile.rstrip('/')}/customer-reviews"
            seen_page_signatures = set()
            for page in range(1, 30):
                url = reviews_root if page == 1 else f"{reviews_root}?page={page}"
                try:
                    resp = S.get(url, timeout=45)
                    html = resp.text
                    self.note_source_attempt("bbb.org", status_code=resp.status_code, pages=1)
                except Exception:
                    break

                soup = BeautifulSoup(html, "html.parser")
                cards = soup.select("li.card.bpr-review")
                if not cards:
                    if self.is_challenge_response(getattr(resp, "status_code", 0), html):
                        self.note_source_attempt("bbb.org", blocked=True, note=f"direct BBB customer reviews blocked for {profile}")
                    markdown = self.fetch_reader_text(url, "bbb.org")
                    entries = self.parse_bbb_reader_customer_reviews(markdown)
                    if not entries:
                        break
                    signature = tuple((entry["author"], entry["date"], entry["text"][:80]) for entry in entries[:8])
                    if signature in seen_page_signatures:
                        break
                    seen_page_signatures.add(signature)
                    page_oldest_date = None
                    for idx, entry in enumerate(entries, start=1):
                        review_date = self.normalize_date(entry["date"])
                        candidates_seen += 1
                        if page_oldest_date is None or review_date < page_oldest_date:
                            page_oldest_date = review_date
                        if review_date != "1970-01-01" and (latest_candidate_date is None or review_date > latest_candidate_date):
                            latest_candidate_date = review_date
                        self.add_review(
                            source_website="bbb.org",
                            source_label="BBB Customer Reviews",
                            source_url=f"{url}#{entry['url_fragment']}",
                            author=entry["author"],
                            review_date=review_date,
                            rating=entry["rating"],
                            review_text=entry["text"],
                            external_id=f"bbb_reader_r_{profile}_{page}_{idx}_{review_date}",
                        )
                    if page_oldest_date and page_oldest_date < self.since:
                        break
                    if len(entries) < 8:
                        break
                    time.sleep(0.12)
                    continue

                for card in cards:
                    cid = (card.get("id") or "").strip()

                    author_node = card.select_one("h3.bpr-review-title")
                    author_raw = self.normalize_text(author_node.get_text(" ", strip=True) if author_node else "")
                    author = re.sub(r"^Review from\s+", "", author_raw, flags=re.I) or "BBB customer"

                    date_node = card.select_one("p.bds-body")
                    date_raw = date_node.get_text(" ", strip=True) if date_node else ""
                    review_date = self.normalize_us_date(date_raw)

                    rating = None
                    rating_text = self.normalize_text(card.get_text(" ", strip=True))
                    m_rating = re.search(r"(\d+(?:\.\d+)?)\s*star", rating_text, re.I)
                    if m_rating:
                        try:
                            rating = float(m_rating.group(1))
                        except Exception:
                            rating = None

                    body = ""
                    for child in card.find_all("div", recursive=False):
                        classes = child.get("class") or []
                        if "bpr-review-business-response-grid" in classes:
                            continue
                        candidate = self.normalize_text(child.get_text(" ", strip=True))
                        if not candidate:
                            continue
                        if re.fullmatch(r"\d+(?:\.\d+)?\s*star[s]?", candidate, flags=re.I):
                            continue
                        body = candidate
                        break

                    if not body:
                        body = rating_text

                    candidates_seen += 1
                    if review_date != "1970-01-01" and (latest_candidate_date is None or review_date > latest_candidate_date):
                        latest_candidate_date = review_date
                    self.add_review(
                        source_website="bbb.org",
                        source_label="BBB Customer Reviews",
                        source_url=f"{url}#{cid}" if cid else url,
                        author=author,
                        review_date=review_date,
                        rating=rating,
                        review_text=body,
                        external_id=f"bbb_r_{cid}" if cid else None,
                    )

                if page % 8 == 0:
                    print(f"  - customer reviews {profile} page {page}: {len(self.records)} collected")

                if len(cards) < 10:
                    break

                time.sleep(0.06)

        self.source_run_finish("bbb.org", start_count, candidates=candidates_seen, latest_date=latest_candidate_date)
        print(f"  - Added {len(self.records) - start_count} BBB customer reviews")

    def collect_ripoffreport(self):
        print("[collect] Ripoff Report")
        start_count = len(self.records)

        if not RIPOFF_SEARCH_URL:
            return

        report_urls = set()
        for page in range(1, 16):
            url = RIPOFF_SEARCH_URL if page == 1 else f"{RIPOFF_SEARCH_URL}?&pg={page}"
            try:
                html = S.get(url, timeout=45).text
            except Exception:
                break

            soup = BeautifulSoup(html, "html.parser")
            links_found = 0
            for a in soup.select("a[href]"):
                href = (a.get("href") or "").strip()
                if not href or not href.startswith("/report/"):
                    continue
                full_url = f"https://www.ripoffreport.com{href}"
                if not self.mentions_company(full_url.lower()):
                    continue
                report_urls.add(full_url)
                links_found += 1

            if links_found == 0 and page > 2:
                break

            time.sleep(0.08)

        for idx, report_url in enumerate(sorted(report_urls), start=1):
            try:
                html = S.get(report_url, timeout=45).text
            except Exception:
                continue

            soup = BeautifulSoup(html, "html.parser")
            title = self.normalize_text(soup.title.get_text(" ", strip=True) if soup.title else "")
            body_node = soup.select_one(".report-body")
            body = self.normalize_text(body_node.get_text(" ", strip=True) if body_node else "")
            if not body:
                continue

            body = re.sub(r"^.*?Click here now\.\.\s*", "", body, flags=re.I)
            body = re.sub(r"\s+", " ", body).strip()
            if not self.mentions_company(f"{title} {body}".lower()):
                continue

            time_node = soup.select_one("time[datetime]")
            date_raw = (time_node.get("datetime") if time_node else "") or "1970-01-01"
            review_text = self.normalize_text(f"{title}. {body[:3500]}")
            external_id = report_url.rstrip("/").split("/")[-1]

            self.add_review(
                source_website="ripoffreport.com",
                source_label="Ripoff Report",
                source_url=report_url,
                author="Ripoff Report user",
                review_date=date_raw,
                rating=1,
                review_text=review_text,
                external_id=f"rr_{external_id}",
            )

            if idx % 10 == 0:
                print(f"  - reports parsed {idx}/{len(report_urls)}: {len(self.records)} collected")

            time.sleep(0.06)

        print(f"  - Added {len(self.records) - start_count} Ripoff Report entries")

    def finalize(self):
        if self.target > 0 and len(self.records) < self.target:
            self._close_reddit_browser()
            raise RuntimeError(f"Collected {len(self.records)} reviews, below target {self.target}")

        # Keep newest first and cap payload size for browser performance.
        self.records.sort(key=lambda r: (r["review_date"], r["source_website"]), reverse=True)
        self.records = self.records[: self.max_output]

        rows = []
        next_id = 1
        used_ids = set()
        for record in self.records:
            existing_id = str(record.get("id") or "").strip()
            if re.fullmatch(r"rvw-(\d{6})", existing_id):
                used_ids.add(existing_id)
                next_id = max(next_id, int(existing_id.split("-")[1]) + 1)

        for record in self.records:
            row = dict(record)
            existing_id = str(row.get("id") or "").strip()
            if existing_id and existing_id not in used_ids:
                used_ids.add(existing_id)
                row["id"] = existing_id
            elif existing_id and existing_id in used_ids:
                row["id"] = existing_id
            else:
                while f"rvw-{next_id:06d}" in used_ids:
                    next_id += 1
                row["id"] = f"rvw-{next_id:06d}"
                used_ids.add(row["id"])
                next_id += 1
            rows.append(row)

        source_counts = Counter(r["source_website"] for r in rows)
        sentiment_counts = Counter(r["sentiment"] for r in rows)
        source_health_audit = self.build_source_health_audit(source_counts, rows)

        unique_source_urls = []
        seen_urls = set()
        for row in rows:
            u = row["source_url"]
            if u not in seen_urls:
                seen_urls.add(u)
                unique_source_urls.append(u)

        geo_validation_counts = Counter()
        geo_excluded_counts = Counter()
        geo_excluded_examples = []
        active_collectors = list(getattr(self, "active_collectors", []))
        if getattr(self, "only_collector", None):
            existing_geo_validation = dict(self.existing_meta.get("geo_validation_counts") or {})
            existing_geo_excluded = dict(self.existing_meta.get("geo_excluded_counts") or {})
            existing_geo_examples = list(self.existing_meta.get("geo_excluded_examples") or [])
            if "google.com" in self.replace_source_websites:
                existing_geo_validation.pop("google_business_us_profile", None)
                existing_geo_excluded = {
                    key: value for key, value in existing_geo_excluded.items()
                    if not str(key).startswith("google.com:")
                }
                existing_geo_examples = [
                    row for row in existing_geo_examples
                    if str(row.get("source_website") or "").lower() != "google.com"
                ]
            geo_validation_counts.update(existing_geo_validation)
            geo_excluded_counts.update(existing_geo_excluded)
            geo_excluded_examples.extend(existing_geo_examples)
            active_collectors = unique_preserve(
                list(self.existing_meta.get("active_collectors") or []) + active_collectors
            )
        geo_validation_counts.update(self.geo_validation_counts)
        geo_excluded_counts.update(self.geo_excluded_counts)
        geo_excluded_examples.extend(self.geo_excluded_examples)

        payload = {
            "meta": {
                "description": f"Large-scale English-only {DISPLAY_NAME} textual review/problem dataset from public web sources (recency-first).",
                "review_count": len(rows),
                "source_counts": dict(source_counts),
                "source_audit": source_health_audit,
                "sentiments": {
                    "positive": int(sentiment_counts.get("positive", 0)),
                    "negative": int(sentiment_counts.get("negative", 0)),
                },
                "source_urls": unique_source_urls[:300],
                "generated_at_utc": datetime.now(timezone.utc).isoformat(),
                "since_date": self.since,
                "until_date": self.until,
                "collector_failures": self.collector_failures,
                "existing_review_count": self.existing_review_count,
                "new_reviews_added": max(0, len(rows) - self.existing_review_count),
                "youtube_excluded": True,
                "usa_only": True,
                "english_only": True,
                "expected_source_websites": EXPECTED_SOURCE_WEBSITES,
                "required_source_websites": REQUIRED_SOURCE_WEBSITES,
                "geo_validation_counts": dict(geo_validation_counts),
                "geo_excluded_counts": dict(geo_excluded_counts),
                "geo_excluded_examples": geo_excluded_examples[:40],
                "active_collectors": active_collectors,
                "google_business_profiles": self.google_business_profiles,
            },
            "reviews": rows,
        }

        OUTPUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        self._write_csv(rows)
        self._close_reddit_browser()

        print(f"Wrote {OUTPUT_JSON}")
        print(f"Wrote {OUTPUT_CSV}")
        print(f"Review count: {len(rows)}")
        print(f"Sentiments: {payload['meta']['sentiments']}")
        print(f"Sources: {payload['meta']['source_counts']}")

    def _write_csv(self, rows):
        cols = [
            "id",
            "source_website",
            "source_label",
            "source_url",
            "geo_validation",
            "author",
            "review_date",
            "rating",
            "sentiment",
            "review_text",
            "tier1",
            "tier2",
            "tier3",
        ]
        with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=cols)
            writer.writeheader()
            writer.writerows(rows)

    def run_collectors(self, only_collector: str | None = None):
        self.only_collector = only_collector
        collectors = []
        if GOOGLE_PLAY_APPS:
            collectors.append(("google_play", self.collect_google_play))
        if GOOGLE_BUSINESS_SEARCH_NAMES:
            collectors.append(("google_business", self.collect_google_business))
        if TRUSTPILOT_SLUGS:
            collectors.append(("trustpilot", self.collect_trustpilot))
        if REVIEWSIO_ROOT:
            collectors.append(("reviewsio", self.collect_reviewsio))
        if REDDIT_QUERIES or REDDIT_SUBREDDITS:
            collectors.append(("reddit_pullpush", self.collect_reddit_pullpush))
            collectors.append(("reddit_arctic_shift", self.collect_reddit_arctic_shift))
        if BBB_SEARCH_TEXT or BBB_FALLBACK_PROFILES:
            collectors.extend([
                ("bbb_customer_reviews", self.collect_bbb_customer_reviews),
                ("bbb_complaints", self.collect_bbb_complaints),
            ])
        if RIPOFF_SEARCH_URL:
            collectors.append(("ripoffreport", self.collect_ripoffreport))
        if SMARTCUSTOMER_ROOT:
            collectors.append(("smartcustomer", self.collect_smartcustomer))
        if BIRDEYE_PAGES:
            collectors.append(("birdeye", self.collect_birdeye))
        if COMPLAINTSBOARD_ROOT:
            collectors.append(("complaintsboard", self.collect_complaintsboard))
        if APPLE_APP_IDS:
            collectors.append(("apple", self.collect_apple))
        if only_collector:
            collectors = [(name, fn) for name, fn in collectors if name == only_collector]
            if not collectors:
                raise ValueError(f"Unknown or unavailable collector: {only_collector}")
        self.active_collectors = [name for name, _ in collectors]
        wrapper_health_sources = {
            "reddit_pullpush": "reddit.com",
            "reddit_arctic_shift": "reddit.com",
            "ripoffreport": "ripoffreport.com",
        }
        for name, fn in collectors:
            health_source = wrapper_health_sources.get(name)
            wrapper_start = len(self.records)
            google_snapshot = None
            if name == "google_business":
                google_snapshot = {
                    "records": deepcopy(self.records),
                    "seen": set(self._seen),
                    "profiles": deepcopy(self.google_business_profiles),
                    "source_health": deepcopy(self.source_health),
                    "geo_validation_counts": self.geo_validation_counts.copy(),
                    "geo_excluded_counts": self.geo_excluded_counts.copy(),
                    "geo_excluded_examples": deepcopy(self.geo_excluded_examples),
                }
            if health_source:
                self.note_source_attempt(
                    health_source,
                    note=f"{name} ran; candidate count is not separately tracked for this collector.",
                )
            try:
                fn()
                if health_source:
                    self.note_source_attempt(
                        health_source,
                        added=max(0, len(self.records) - wrapper_start),
                    )
            except Exception as exc:
                failure = {"collector": name, "error": str(exc)}
                if name == "google_business" and google_snapshot is not None:
                    failed_health = deepcopy(self.source_health.get("google.com") or {})
                    can_retain = (
                        int(self.existing_counts_by_source.get("google.com", 0)) > 0
                        and "google.com" not in self.replace_source_websites
                    )
                    if not can_retain:
                        self.collector_failures.append(failure)
                        print(f"[warn] collector failed: {name}: {exc}")
                        raise

                    self.records = google_snapshot["records"]
                    self._seen = google_snapshot["seen"]
                    self.google_business_profiles = google_snapshot["profiles"]
                    self.source_health = google_snapshot["source_health"]
                    self.geo_validation_counts = google_snapshot["geo_validation_counts"]
                    self.geo_excluded_counts = google_snapshot["geo_excluded_counts"]
                    self.geo_excluded_examples = google_snapshot["geo_excluded_examples"]
                    failed_health["source_website"] = "google.com"
                    failed_health["attempted"] = True
                    failed_health["retained_after_failed_refresh"] = True
                    failed_health["new_reviews_added"] = 0
                    prior_google_audit = self.existing_source_audit.get("google.com") or {}
                    last_successful_until = str(
                        prior_google_audit.get("last_successful_refresh_until") or ""
                    ).strip()
                    if not last_successful_until and prior_google_audit.get("status") == "ok":
                        last_successful_until = str(
                            self.existing_meta.get("until_date") or ""
                        ).strip()
                    failed_health["last_successful_refresh_until"] = last_successful_until
                    errors = failed_health.setdefault("errors", [])
                    if str(exc) not in errors:
                        errors.append(str(exc)[:300])
                    notes = failed_health.setdefault("notes", [])
                    retention_note = (
                        "Google refresh failed atomically; the last verified Google rows "
                        "and profile registry were retained."
                    )
                    if retention_note not in notes:
                        notes.append(retention_note)
                    self.source_health["google.com"] = failed_health
                    failure["retained_previous_data"] = True
                self.collector_failures.append(failure)
                if health_source:
                    self.note_source_attempt(health_source, error=str(exc))
                print(f"[warn] collector failed: {name}: {exc}")


def main():
    parser = argparse.ArgumentParser(description=f"Collect and classify {DISPLAY_NAME} reviews")
    parser.add_argument("--company", default=COMPANY_KEY, help="Company key from data/businesses.json")
    parser.add_argument("--config-path", default=str(DEFAULT_CONFIG_PATH), help="Path to businesses config JSON")
    parser.add_argument("--target", type=int, default=TARGET_DEFAULT, help="Minimum number of reviews to collect")
    parser.add_argument("--since", type=str, default=SINCE_DEFAULT, help="Include reviews on/after this date (YYYY-MM-DD)")
    parser.add_argument("--until", type=str, default=None, help="Include reviews on/before this date (YYYY-MM-DD)")
    parser.add_argument("--max-output", type=int, default=MAX_OUTPUT_DEFAULT, help="Maximum number of rows to keep in output")
    parser.add_argument(
        "--reddit-time-budget",
        type=int,
        default=900,
        help="Maximum seconds to spend in each Reddit collector before keeping partial Reddit results.",
    )
    parser.add_argument(
        "--only-collector",
        choices=["google_business"],
        default=None,
        help="Run only the selected collector while preserving all existing rows.",
    )
    parser.add_argument(
        "--google-business-query-limit",
        type=int,
        default=0,
        help="Limit Google profile-discovery queries for diagnostics (0 means all).",
    )
    parser.add_argument(
        "--google-business-location-limit",
        type=int,
        default=0,
        help="Limit Google profiles scraped for diagnostics (0 means all).",
    )
    parser.add_argument(
        "--replace-google-business",
        action="store_true",
        help="Rebuild Google Business Profile rows atomically instead of merging new rows.",
    )
    args = parser.parse_args()

    collector = Collector(
        target=args.target,
        since=args.since,
        until=args.until,
        max_output=args.max_output,
        reddit_time_budget=args.reddit_time_budget,
        google_business_query_limit=args.google_business_query_limit,
        google_business_location_limit=args.google_business_location_limit,
        replace_source_websites=(
            {"google.com"}
            if args.replace_google_business
            and GOOGLE_BUSINESS_SEARCH_NAMES
            and not args.google_business_query_limit
            and not args.google_business_location_limit
            else set()
        ),
    )

    collector.run_collectors(only_collector=args.only_collector)

    collector.finalize()


if __name__ == "__main__":
    main()



