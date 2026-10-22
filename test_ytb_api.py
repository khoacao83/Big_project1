
import os
import json

from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

load_dotenv()

api_key = os.getenv("YOUTUBE_API_KEY")

if not api_key:
    raise ValueError("Missing YOUTUBE_API_KEY")

youtube = build(
    "youtube",
    "v3",
    developerKey=api_key
)

# Public YouTube channel used only for testing.
channel_id = "UC_x5XG1OV2P6uZZ5FSM9Ttw"

try:
    response = youtube.channels().list(
        part="snippet,statistics,contentDetails",
        id=channel_id
    ).execute()

    if not response.get("items"):
        raise ValueError("Channel not found")

    channel = response["items"][0]

    result = {
        "channel_id": channel["id"],
        "channel_title": channel["snippet"]["title"],
        "subscriber_count": channel[
            "statistics"
        ].get("subscriberCount"),
        "video_count": channel[
            "statistics"
        ].get("videoCount"),
        "uploads_playlist_id": channel[
            "contentDetails"
        ]["relatedPlaylists"]["uploads"]
    }

    print(json.dumps(
        result,
        indent=2,
        ensure_ascii=False
    ))

except HttpError as error:
    print(f"YouTube API error: {error.resp.status}")
    raise
