from etl.utils.checkpoint import get_existing_video_ids
from etl.extract.incremental import find_new_video_ids

channel_id= "UC_x5XG1OV2P6uZZ5FSM9Ttw"

def main():
    existing_ids=get_existing_video_ids(channel_id)
    print(len(existing_ids))

    playlist_video_ids = list(existing_ids)
    
    new_ids=find_new_video_ids(playlist_video_ids, existing_ids)
    print(len(new_ids))
    print(new_ids)

if __name__=="__main__":
    main()