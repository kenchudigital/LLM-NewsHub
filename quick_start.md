# Quick Start

All script can be run at the root /

```bash
# RUN ALL
conda activate llm-news
python run_all.py --date "your_date"
conda activate llm-news-video
python run_all2.py --date "your_date"
```

## Pre install the trust score data

```bash
python scrapers/trust_score/country_index_scraper.py
python scrapers/trust_score/country_index_scraper.py
```

## Classifier - Fake News

```bash
python classifier/fake_news/run_pipeline.py 
python classifier/fake_news/run_pipeline.py --test-size 0.2 --random-state 42
```

```python
# Fake News Classifer
from classifier.fake_news.predict import predict_fake_news
text = "Your news article text here"
result = predict_fake_news(text)
print(f"Fake news probability: {result['fake_probability']:.3f}")
```

## Classifier - Category

```bash
python classifier/category/run_pipeline.py --test "classifier/category/dataset/BBC_News_Test.csv" --train "classifier/category/dataset/BBC_News_Train.csv"
```

```python
# Category
from classifer.category.predict import predict_single_text
text = "Technology giant Apple unveiled its latest iPhone model today"
result = predict_single_text(text)
```

## Daily Update

```bash
python run_all.py
```

## Scraper 

```bash
# Fundus (news publisher)
python scrapers/fundus/scraper.py --date "2025-06-21" # ok

# Reddit (Social Media) 
python scrapers/reddit/scraper.py # only that day information
# if get something wrong, re-run this command then will resume the processing !
```

## Card Generation
```bash
python card/event/process.py --date "2025-06-21" # ok
python card/statement/process.py --date "2025-06-21" # ok
```

## Cluster
```bash
python cluster/group_content.py --date "2025-06-21" # ok
python cluster/regroup_with_size_limits.py --date "2025-06-21" 
```

## Content Generation

```bash
# output: data/output/article/{date}/group_{n}.json (LLM generate)
python generate_article/generate_article.py --date "2025-06-21"
```

```bash
# output: data/output/resource/{date}/group_{n}.json
python generate_article/gather_resource.py --date "2025-06-21"
```

```bash
# output: data/output/article/{date}/group_{n}.json
python generate_article/category_arrange.py --date "2025-06-21"
```

## Summary

```
# output: 
python
```

## Evaluate

```bash
python evaluate/evaluate.py --date "2025-06-21"
```

## Image Generation

```bash
# need to deploy stable diffusion first --api
python deployment/image/main.py --date "2025-06-21"   
```

## Audio Generation

```bash
python deployment/audio/main.py --date "2025-06-21"
# for summary
python deployment/audio/tts.py --speech deployment/summary/summary.txt --output deployment/summary/summary.mp3 --voice us
```

## Video - Wav2Lip (Manually) - need another environment due to python package compatibility 

```bash
conda create -n wav2lip python=3.8
```

## Migrate

```bash
python migrate.py --date "2025-06-21"
```

## Summary Video

```bash
# python deployment/wav2lip.py --date "2025-06-21"

# python deployment/summary/add_logo.py # for first time only
python deployment/summary/generate_summary.py
python deployment/audio/tts.py --speech deployment/summary/resource/summary.txt --output deployment/summary/resource/summary.mp3 --voice us

# do the Wav2Lip manually
# summary
conda activate llm-news-video && \
cd deployment/Wav2Lip && python inference.py \
  --checkpoint_path checkpoints/wav2lip_gan.pth \
  --face samples/face.mp4 \
  --audio ../summary/resource/summary.mp3 \
  --outfile ../summary/resource/news_report.mp4
conda activate llm-news && cd .. && cd ..

python deployment/summary/merge_video.py
python deployment/summary/add_bg_music.py
cp deployment/summary/resource/summary.mp4 apps/static/summary-video/{date}/summary.mp4
```

## UI

```bash
cd apps && docker compose up
```

## Knowledge Graph

```bash
python data/output/generate_kg.py # manually to adjust the knowledge graph !
```

## Backup Deploy

```bash
docker-compose up -d
ngrok http http://localhost:3000
```

## Potential issue

```bash
# Install this before run
python setup_nltk.py
```

## Makefile Usage

```bash
# Full setup with NLTK
make setup

# Or step by step
make install
make setup-nltk

# If you still get errors, try the alternative method
make setup-nltk-alt

# Debug NLTK issues
make debug-nltk
```
