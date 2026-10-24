
import json
from pathlib import Path

from etl.transform.video import transform_video

def main():
    raw_files = sorted(
        Path("data/raw").glob("*.json")
    )

    if not raw_files:
        raise FileNotFoundError(
            "No raw JSON files found"
        )

    raw_path = raw_files[-1]

    with raw_path.open(encoding="utf-8") as f:
        raw_data = json.load(f)

    videos = raw_data["videos"]

    transformed = [
        transform_video(video)
        for video in videos
    ]

    output_dir = Path("data/clean")
    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    output_path = output_dir / (
        raw_path.stem + "_clean.json"
    )

    with output_path.open(
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            transformed,
            f,
            ensure_ascii=False,
            indent=2
        )

    print("Raw videos:", len(videos))
    print("Clean videos:", len(transformed))
    print("Saved:", output_path)

if __name__ == "__main__":
    main()