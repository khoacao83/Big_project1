
import json
from pathlib import Path
from collections import Counter

raw_files = sorted(
    Path("data/raw").glob("*.json")
)

if not raw_files:
    raise FileNotFoundError("No raw JSON files")

with raw_files[-1].open(
    encoding="utf-8"
) as f:
    data = json.load(f)

videos = data["video"]

video_ids = [
    video.get("id")
    for video in videos
]

id_counts = Counter(video_ids)

duplicate_ids = [
    video_id
    for video_id, count in id_counts.items()
    if count > 1
]

missing_ids = sum(
    not video.get("id")
    for video in videos
)

missing_snippet = sum(
    not video.get("snippet")
    for video in videos
)

missing_statistics = sum(
    not video.get("statistics")
    for video in videos
)

missing_duration = sum(
    not video.get(
        "contentDetails", {}
    ).get("duration")
    for video in videos
)

print("=== DATA QUALITY REPORT ===")
print("Total records:", len(videos))
print("Unique IDs:", len(set(video_ids)))
print("Duplicate IDs:", len(duplicate_ids))
print("Missing IDs:", missing_ids)
print("Missing snippet:", missing_snippet)
print("Missing statistics:", missing_statistics)
print("Missing duration:", missing_duration)

assert missing_ids == 0, "Missing video IDs"
assert len(duplicate_ids) == 0, "Duplicate IDs"

print("Basic ID validation passed")
