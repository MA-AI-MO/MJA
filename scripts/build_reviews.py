import argparse
import csv
from html import unescape
import json
import math
import re
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote

import requests
from bs4 import BeautifulSoup
from google_play_scraper import Sort, reviews as gp_reviews

try:
    from langdetect import DetectorFactory, detect as detect_lang
    DetectorFactory.seed = 0
except Exception:
    detect_lang = None

BASE_DIR = Path(__file__).resolve().parents[1]
HIERARCHY_PATH = BASE_DIR / "data" / "tier-hierarchy.json"
OUTPUT_JSON = BASE_DIR / "data" / "reviews.json"
OUTPUT_CSV = BASE_DIR / "data" / "reviews.csv"

TARGET_DEFAULT = 0
MAX_OUTPUT_DEFAULT = 120000
SINCE_DEFAULT = "2023-01-01"

GOOGLE_PLAY_APPS = [
    "com.copart.membermobile",
    "com.copart.transportation",
    "com.copart.seller.mobile",
    "com.copart.seller.go",
    "com.copart.quikauction",
]

GOOGLE_PLAY_MARKETS = [
    ("us", "en"),
    ("us", "es"),
    ("us", "fr"),
    ("us", "de"),
    ("us", "pt"),
    ("us", "ru"),
    ("us", "ar"),
    ("us", "it"),
    ("us", "nl"),
    ("us", "tr"),
    ("us", "pl"),
    ("us", "ja"),
    ("us", "ko"),
]

TRUSTPILOT_SLUGS = [
    "copart.co.uk",
    "copart.com",
    "copart.de",
    "copart.ie",
    "copart.es",
    "copart.fr",
    "copart.nl",
    "copart.it",
    "copart.ca",
]
APPLE_APP_IDS = [
    "414275302",   # Copart - Online Auto Auctions
    "1410332198",  # Copart Transportation
    "1461510275",  # Copart GO
    "1480604203",  # Copart - Seller Mobile
    "6474267839",  # QuickAuction
]

APPLE_COUNTRIES = ["us", "gb", "ca", "au", "nz", "ie"]
REVIEWSIO_ROOT = "https://www.reviews.io/company-reviews/store/copart-com-"
COMPLAINTSBOARD_ROOT = "https://www.complaintsboard.com/copart-b120065"

US_GEO_MARKERS = {
    " usa ", " united states ", " us yard ", " us lot ", " us auction ",
    " copart dallas ", " copart houston ", " copart florida ", " copart texas ",
    " copart california ", " copart chicago ", " copart new jersey ", " copart usa ",
    " buying from the us ", " bought from the us ", " shipped from the us ",
    " shipping to the us ", " imported from the us ", " dmv ", " salvage title ",
    " texas ", " dallas ", " houston ", " florida ", " miami ", " california ",
    " los angeles ", " new jersey ", " new york ", " chicago ", " arizona ",
    " nevada ", " georgia ", " north carolina ", " south carolina ", " illinois ",
    " pennsylvania ", " ohio ", " washington state ", " united states yard ",
}
STRONG_US_GEO_MARKERS = {
    " us yard ", " us lot ", " us auction ",
    " copart dallas ", " copart houston ", " copart florida ", " copart texas ",
    " copart california ", " copart chicago ", " copart new jersey ",
    " buying from the us ", " bought from the us ", " purchased from the us ",
    " purchase from the us ", " shipped from the us ", " shipped to the us ",
    " shipping to the us ", " imported from the us ", " imported to the us ",
    " import into the us ", " export to the us ", " exported to the us ",
    " texas ", " dallas ", " houston ", " florida ",
    " miami ", " california ", " los angeles ", " new jersey ", " new york ",
    " chicago ", " arizona ", " nevada ", " north carolina ",
    " south carolina ", " illinois ", " pennsylvania ", " ohio ", " washington state ",
}

NON_US_GEO_MARKERS = {
    " uk ", " copart.co.uk ", " copart uk ", " united kingdom ", " england ", " scotland ",
    " wales ", " northern ireland ", " london ", " bristol ", " manchester ",
    " wolverhampton ", " rochford ", " westbury ", " whitburn ", " dvla ", " mot ", " v5c ",
    " vat ", " biba ", " cat s ", " cat n ", " ireland ", " dublin ", " germany ",
    " berlin ", " france ", " spain ", " netherlands ", " italy ", " canada ",
    " ontario ", " british columbia ", " australia ", " new zealand ", " £", " ł",
}

MIXED_SOURCE_WEBSITES = {"reddit.com", "pissedconsumer.com", "smartcustomer.com", "ripoffreport.com", "complaintsboard.com", "reviews.io"}
EXPECTED_SOURCE_WEBSITES = [
    "play.google.com",
    "apps.apple.com",
    "bbb.org",
    "trustpilot.com",
    "reviews.io",
    "reddit.com",
    "pissedconsumer.com",
    "ripoffreport.com",
    "smartcustomer.com",
    "complaintsboard.com",
]
REQUIRED_SOURCE_WEBSITES = ["play.google.com", "apps.apple.com", "bbb.org"]

BBB_SEARCH_URL = "https://www.bbb.org/search?find_country=USA&find_text=Copart&find_type=business"
BBB_FALLBACK_PROFILES = [
    "https://www.bbb.org/us/tx/dallas/profile/online-car-dealers/copart-inc-0875-90403032",
]

RIPOFF_SEARCH_URL = "https://www.ripoffreport.com/reports/specific_search/copart"

ENGLISH_COMMON_WORDS = {
    "the", "and", "for", "that", "with", "this", "was", "are", "but", "have", "not", "you",
    "they", "from", "been", "had", "all", "their", "there", "would", "could", "should",
    "very", "when", "what", "where", "which", "about", "after", "before", "because", "into",
    "while", "than", "then", "only", "also", "just", "your", "our", "his", "her", "them",
    "will", "cant", "cannot", "did", "didnt", "dont", "does", "doesnt", "too", "more",
    "review", "service", "customer", "auction", "vehicle", "car", "cars", "copart", "fees",
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

COPART_TERMS = {"copart", "coparts", "co part"}
COPART_CONTEXT_TERMS = {
    "auction", "bid", "bidding", "buyer", "seller", "salvage", "lot", "yard", "title",
    "pickup", "delivery", "dispatch", "tow", "storage", "gate pass", "membership",
    "deposit", "fee", "fees", "refund", "payment", "wire", "account", "login", "app",
    "support", "customer service", "representative", "agent", "listing", "vehicle",
}
OFFTOPIC_TERMS = {
    "stock", "share price", "ticker", "cprt", "earnings call", "quarterly earnings",
    "investor", "market cap", "dividend", "trading", "options chain",
}
COPART_EXONERATION_PATTERNS = [
    r"\bnot copart'?s fault\b",
    r"\bnot copart\b",
    r"\bnot their fault\b",
    r"\binsurance(?: company)? fault\b",
    r"\btow (?:company|provider) fault\b",
    r"\bseller'?s fault\b",
]

S = requests.Session()
S.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json,text/plain,*/*",
    "Accept-Language": "en-US,en;q=0.9",
})


class Collector:
    def __init__(self, target: int, since: str, until: str | None, max_output: int):
        self.target = max(0, int(target))
        self.max_output = max(1, int(max_output))
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
        self._build_path_constants()

    def _load_allowed_paths(self):
        payload = json.loads(HIERARCHY_PATH.read_text(encoding="utf-8"))
        return {
            (row["tier1"], row["tier2"], row["tier3"])
            for row in payload["allowed_paths"]
        }

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
            if "copart-com" in url_lower:
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

        if source_website == "trustpilot.com":
            if "(copart.com)" in label_lower:
                if has_non_us_marker and not has_strong_us_marker:
                    return False, "trustpilot_us_slug_non_us_marker"
                return True, "trustpilot_us_slug"
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

    @staticmethod
    def is_copart_subreddit(source_website: str, source_label: str) -> bool:
        if source_website != "reddit.com":
            return False
        lbl = str(source_label or "").lower()
        return any(tag in lbl for tag in {"r/copart", "r/copartonline", "r/copartauctions"})

    def is_copart_relevant(self, source_website: str, source_label: str, text: str) -> bool:
        t = str(text or "").lower()

        if not t:
            return False
        if any(term in t for term in OFFTOPIC_TERMS):
            return False

        has_copart = any(term in t for term in COPART_TERMS)
        has_context = any(term in t for term in COPART_CONTEXT_TERMS)
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
        # is not always present, but review text still needs some operational context.
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
        exonerated = any(re.search(pattern, t) for pattern in COPART_EXONERATION_PATTERNS)

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
        if any(k in t for k in {"recommend", "highly recommend", "great", "excellent", "love copart"}):
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

        key_id = (source_website, str(external_id or ""))
        if key_id[1] and key_id in self._seen:
            return False
        if not key_id[1]:
            key_id = (source_website, f"{author}|{normalized_date}|{txt[:120]}")
            if key_id in self._seen:
                return False

        sentiment = self.infer_sentiment(txt, rating, source_website)
        if sentiment not in {"positive", "negative"}:
            return False

        path = self.classify(txt, sentiment)
        if not path:
            return False
        tier1, tier2, tier3 = path

        self._seen.add(key_id)

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

    def collect_google_play(self):
        print("[collect] Google Play reviews")
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

                    
    def collect_youtube_comments(self):
        print("[collect] YouTube comments: skipped (text-only mode)")

    def collect_reddit_pullpush(self):
        print("[collect] Reddit (PullPush comments/submissions)")

        def parse_ts(ts):
            try:
                return datetime.fromtimestamp(float(ts), tz=timezone.utc).date().isoformat()
            except Exception:
                return "1970-01-01"

        def fetch(endpoint: str, q: str, page_limit: int):
            before = None
            for page in range(page_limit):
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
                    resp = S.get(url, params=params, timeout=45)
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
                    if endpoint == "comment":
                        body = self.normalize_text(row.get("body"))
                        if not body or body in {"[deleted]", "[removed]"}:
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

                    if "copart" not in text.lower():
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
                        if created_utc < self.since_ts:
                            reached_since_boundary = True

                    self.add_review(
                        source_website="reddit.com",
                        source_label=f"Reddit r/{row.get('subreddit','unknown')}",
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
                if reached_since_boundary or before < self.since_ts:
                    break

                time.sleep(0.15)

        def fetch_subreddit(endpoint: str, subreddit: str, page_limit: int):
            before = None
            for page in range(page_limit):
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
                    resp = S.get(url, params=params, timeout=45)
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
                    if endpoint == "comment":
                        body = self.normalize_text(row.get("body"))
                        if not body or body in {"[deleted]", "[removed]"}:
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
                        if created_utc < self.since_ts:
                            reached_since_boundary = True

                    self.add_review(
                        source_website="reddit.com",
                        source_label=f"Reddit r/{subreddit}",
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
                if reached_since_boundary or before < self.since_ts:
                    break
                time.sleep(0.15)

        query_limits = [
            ("copart", 420, 260),
            ("copart auction", 120, 80),
            ("copart app", 120, 80),
            ("copart fees", 120, 80),
            ("copart title", 120, 80),
        ]
        for query, comment_limit, submission_limit in query_limits:
            fetch("comment", query, page_limit=comment_limit)
            fetch("submission", query, page_limit=submission_limit)

        for subreddit in ["copart", "copartonline"]:
            fetch_subreddit("comment", subreddit, page_limit=220)
            fetch_subreddit("submission", subreddit, page_limit=140)


    def collect_trustpilot(self):
        print("[collect] Trustpilot reviews")
        start_count = len(self.records)

        for slug in TRUSTPILOT_SLUGS:
            page = 1
            max_pages = 700
            while page <= max_pages:
                url = f"https://www.trustpilot.com/review/{slug}"
                if page > 1:
                    url += f"?page={page}"

                try:
                    resp = S.get(url, timeout=45)
                    if resp.status_code != 200:
                        break
                    html = resp.text
                except Exception:
                    break

                m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html, re.S)
                if not m:
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
                    consumer = r.get("consumer") or {}
                    author = consumer.get("displayName") or "Trustpilot user"
                    review_url = f"https://www.trustpilot.com/reviews/{rid}" if rid else url

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

        print(f"  - Added {len(self.records) - start_count} Trustpilot reviews")

    def collect_pissedconsumer(self):
        print("[collect] PissedConsumer reviews")
        start_count = len(self.records)

        first_url = "https://copart-auto-auction.pissedconsumer.com/review.html?page=1"
        try:
            html = S.get(first_url, timeout=40).text
        except Exception:
            return

        title_match = re.search(r"(\d+)\s+Copart Auto Auction Reviews", html, re.I)
        total_est = int(title_match.group(1)) if title_match else 350
        max_pages = min(80, math.ceil(total_est / 15) + 5)

        seen_signatures = set()

        for page in range(1, max_pages + 1):
            url = f"https://copart-auto-auction.pissedconsumer.com/review.html?page={page}"
            try:
                html = S.get(url, timeout=40).text
            except Exception:
                continue

            soup = BeautifulSoup(html, "html.parser")
            items = soup.select("div.f-component-item.review-item")
            if not items:
                continue

            page_ids = []
            before_page_count = len(self.records)
            for item in items:
                rid = item.get("data-id")
                if rid:
                    page_ids.append(rid)

                body_node = item.find(attrs={"itemprop": "reviewBody"})
                body = self.normalize_text(body_node.get_text(" ", strip=True) if body_node else "")

                title_node = item.find(["h1", "h2", "h3"])
                title = self.normalize_text(title_node.get_text(" ", strip=True) if title_node else "")

                author_node = item.find(attrs={"itemprop": "author"})
                author = self.normalize_text(author_node.get_text(" ", strip=True) if author_node else "PissedConsumer user")

                date_node = item.find(attrs={"itemprop": "datePublished"})
                if date_node and date_node.get("content"):
                    date_raw = date_node.get("content")
                elif date_node:
                    date_raw = date_node.get_text(" ", strip=True)
                else:
                    date_raw = "1970-01-01"

                rating_node = item.find(attrs={"itemprop": "ratingValue"})
                rating_raw = None
                if rating_node:
                    rating_raw = rating_node.get("content") or rating_node.get_text(" ", strip=True)
                try:
                    rating = float(rating_raw) if rating_raw else None
                except Exception:
                    rating = None

                if title and title.lower() not in body.lower():
                    review_text = f"{title}. {body}" if body else title
                else:
                    review_text = body or title

                self.add_review(
                    source_website="pissedconsumer.com",
                    source_label="PissedConsumer",
                    source_url=f"{url}#review-{rid}" if rid else url,
                    author=author,
                    review_date=date_raw,
                    rating=rating,
                    review_text=review_text,
                    external_id=f"pc_{rid}" if rid else None,
                )

            sig = tuple(page_ids)
            if sig in seen_signatures:
                break
            seen_signatures.add(sig)

            if len(self.records) == before_page_count and page > 5:
                break

            if page % 10 == 0:
                print(f"  - page {page}/{max_pages}: {len(self.records)} collected")

            time.sleep(0.07)

        print(f"  - Added {len(self.records) - start_count} PissedConsumer reviews")

    def collect_smartcustomer(self):
        print("[collect] SmartCustomer reviews")
        start_count = len(self.records)

        url = "https://www.smartcustomer.com/reviews/copart.com"
        try:
            html = S.get(url, timeout=35).text
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
                headline = self.normalize_text(r.get("headline") or "")
                body = self.normalize_text(r.get("reviewBody") or "")
                review_text = self.normalize_text(f"{headline}. {body}")
                review_url = r.get("url") or url

                self.add_review(
                    source_website="smartcustomer.com",
                    source_label="SmartCustomer",
                    source_url=review_url,
                    author=author,
                    review_date=date_raw,
                    rating=rating,
                    review_text=review_text,
                    external_id=f"sc_{review_url}",
                )

        print(f"  - Added {len(self.records) - start_count} SmartCustomer reviews")

    def collect_reviewsio(self):
        print("[collect] Reviews.io reviews")
        start_count = len(self.records)

        queue = [REVIEWSIO_ROOT]
        seen_pages = set()
        seen_signatures = set()

        while queue and len(seen_pages) < 80:
            url = queue.pop(0).split("#")[0]
            if url in seen_pages or "questions" in url:
                continue
            seen_pages.add(url)

            try:
                html = S.get(url, timeout=40).text
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

                review_url = row.get("url") or f"{url}#review-{idx + 1}"
                self.add_review(
                    source_website="reviews.io",
                    source_label="Reviews.io (www.copart.com)",
                    source_url=review_url,
                    author=author,
                    review_date=review_date,
                    rating=rating,
                    review_text=review_text,
                    external_id=f"reviewsio_{review_url}",
                )

            for a in soup.select("a[href]"):
                href = (a.get("href") or "").strip()
                if not href or "company-reviews/store/copart-com-" not in href or "questions" in href:
                    continue
                if href.startswith("/"):
                    href = f"https://www.reviews.io{href}"
                href = href.split("#")[0]
                if href not in seen_pages and href not in queue:
                    queue.append(href)

        print(f"  - Added {len(self.records) - start_count} Reviews.io reviews")

    def collect_complaintsboard(self):
        print("[collect] ComplaintsBoard reviews")
        start_count = len(self.records)

        queue = [COMPLAINTSBOARD_ROOT]
        seen_pages = set()
        seen_signatures = set()

        while queue and len(seen_pages) < 20:
            url = queue.pop(0).split("#")[0]
            if url in seen_pages:
                continue
            seen_pages.add(url)

            try:
                html = S.get(url, timeout=45).text
            except Exception:
                continue

            soup = BeautifulSoup(html, "html.parser")
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
                if not href or "/copart-b120065/page/" not in href:
                    continue
                if href.startswith("/"):
                    href = f"https://www.complaintsboard.com{href}"
                href = href.split("#")[0]
                if href not in seen_pages and href not in queue:
                    queue.append(href)

        print(f"  - Added {len(self.records) - start_count} ComplaintsBoard reviews")

    def discover_bbb_profiles(self):
        profiles = set(BBB_FALLBACK_PROFILES)

        try:
            html = S.get(BBB_SEARCH_URL, timeout=45).text
            soup = BeautifulSoup(html, "html.parser")
            for a in soup.select("a[href*='/profile/']"):
                href = (a.get("href") or "").strip()
                if not href or "copart" not in href.lower():
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
        start_count = len(self.records)

        profiles = self.discover_bbb_profiles()
        for profile in profiles:
            complaints_root = f"{profile.rstrip('/')}/complaints"
            for page in range(1, 70):
                url = complaints_root if page == 1 else f"{complaints_root}?page={page}"
                try:
                    html = S.get(url, timeout=45).text
                except Exception:
                    break

                soup = BeautifulSoup(html, "html.parser")
                cards = soup.select("li.card.bpr-complaint-grid")
                if not cards:
                    break

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

        print(f"  - Added {len(self.records) - start_count} BBB complaints")

    def collect_bbb_customer_reviews(self):
        print("[collect] BBB customer reviews")
        start_count = len(self.records)

        profiles = self.discover_bbb_profiles()
        for profile in profiles:
            reviews_root = f"{profile.rstrip('/')}/customer-reviews"
            for page in range(1, 30):
                url = reviews_root if page == 1 else f"{reviews_root}?page={page}"
                try:
                    html = S.get(url, timeout=45).text
                except Exception:
                    break

                soup = BeautifulSoup(html, "html.parser")
                cards = soup.select("li.card.bpr-review")
                if not cards:
                    break

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

        print(f"  - Added {len(self.records) - start_count} BBB customer reviews")

    def collect_ripoffreport(self):
        print("[collect] Ripoff Report")
        start_count = len(self.records)

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
                if "copart" not in full_url.lower():
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
            if "copart" not in f"{title} {body}".lower():
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
            raise RuntimeError(f"Collected {len(self.records)} reviews, below target {self.target}")

        # Keep newest first and cap payload size for browser performance.
        self.records.sort(key=lambda r: (r["review_date"], r["source_website"]), reverse=True)
        self.records = self.records[: self.max_output]

        rows = []
        for idx, r in enumerate(self.records, start=1):
            rows.append({"id": f"rvw-{idx:06d}", **r})

        source_counts = Counter(r["source_website"] for r in rows)
        sentiment_counts = Counter(r["sentiment"] for r in rows)

        unique_source_urls = []
        seen_urls = set()
        for row in rows:
            u = row["source_url"]
            if u not in seen_urls:
                seen_urls.add(u)
                unique_source_urls.append(u)

        payload = {
            "meta": {
                "description": "Large-scale English-only Copart textual review/problem dataset from public web sources (recency-first).",
                "review_count": len(rows),
                "source_counts": dict(source_counts),
                "source_audit": [
                    {
                        "source_website": source_website,
                        "review_count": int(source_counts.get(source_website, 0)),
                        "present": bool(source_counts.get(source_website, 0)),
                    }
                    for source_website in EXPECTED_SOURCE_WEBSITES
                ],
                "sentiments": {
                    "positive": int(sentiment_counts.get("positive", 0)),
                    "negative": int(sentiment_counts.get("negative", 0)),
                },
                "source_urls": unique_source_urls[:300],
                "generated_at_utc": datetime.now(timezone.utc).isoformat(),
                "since_date": self.since,
                "until_date": self.until,
                "collector_failures": self.collector_failures,
                "youtube_excluded": True,
                "usa_only": True,
                "english_only": True,
                "expected_source_websites": EXPECTED_SOURCE_WEBSITES,
                "required_source_websites": REQUIRED_SOURCE_WEBSITES,
                "geo_validation_counts": dict(self.geo_validation_counts),
                "geo_excluded_counts": dict(self.geo_excluded_counts),
                "geo_excluded_examples": self.geo_excluded_examples,
                "active_collectors": [
                    "google_play",
                    "trustpilot",
                    "reviewsio",
                    "reddit_pullpush",
                    "bbb_customer_reviews",
                    "bbb_complaints",
                    "pissedconsumer",
                    "ripoffreport",
                    "smartcustomer",
                    "complaintsboard",
                    "apple",
                ],
            },
            "reviews": rows,
        }

        OUTPUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        self._write_csv(rows)

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

    def run_collectors(self):
        collectors = [
            ("google_play", self.collect_google_play),
            ("trustpilot", self.collect_trustpilot),
            ("reviewsio", self.collect_reviewsio),
            ("reddit_pullpush", self.collect_reddit_pullpush),
            ("bbb_customer_reviews", self.collect_bbb_customer_reviews),
            ("bbb_complaints", self.collect_bbb_complaints),
            ("pissedconsumer", self.collect_pissedconsumer),
            ("ripoffreport", self.collect_ripoffreport),
            ("smartcustomer", self.collect_smartcustomer),
            ("complaintsboard", self.collect_complaintsboard),
            ("apple", self.collect_apple),
        ]
        for name, fn in collectors:
            try:
                fn()
            except Exception as exc:
                self.collector_failures.append({"collector": name, "error": str(exc)})
                print(f"[warn] collector failed: {name}: {exc}")


def main():
    parser = argparse.ArgumentParser(description="Collect and classify Copart reviews")
    parser.add_argument("--target", type=int, default=TARGET_DEFAULT, help="Minimum number of reviews to collect")
    parser.add_argument("--since", type=str, default=SINCE_DEFAULT, help="Include reviews on/after this date (YYYY-MM-DD)")
    parser.add_argument("--until", type=str, default=None, help="Include reviews on/before this date (YYYY-MM-DD)")
    parser.add_argument("--max-output", type=int, default=MAX_OUTPUT_DEFAULT, help="Maximum number of rows to keep in output")
    args = parser.parse_args()

    collector = Collector(target=args.target, since=args.since, until=args.until, max_output=args.max_output)

    collector.run_collectors()

    collector.finalize()


if __name__ == "__main__":
    main()



