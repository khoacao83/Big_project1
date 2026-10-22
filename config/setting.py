import os
from dotenv import load_dotenv

load_dotenv()

YOUTUBE_API_KEY=os.getenv("YOUTUBE_API_KEY")

if not YOUTUBE_API_KEY:
    raise ValueError(
        "YOUTUBE_API_KEY is missing from .env"
    )

TEST_CHANNEL_ID = "UC_x5XG1OV2P6uZZ5FSM9Ttw"

RAW_DATA_DIR = "data/raw"
