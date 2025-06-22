# Quick Start

All script can be run at the root /

## Pre install the trust score data

```bash
python scrapers/trust_score/country_index_scraper.py
python scrapers/trust_score/country_index_scraper.py
```

## Classifier - Fake Mews

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
python rull_all.py
```

## Scraper 

```bash
# Fundus (news publisher)
python scrapers/fundus/scraper.py --date "2025-06-21"

# Reddit (Social Media) 
python scrapers/reddit/scraper.py # only that day information
# if get something wrong, re-run this command then will resume the processing !
```

## Card Generation
```bash
python card/event/process.py --date "2025-06-21"
python card/statement/process.py --date "2025-06-21"
```

## Cluster
```bash
python cluster/group_content.py --date "2025-06-21"  
python cluster/regroup_with_size_limits.py --date "2025-06-21" 
```

## Content Generation
```bash
# output: data/group/{date}/articles_df.csv | comments_df.csv | events_df.csv | post_df.csv
python generate_article/generate_data.py --date "2025-06-21"
```

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
```

## Video - Wav2Lip (Manually) - need another environment due to python package compatibility 

```bash
conda create -n wav2lip python=3.8
```

```bash
# python deployment/wav2lip.py --date "2025-06-21"
```

## Migrate

```bash
python migrate.py --date "2025-06-21"
```

## UI

```bash
cd apps && docker compose up
```
