from googleapiclient.discovery import build
from config.setting import YOUTUBE_API_KEY


def get_youtube_client(): # call func từ setting.py 
    return build(
        "youtube",
        "v3",
        developerKey=YOUTUBE_API_KEY
    )

def get_all_video_ids(playist_id) -> list :
    youtube=get_youtube_client()
    video_ids=[]
    next_page_token=None
    page_number=0

    while True:
        response=youtube.playlistItems().list(
            part="contentDetails",
            playlistId=playist_id,
            maxResults=50,
            pageToken=next_page_token
        ).execute()
        page_number+=1

        for item in response.get("items",[]):
            video_id = item.get(
                "contentDetails",{}
            ).get("videoId")

            if video_id:
                video_ids.append(video_id)
        print(
            f"Page {page_number}  total {len(video_ids)}"
        )
        
        next_page_token=response.get("nextPageToken")
        if not next_page_token: break
    return list(dict.fromkeys(video_ids))

def get_video_details(video_ids):
    youtube=get_youtube_client()
    all_videos=[]

    for start in range(0, len(video_ids), 50):
        batch=video_ids[start:start+50]
        response=youtube.videos().list(
            part="snippet, contentDetails, statistics",
            #snippet: title, description, publishedAt, tags, channelId, categoryId.
            #contentDetails: duration và các thuộc tính nội dung khác.
            #statistics: viewCount, likeCount, commentCount nếu có.
            # -> trường để thiết kế bảng video trong bigQuery
            id=",".join(batch),
            maxResults=50
        ).execute()
        all_videos.extend(
            response.get("items",[])
        )
        print(f"Fetched {len(all_videos) }")
    return all_videos
