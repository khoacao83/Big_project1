from config.setting import TEST_CHANNEL_ID
from etl.extract.video import (get_all_video_ids, get_video_details)
from etl.utils.storage import save_raw_json

def main():
    channel_id = TEST_CHANNEL_ID

    playlist_id = "UU_x5XG1OV2P6uZZ5FSM9Ttw"

    print("Start extraction ")
    video_ids=get_all_video_ids(playlist_id)
    print(f"total playist ID {len(video_ids)}")

    video=get_video_details(video_ids)
    print(f"total video {len(video)}")

    raw_data={
        "channel_id":channel_id,
        "playlist_id":playlist_id,
        "total_video_ids":video_ids,
        "video":video
    }
    filepath= save_raw_json(raw_data, channel_id)
    print(f"complete {filepath}")

if __name__== "__main__":
    main()