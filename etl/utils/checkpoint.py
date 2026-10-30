
from datetime import datetime, timezone

from google.cloud import bigquery

from config.setting import PROJECT_ID, BQ_LOCATION

def get_existing_video_ids(channel_id):
    client = bigquery.Client(
        project=PROJECT_ID,
        location=BQ_LOCATION
    )

    sql = f"""
        SELECT video_id
        FROM `{PROJECT_ID}.youtube_clean.videos`
        WHERE channel_id = @channel_id
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter(
                "channel_id",
                "STRING",
                channel_id
            )
        ]
    )

    rows = client.query(
        sql,
        job_config=job_config,
        location=BQ_LOCATION
    ).result()

    return {row.video_id for row in rows}


def save_checkpoint(
    channel_id,
    playlist_id,
    last_seen_video_id,
    status="SUCCESS"
):
    client = bigquery.Client(
        project=PROJECT_ID,
        location=BQ_LOCATION
    )

    sql = f"""
    MERGE `{PROJECT_ID}.youtube_raw.pipeline_checkpoints` T
    USING (
      SELECT
        @channel_id AS channel_id,
        @playlist_id AS uploads_playlist_id,
        @last_seen_video_id AS last_seen_video_id,
        @status AS status
    ) S
    ON T.channel_id = S.channel_id

    WHEN MATCHED THEN UPDATE SET
      uploads_playlist_id = S.uploads_playlist_id,
      last_seen_video_id = S.last_seen_video_id,
      status = S.status,
      last_success_at = CURRENT_TIMESTAMP(),
      updated_at = CURRENT_TIMESTAMP()

    WHEN NOT MATCHED THEN INSERT (
      channel_id,
      uploads_playlist_id,
      last_seen_video_id,
      status,
      last_success_at,
      updated_at
    )
    VALUES (
      S.channel_id,
      S.uploads_playlist_id,
      S.last_seen_video_id,
      S.status,
      CURRENT_TIMESTAMP(),
      CURRENT_TIMESTAMP()
    )
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter(
                "channel_id", "STRING", channel_id
            ),
            bigquery.ScalarQueryParameter(
                "playlist_id", "STRING", playlist_id
            ),
            bigquery.ScalarQueryParameter(
                "last_seen_video_id",
                "STRING",
                last_seen_video_id
            ),
            bigquery.ScalarQueryParameter(
                "status", "STRING", status
            )
        ]
    )

    client.query(
        sql,
        job_config=job_config,
        location=BQ_LOCATION
    ).result()
