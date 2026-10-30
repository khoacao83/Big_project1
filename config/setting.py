import os
from dotenv import load_dotenv

load_dotenv()

PROJECT_ID=os.getenv(
    "GOOGLE_CLOUD_PROJECT",
    "youtube-de-project1"
)

BQ_LOCATION=os.getenv(
    "BQ_LOCATION",
    "asia-southeast1"
)

YOUTUBE_API_KEY=os.getenv("YOUTUBE_API_KEY")

CHANNEL_ID = os.getenv(
    "CHANNEL_ID",
    os.getenv("TEST_CHANNEL_ID", "UC_x5XG1OV2P6uZZ5FSM9Ttw")
).strip()

UPLOADS_PLAYLIST_ID = os.getenv(
    "UPLOADS_PLAYLIST_ID",
    os.getenv("TEST_UPLOADS_PLAYLIST_ID", "UU_x5XG1OV2P6uZZ5FSM9Ttw")
).strip()

if not YOUTUBE_API_KEY:
    raise ValueError(
        "YOUTUBE_API_KEY is missing from .env"
    )

RAW_DATA_DIR = "data/raw"
