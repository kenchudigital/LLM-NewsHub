import os
from datetime import datetime

today = datetime.now().strftime('%Y-%m-%d')

if __name__ == "__main__":
    import sys
    if "--date" in sys.argv:
        date_index = sys.argv.index("--date") + 1
        if date_index < len(sys.argv):
            today = sys.argv[date_index]
    
# Optional

    # video generation please see quick_start.md
    os.system(f"""
cd deployment/Wav2Lip && python inference.py \
  --checkpoint_path checkpoints/wav2lip_gan.pth \
  --face samples/face.mp4 \
  --audio ../summary/resource/summary.mp3 \
  --outfile ../summary/resource/news_report.mp4 
""") 
    # need to update which summary video to use
    os.system("python deployment/summary/merge_video.py")
    os.system("python deployment/summary/add_bg_music.py")
    os.system(f"cp deployment/summary/resource/summary.mp4 apps/static/summary-video/{today}/summary.mp4")

    print('Finally, migrate the data to the UI database...')
    os.system(f"python migrate.py --date {today}")