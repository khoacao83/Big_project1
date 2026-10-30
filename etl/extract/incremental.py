def find_new_video_ids(playlist_video_ids, existing_video_ids): # so sanh 2 list de tim ID hien chua co
    new_ids=[]
    seen=set()

    for video_id in playlist_video_ids:
        if not video_id or video_id in seen: continue
        seen.add(video_id)

        if video_id not in existing_video_ids:
            new_ids.append(video_id)
    return new_ids