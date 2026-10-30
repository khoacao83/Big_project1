from googleapiclient.discovery import build

from config.setting import YOUTUBE_API_KEY
from etl.utils.retry import execute_with_retry

def get_all_playlist_video_ids(playlist_id):
    youtube = build(
        "youtube",
        "v3",
        developerKey=YOUTUBE_API_KEY,
        cache_discovery=False
    )

    video_ids=[]
    seen=set()
    next_page_token=None
    page=0

    while True:
        response=execute_with_retry(
            lambda: youtube.playlistItems().list(
                part="contentDetails",
                playlistId=playlist_id,
                maxResults=50,
                pageToken=next_page_token
            )
        )
        page+=1
        for item in response.get("items",[]):
            video_id = (
                item.get("contentDetails",{}).get("videoId")
            )
            if video_id and video_id not in seen:
                seen.add(video_id)
                video_ids.append(video_id)
        
        print(
            f"page {page}: "
            f"{len(video_ids)} unique IDs"
        )

        next_page_token=response.get("nextPageToken")
        if not next_page_token: break
    return video_ids
