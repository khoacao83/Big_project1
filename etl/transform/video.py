from datetime import datetime, timezone
import isodate

def to_init(value):
    if value is None:
        return None
    try: 
        return int(value)
    except (ValueError, TypeError):
        return None

def parse_duration(duration):
    if not duration:
        return None
    try:
        return int(
            isodate.parse_duration(duration).total_seconds()
        )
    except (ValueError, TypeError, OverflowError):
        return None

def transform_video(video, artist_name=None):
    snippet = video.get("snippet") or {}
    content = video.get("contentDetails") or {}
    stats = video.get("statistic") or {}

    return {
        "artist_name": artist_name,
        "channel_ID": snippet.get("channelId"),
        "channel_title": snippet.get("channelTitle"),
        "video_id":snippet.get("id"),
        "video_title":snippet.get("title"),
        "description":snippet.get("description"),
        "published_at":snippet.get("publishedAt"),
        "duration_second":parse_duration(content.get("duration")),

        "tags": snippet.get("tags", []),
        "category_id": snippet.get("categoryId"),
        "view_count": to_int(stats.get("viewCount")),
        "like_count": to_int(stats.get("likeCount")),
        "comment_count": to_int(stats.get("commentCount")),
        "extracted_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "source": "youtube_data_api_v3",
        "ingestion_date": datetime.now(
            timezone.utc
        ).date().isoformat()
    }