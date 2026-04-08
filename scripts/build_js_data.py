import json
from pathlib import Path

base = Path(__file__).resolve().parents[1]
copart_reviews = json.loads((base / 'data' / 'reviews.json').read_text(encoding='utf-8'))
iaa_reviews_path = base / 'data' / 'reviews-iaa.json'
tiers = json.loads((base / 'data' / 'tier-hierarchy.json').read_text(encoding='utf-8'))

if iaa_reviews_path.exists():
    iaa_reviews = json.loads(iaa_reviews_path.read_text(encoding='utf-8'))
else:
    iaa_reviews = {"meta": {"review_count": 0, "source_urls": []}, "reviews": []}

(base / 'data' / 'reviews-data.js').write_text(
    'window.COPART_REVIEWS_DATA = ' + json.dumps(copart_reviews, ensure_ascii=False, indent=2) + ';\n',
    encoding='utf-8'
)
(base / 'data' / 'reviews-data-iaa.js').write_text(
    'window.IAA_REVIEWS_DATA = ' + json.dumps(iaa_reviews, ensure_ascii=False, indent=2) + ';\n',
    encoding='utf-8'
)
(base / 'data' / 'tiers-data.js').write_text(
    'window.COPART_TIERS_DATA = ' + json.dumps(tiers, ensure_ascii=False, indent=2) + ';\n',
    encoding='utf-8'
)
print('Wrote JS data bundles (Copart + IAA).')
