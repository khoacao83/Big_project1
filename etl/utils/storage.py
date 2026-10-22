import json
from pathlib import Path
from datetime import datetime, timezone

def save_raw_json(data, channel_id):
    raw_dir = Path("data/raw")
    raw_dir.mkdir(parents=True, exist_ok=True)
    timestamp=datetime.now(
        timezone.utc
    ).strftime("%Y%m%dT%H%M%SZ")

    filename=(
        f"{channel_id}_{timestamp}.json"
    )
    file_path=raw_dir/filename

    with open(file_path, "w", encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)

    print(f"Done to save raw data {file_path}")

    return file_path
