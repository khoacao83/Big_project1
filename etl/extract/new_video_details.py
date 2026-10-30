from googleapiclient.discovery import build

from config.setting import YOUTUBE_API_KEY
from etl.utils.retry import execute_with_retry

def get_video_details(video_ids):
    if not video_ids:
        return []
    youtube=build("youtube", "v3", developerKey=YOUTUBE_API_KEY, cache_discovery=False)
    results=[]

    for start in range(0, len(video_ids),50):
        batch=video_ids[start : start+50]
        response =execute_with_retry(
            lambda batch=batch: youtube.videos().list(
                part="snippet, contentDetails, statistics",
                id=",".join(batch),
                maxResults=50
            )
        )

        results.extend(response.get("items",[]))
        print(f"fetcjed {len(results)} video")
    return results