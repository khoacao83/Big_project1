import json
from pathlib import Path

from config.setting import ( PROJECT_ID, CHANNEL_ID, UPLOADS_PLAYLIST_ID )

from etl.extract.playlist_incremental import (get_all_playlist_video_ids)
from etl.extract.incremental import find_new_video_ids
from etl.extract.new_video_details import get_video_details
from etl.transform.video import  transform_video
from etl.utils.checkpoint import (get_existing_video_ids, save_checkpoint)
from etl.load.bigquery import load_to_staging
from etl.load.merge_video import merge_staging_to_videos

def main():
    print(f"BigQuery table: {PROJECT_ID}.youtube_clean.videos")
    print(f"CHANNEL_ID={CHANNEL_ID!r}")
    print(f"UPLOADS_PLAYLIST_ID={UPLOADS_PLAYLIST_ID!r}")
    if not CHANNEL_ID.startswith("UC"):
        raise ValueError("CHANNEL_ID must be a YouTube channel ID starting with UC")

    # đọc tất cả hiện có bn video trong bigquery
    existing_ids=get_existing_video_ids(CHANNEL_ID)

    print(f"Existing videos in BigQuery for this channel: {len(existing_ids)}")

    #quét và lấy ds video id hiện tại
    playlist_ids = get_all_playlist_video_ids(UPLOADS_PLAYLIST_ID)
    print(f"Playlist videos: {len(playlist_ids)}")

    # so sánh list cũ và mới để tìm ID ch tồn tại trong biguery
    new_ids=find_new_video_ids(playlist_ids, existing_ids)
    print(f"Already loaded: {len(set(playlist_ids) & existing_ids)}")
    print(f"New videos to fetch: {len(new_ids)}")

    if not new_ids:
        print("No update today")
        save_checkpoint(CHANNEL_ID, UPLOADS_PLAYLIST_ID, playlist_ids[0] if playlist_ids else None)
        return
    
    #so sánh để tìm ra các ID chưa tồn tại
    raw_videos = get_video_details(new_ids)

    returned_ids={
        video["id"] for video in raw_videos
    }
    missing_ids= set(new_ids) - returned_ids
    
    if missing_ids:
        raise RuntimeError(
            f"API did not return {len(missing_ids)}"
        )
    #transform from json to clean 
    clean_video= [transform_video(video) for video in raw_videos]

    #chuyển thành json
    output_dir=Path("data/clean")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path=(output_dir/"incremental.ndjson")

    with output_path.open("w",encoding="utf-8") as f:
        for video in clean_video:
            f.write(
                json.dumps(
                    video,ensure_ascii=False
                ) + "\n"
            )
    #load stagging
    loaded_rows=load_to_staging(PROJECT_ID,str(output_path))
    if loaded_rows != len(clean_video):
        raise RuntimeError("loaded mismatch")
    
    # merge
    merge_staging_to_videos()

    #update checkpoint
    save_checkpoint(CHANNEL_ID, UPLOADS_PLAYLIST_ID, playlist_ids[0] if playlist_ids else None)

if __name__=="__main__":
    main()
