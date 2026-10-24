
import json
from pathlib import Path

files = sorted(
    Path("data/raw").glob("*.json")
)

if not files:
    raise FileNotFoundError("No raw JSON found")

with files[-1].open(encoding="utf-8") as f:
    data = json.load(f)

videos = data["video"]
ids = [video["id"] for video in videos]

print("Total videos:", len(videos))
print("Unique IDs:", len(set(ids)))
print("Duplicates:", len(ids) - len(set(ids)))
print(
    "Missing details:",
    len(data["total_video_ids"]) - len(videos)
)
