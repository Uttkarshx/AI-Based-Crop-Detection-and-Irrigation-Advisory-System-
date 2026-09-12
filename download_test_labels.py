import requests
from pathlib import Path

BASE_URL = "https://data.source.coop/radiantearth/agrifieldnet-competition/test_labels"

OUT_DIR = Path("data/raw/ground_truth/test_labels")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Test labels are named using this pattern.
# We first query the Source Cooperative directory listing.
listing_url = "https://source.coop/radiantearth/agrifieldnet-competition/test_labels"

print("Fetching test-label listing...")

r = requests.get(listing_url, timeout=60)
r.raise_for_status()

text = r.text

# Extract TIFF filenames from page
import re

files = sorted(set(
    re.findall(
        r'ref_agrifieldnet_competition_v1_labels_test_[^"<>\s]+\.tif',
        text
    )
))

print(f"Found {len(files)} TIFF files.")

if not files:
    print("\nNo files found in HTML listing.")
    print("The Source Cooperative page uses dynamic listing.")
    print("We will use the S3 API instead.")
    raise SystemExit

for i, filename in enumerate(files, 1):

    output = OUT_DIR / filename

    if output.exists():
        print(f"[{i}/{len(files)}] SKIP: {filename}")
        continue

    url = f"{BASE_URL}/{filename}"

    print(f"[{i}/{len(files)}] Downloading {filename}")

    response = requests.get(url, timeout=120)
    response.raise_for_status()

    output.write_bytes(response.content)

print("\nDONE.")