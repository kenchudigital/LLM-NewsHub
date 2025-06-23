# Fake News Detection Dataset

Source URL: https://www.kaggle.com/datasets/emineyetm/fake-news-detection-datasets

This directory contains the datasets used for training and evaluating fake news detection models.

## Dataset Files

`Fake.csv` - Contains fake news articles
`True.csv` - Contains real news articles

## Data Schema

Both datasets (`Fake.csv` and `True.csv`) have the same structure with the following columns:

| Column    | Type   | Description                                    |
|-----------|--------|------------------------------------------------|
| title     | string | Title of the news article                      |
| text      | string | Full text content of the article               |
| subject   | string | Subject/category of the news article           |
| date      | string | Publication date of the article                |

## Dataset Information

- **Fake.csv**: Contains articles labeled as fake news
- **True.csv**: Contains articles labeled as real/true news
- Both datasets use the same column structure for consistency
- The datasets are used for binary classification (fake vs real news detection)