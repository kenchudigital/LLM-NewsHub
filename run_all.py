import os
from datetime import datetime

today = datetime.now().strftime('%Y-%m-%d')

if __name__ == "__main__":
    # will run this every day on the cloud (Function Compute in Alibaba Cloud)
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
    os.system(f"python generate_article/generate_data.py --date {today}")
    os.system(f"python generate_article/generate_article.py --date {today}")
    os.system(f"python generate_article/gather_resource.py --date {today}")
    os.system(f"python generate_article/category_arrange.py --date {today}")
    print('Image Generation: ...')
    os.system(f"python deployment/image/main.py --date {today}")
    print('Audio Generation: ...')
    os.system(f"python deployment/audio/main.py --date {today}")
    # print('Video Generation: ...')
    # os.system(f"python deployment/wav2lip.py --date {today}")
    print('migrate the data to the UI database...')
    os.system(f"python migrate.py --date {today}")


    # print('Evaluate the content...') 
    # os.system(f"python evaluate/evaluate.py --date {today}")

    # print('generate the knowledge graph...')
    # os.system(f"python migrate.py --date {today}")