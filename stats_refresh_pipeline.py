
import argparse
from datetime import datetime, timezone
from uuid import uuid4

from google.cloud import bigquery

from config.setting import PROJECT_ID, CHANNEL_ID
from etl.extract.video_statistics import extract_statistics
from etl.load.video_stats import (
    load_statistics_to_staging,
    merge_statistics_history,
    update_latest_statistics,
)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Number of videos to refresh; 0 means all"
    )

    parser.add_argument(
        "--run-id",
        default=None,
        help="Reuse a run ID when retrying"
    )

    args = parser.parse_args()

    if args.limit < 0:
        parser.error("--limit must be >= 0")

    client = bigquery.Client(project=PROJECT_ID)

    query = f"""
    SELECT DISTINCT video_id
    FROM `{PROJECT_ID}.youtube_clean.videos`
    WHERE channel_id = @channel_id
    ORDER BY video_id
    """

    if args.limit > 0:
        query += f"\nLIMIT {args.limit}"

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter(
                "channel_id", "STRING", CHANNEL_ID
            )
        ]
    )

    rows = client.query(
        query,
        job_config=job_config,
        location="asia-southeast1",
    ).result()

    video_ids = [row.video_id for row in rows]

    if not video_ids:
        print("No videos found")
        return

    print("Refreshing:", len(video_ids), "videos")

    # Generate or reuse the run identifier
    run_id = args.run_id or str(uuid4())

    snapshot_at = datetime.now(timezone.utc)

    statistics = extract_statistics(video_ids)

    returned_ids = {
        item["video_id"] for item in statistics
    }

    missing_ids = set(video_ids) - returned_ids

    if missing_ids:
        raise RuntimeError(
            f"Missing statistics for {len(missing_ids)} videos. "
            f"Sample: {list(missing_ids)[:5]}"
        )

    if len(statistics) != len(returned_ids):
        raise RuntimeError(
            "Duplicate video IDs in API response"
        )

    records = []

    for item in statistics:
        records.append({
            "video_id": item["video_id"],
            "channel_id": CHANNEL_ID,
            "view_count": item["view_count"],
            "like_count": item["like_count"],
            "comment_count": item["comment_count"],
            "snapshot_at": snapshot_at.isoformat(),
            "snapshot_date": snapshot_at.date().isoformat(),
            "run_id": run_id,
        })

    loaded = load_statistics_to_staging(records)

    if loaded != len(records):
        raise RuntimeError(
            "Staging row count mismatch"
        )

    merge_statistics_history()
    update_latest_statistics()

    print("Statistics refresh completed")
    print("Run ID:", run_id)
    print("Videos refreshed:", len(records))


if __name__ == "__main__":
    main()
