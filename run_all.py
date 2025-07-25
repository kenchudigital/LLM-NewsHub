import os
from datetime import datetime

today = datetime.now().strftime('%Y-%m-%d')

if __name__ == "__main__":
    import sys
    if "--date" in sys.argv:
        date_index = sys.argv.index("--date") + 1
        if date_index < len(sys.argv):
            today = sys.argv[date_index]
    
    print(f'process date: {today}')
    # will run this every day on the cloud (ECS in Alibaba Cloud)

    # prepare your stable diffusion server before start !

    print('Scraping: ...')
    os.system(f"python scrapers/fundus/scraper.py --date {today}")
    os.system(f"python scrapers/reddit/scraper.py")

    print('Generating Card: ...')
    os.system(f"python card/event/process.py --date {today}")
    os.system(f"python card/statement/process.py --date {today}")

    print('Grouping: ...')
    os.system(f"python cluster/group_content.py --date {today}")
    os.system(f"python cluster/regroup_with_size_limits.py --date {today}")

    print('Content Generation: ...')
    os.system(f"python generate_article/generate_article.py --date {today}")
    os.system(f"python generate_article/gather_resource.py --date {today}")
    os.system(f"python generate_article/category_arrange.py --date {today}")

    print('Audio Generation: ...')
    os.system(f"python deployment/audio/main.py --date {today}")

    print('Image Generation: ...') # {path}/stable-diffusion/stable-diffusion-webui/webui.sh --api
    os.system(f"python deployment/image/main.py --date {today}")

# ---
    # print('migrate the data to the UI database...')
    # os.system(f"python migrate.py --date {today}")

    print(datetime.now()) 

    print('Video Generation: ...')
    os.system(f"python deployment/summary/generate_summary.py --date {today}")

    os.system("python deployment/audio/tts.py --speech deployment/summary/resource/summary.txt --output deployment/summary/resource/summary.mp3 --voice us")


# Optional

    # video generation please see quick_start.md

    # print('Video Generation: ...')
    # os.system(f"python deployment/summary/generate_summary.py --date {today}")

    # os.system("python deployment/audio/tts.py --speech deployment/summary/resource/summary.txt --output deployment/summary/resource/summary.mp3 --voice us")

#     os.system(f"""
# conda activate llm-news-video && \
# cd deployment/Wav2Lip && python inference.py \
#   --checkpoint_path checkpoints/wav2lip_gan.pth \
#   --face samples/face.mp4 \
#   --audio ../summary/resource/summary.mp3 \
#   --outfile ../summary/resource/news_report.mp4 && \
# conda activate llm-news && cd ../..
# """) 
    # need to update which summary video to use
    # os.system("python deployment/summary/merge_video.py")
    # os.system("python deployment/summary/add_bg_music.py")
    # os.system(f"cp deployment/summary/resource/summary.mp4 apps/static/summary-video/2025-07-18/summary.mp4")


    # print('Evaluate the content...') 
    # os.system(f"python evaluate/evaluate.py --date {today}")

    # print('generate the knowledge graph...')
    # os.system(f"python data/output/generate_kg.py")