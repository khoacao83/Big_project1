from google.cloud import bigquery
from config.setting import PROJECT_ID, BQ_LOCATION

def merge_staging_to_videos():
    client = bigquery.Client(
        project=PROJECT_ID,
        location=BQ_LOCATION
    )
    sql = f"""
    MERGE `{PROJECT_ID}.youtube_clean.videos` T
    USING `{PROJECT_ID}.youtube_raw.staging_videos` S
    ON T.video_id = S.video_id

    WHEN MATCHED AND (
        T.extracted_at IS NULL
        OR S.extracted_at >= T.extracted_at
    )
    THEN UPDATE SET
        artist_name = S.artist_name,
        channel_id = S.channel_id,
        channel_title = S.channel_title,
        video_title = S.video_title,
        description = S.description,
        published_at = S.published_at,
        duration_seconds = S.duration_seconds,
        tags = S.tags,
        category_id = S.category_id,
        view_count = S.view_count,
        like_count = S.like_count,
        comment_count = S.comment_count,
        extracted_at = S.extracted_at,
        source = S.source,
        ingestion_date = S.ingestion_date
    WHEN NOT MATCHED THEN INSERT (
        artist_name,
        channel_id,
        channel_title,
        video_id,
        video_title,
        description,
        published_at,
        duration_seconds,
        tags,
        category_id,
        view_count,
        like_count,
        comment_count,
        extracted_at,
        source,
        ingestion_date
    )
    VALUES (
        S.artist_name,
        S.channel_id,
        S.channel_title,
        S.video_id,
        S.video_title,
        S.description,
        S.published_at,
        S.duration_seconds,
        S.tags,
        S.category_id,
        S.view_count,
        S.like_count,
        S.comment_count,
        S.extracted_at,
        S.source,
        S.ingestion_date
    )
    """

    job = client.query(sql, location=BQ_LOCATION)

    job.result()

    print("Done Merge")
