import csv
import json
import glob
import os

CSV_PATH = "restaurants_north_vietnam.csv"
BATCH_GLOB = "google_batches/batch*.json"

QUALITY = {1: "verified", 0: "MISMATCH - check", 2: "thin data - check"}


def load_batches() -> dict:
    """Load every batch file into a dict keyed by the CSV `name` value."""
    records = {}
    for path in sorted(glob.glob(BATCH_GLOB)):
        for rec in json.load(open(path, encoding="utf-8")):
            records[rec["q"]] = rec
    return records


def merge() -> None:
    rows = list(csv.reader(open(CSV_PATH, encoding="utf-8")))
    header, data = rows[0], rows[1:]
    col = {h: i for i, h in enumerate(header)}

    google = load_batches()
    merged = 0

    for row in data:
        rec = google.get(row[col["name"]])
        if not rec:
            continue
        merged += 1
        row[col["rating"]] = rec["rating"]
        row[col["review_count"]] = rec["n"]
        row[col["google_name"]] = rec["g"]
        row[col["google_address"]] = rec["addr"]
        row[col["match_quality"]] = QUALITY[rec["ok"]]

    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows([header] + data)

    pending = sum(1 for r in data if r[col["match_quality"]] == "pending")
    print(f"Merged {merged} records. {pending} of {len(data)} still pending.")


def list_pending() -> None:
    """Print rows still needing verification, grouped into batches of 10."""
    rows = list(csv.DictReader(open(CSV_PATH, encoding="utf-8")))
    pending = [r for r in rows if r["match_quality"] == "pending"]
    print(f"\n{len(pending)} pending:\n")
    for i in range(0, len(pending), 10):
        print(f"--- batch of 10 ---")
        for r in pending[i:i + 10]:
            print(f"  {r['name']} | {r['location']}")
        print()


if __name__ == "__main__":
    if not os.path.exists(CSV_PATH):
        raise SystemExit(f"Cannot find {CSV_PATH} in the current directory.")
    merge()
    list_pending()
