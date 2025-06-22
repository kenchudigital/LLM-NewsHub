# BBC News Classification Dataset

This directory contains the datasets used for training and evaluating news category classification models.

Source URL: https://www.kaggle.com/competitions/learn-ai-bbc/data?select=BBC+News+Train.csv

## Dataset Files

- `BBC News Train.csv`: Training dataset containing labeled news articles
- `BBC News Test.csv`: Test dataset for model evaluation
- `BBC_News_Sample_Solution.csv`: The Dataset Sample Solution

## Data Schema

### Training Dataset (`BBC News Train.csv`)

| Column    | Type   | Description                                                |
|-----------|--------|------------------------------------------------------------|
| ArticleId | int    | Unique identifier for each article                         |
| Text      | string | Full text content of the news article                      |
| Category  | string | News category label (e.g., 'business', 'tech', 'sport', etc.) |

### Test Dataset (`BBC News Test.csv`)

| Column    | Type   | Description                                        |
|-----------|--------|----------------------------------------------------|
| ArticleId | int    | Unique identifier for each article                 |
| Text      | string | Full text content of the news article              |

## Categories

The dataset includes the following news categories:
- business
- entertainment
- politics
- sport
- tech

## Dataset Statistics

### Training Set
- Total articles: 1,490
- Distribution across categories:
  - business: 298 articles
  - entertainment: 298 articles
  - politics: 298 articles
  - sport: 298 articles
  - tech: 298 articles

### Test Set
- Total articles: 735

## Data Format

- File format: CSV (Comma Separated Values)
- Encoding: UTF-8
- Text column: Contains raw text with punctuation and special characters
- Category labels: Lowercase string values

## Example Data

### Training Data Example
```csv
ArticleId,Text,Category
1,"UK house prices rose by 1.3% in August, indicating a strong housing market despite economic challenges...",business
2,"The latest smartphone from Tech Corp features a revolutionary camera system that uses AI...",tech
3,"In the Premier League match yesterday, Manchester United secured a decisive victory...",sport
```

### Test Data Example
```csv
ArticleId,Text
501,"The central bank announced new measures to control inflation..."
502,"The film festival announced its lineup for the upcoming season..."
```
## Citation

If you use this dataset in your research, please cite:
