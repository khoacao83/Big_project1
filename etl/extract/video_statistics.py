
from googleapiclient.discovery import build

from config.setting import YOUTUBE_API_KEY
from etl.utils.retry import execute_with_retry


def extract_statistics(video_ids):
    youtube = build(
        "youtube",
        "v3",
        developerKey=YOUTUBE_API_KEY
    )

    results = []

    for start in range(0, len(video_ids), 50):
        batch = video_ids[start:start + 50]

        def request_factory():
            return youtube.videos().list(
                part="statistics",
                id=",".join(batch),
                maxResults=50
            )

        response = execute_with_retry(request_factory)

        for video in response.get("items", []):
            stats = video.get("statistics", {})

            results.append({
                "video_id": video["id"],
                "view_count": (
                    int(stats["viewCount"])
                    if "viewCount" in stats else None
                ),
                "like_count": (
                    int(stats["likeCount"])
                    if "likeCount" in stats else None
                ),
                "comment_count": (
                    int(stats["commentCount"])
                    if "commentCount" in stats else None
                ),
            })

        print(
            f"Fetched statistics: {len(results)}/{len(video_ids)}"
        )

    return results
