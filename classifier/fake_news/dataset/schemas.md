# Fake News Detection Dataset

Source URL: https://www.kaggle.com/datasets/emineyetm/fake-news-detection-datasets

This directory contains the datasets used for training and evaluating fake news detection models.

## Dataset Files

- `Fake_News_Train.csv`: Training dataset containing labeled news articles
- `Fake_News_Test.csv`: Test dataset for model evaluation

## Data Schema

### Training Dataset (`Fake_News_Train.csv`)

| Column    | Type   | Description                                    |
|-----------|--------|------------------------------------------------|
| id        | int    | Unique identifier for each article             |
| title     | string | Title of the news article                      |
| text      | string | Full text content of the article               |
| label     | int    | Binary label (0: Real, 1: Fake)               |

### Test Dataset (`Fake_News_Test.csv`)

| Column    | Type   | Description                                    |
|-----------|--------|------------------------------------------------|
| id        | int    | Unique identifier for each article             |
| title     | string | Title of the news article                      |
| text      | string | Full text content of the article               |

## Features Generated

### Sentiment Features

For each text field (title and content), the following sentiment features are extracted:

1. VADER Sentiment:
   - compound_score: Overall sentiment (-1 to 1)
   - positive_score: Positive sentiment strength
   - negative_score: Negative sentiment strength
   - neutral_score: Neutral sentiment strength

2. TextBlob Sentiment:
   - polarity: Sentiment polarity (-1 to 1)
   - subjectivity: Subjectivity score (0 to 1)

## Model Performance Tracking

The experiments are tracked in `experiments/results.json` with the following metrics:
- Accuracy
- Precision
- Recall
- F1 Score
- ROC AUC
- Feature Importance
- Cross-validation Scores

## Visualization Outputs

The following visualizations are generated:
1. Feature importance plots
2. Sentiment distribution by class
3. Confusion matrix
4. ROC curves