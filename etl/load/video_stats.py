
from google.cloud import bigquery

from config.setting import PROJECT_ID

client = bigquery.Client(project=PROJECT_ID)

STAGING = f"{PROJECT_ID}.youtube_raw.staging_video_stats"
HISTORY = f"{PROJECT_ID}.youtube_clean.video_stats_history"
VIDEOS = f"{PROJECT_ID}.youtube_clean.videos"


def load_statistics_to_staging(records):
    job_config = bigquery.LoadJobConfig(
        schema=[
            bigquery.SchemaField("video_id", "STRING"),
            bigquery.SchemaField("channel_id", "STRING"),
            bigquery.SchemaField("view_count", "INT64"),
            bigquery.SchemaField("like_count", "INT64"),
            bigquery.SchemaField("comment_count", "INT64"),
            bigquery.SchemaField("snapshot_at", "TIMESTAMP"),
            bigquery.SchemaField("snapshot_date", "DATE"),
            bigquery.SchemaField("run_id", "STRING"),
        ],
        write_disposition="WRITE_TRUNCATE",
    )

    job = client.load_table_from_json(
        records,
        STAGING,
        job_config=job_config,
        location="asia-southeast1",
    )
    job.result()

    print("Staging rows:", job.output_rows)
    return job.output_rows


def merge_statistics_history():
    sql = f"""
    MERGE `{HISTORY}` T
    USING `{STAGING}` S
    ON T.video_id = S.video_id
       AND T.run_id = S.run_id
       AND T.snapshot_date = S.snapshot_date

    WHEN NOT MATCHED THEN
      INSERT (
        video_id,
        channel_id,
        view_count,
        like_count,
        comment_count,
        snapshot_at,
        snapshot_date,
        run_id
      )
      VALUES (
        S.video_id,
        S.channel_id,
        S.view_count,
        S.like_count,
        S.comment_count,
        S.snapshot_at,
        S.snapshot_date,
        S.run_id
      )
    """

    client.query(sql, location="asia-southeast1").result()
    print("History MERGE completed")


def update_latest_statistics():
    sql = f"""
    MERGE `{VIDEOS}` T
    USING `{STAGING}` S
    ON T.video_id = S.video_id

    WHEN MATCHED AND (
        T.stats_updated_at IS NULL
        OR S.snapshot_at >= T.stats_updated_at
    )
    THEN UPDATE SET
        view_count = S.view_count,
        like_count = S.like_count,
        comment_count = S.comment_count,
        stats_updated_at = S.snapshot_at
    """

    client.query(
        sql,
        location="asia-southeast1"
    ).result()

    print("Latest statistics updated")