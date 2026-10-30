import json
from pathlib import Path

files = sorted(Path("data/clean").glob("*_clean.json"))

if not files:
    raise FileNotFoundError("No clean Json found")

with files[-1].open(encoding="utf-8") as f:
    videos=json.load(f)

missing_video_ids=sum(not v.get("video_id") for v in videos)
invalid_view=sum( v["view_count"] is not None and v["view_count"]<0 for v in videos)
invalid_duration=sum(v["duration_seconds"] is not None and v["duration_seconds"]<0 for v in videos)
print("Total", len(videos))
print("Missing video IDs", missing_video_ids)
print("Negative views:", invalid_view)
print("Negative duration:", invalid_duration)

assert missing_video_ids==0
assert invalid_view==0
assert invalid_duration==0
