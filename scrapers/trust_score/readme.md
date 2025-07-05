# Trust Score Scrapers

This directory contains scrapers for collecting trust score and media bias data from external sources to assess news publisher credibility and country-level trust metrics.

## Overview

The trust score system combines two key data sources:
1. **Publisher-level bias and credibility ratings** from Media Bias Fact Check
2. **Country-level trust scores** from Reporters Sans Frontières (RSF) Press Freedom Index

## Scrapers

### 1. Country Index Scraper (`country_index_scraper.py`)

**Source**: Reporters Sans Frontières (RSF) - Press Freedom Index 2025
- **URL**: `https://rsf.org/sites/default/files/import_classement/2025.csv`
- **Description**: Downloads the official RSF Press Freedom Index data containing country-level trust scores, rankings, and contextual metrics across political, economic, legal, social, and safety dimensions.
- **Output File**: `data/raw/trust_score/country_2025.csv`

**Data Contents**:
- Overall press freedom scores and rankings by country
- Political context scores and rankings
- Economic context scores and rankings  
- Legal context scores and rankings
- Social context scores and rankings
- Safety scores and rankings
- Multi-language country names (English, French, Spanish, Portuguese, Arabic, Persian)
- Year-over-year score and ranking evolution

**Usage**:
```bash
python scrapers/trust_score/country_index_scraper.py
```

**Data Source Authority**: 
Reporters Sans Frontières (RSF) is an international non-profit organization that monitors press freedom worldwide and publishes the annual World Press Freedom Index, ranking countries based on the level of freedom available to journalists.

---

### 2. Publishers Bias Scraper (`publishers_bias_scraper.py`)

**Source**: Media Bias Fact Check (MBFC) via RapidAPI
- **API Endpoint**: `https://media-bias-fact-check-ratings-api2.p.rapidapi.com/fetch-data`
- **Description**: Fetches comprehensive media bias ratings, factual reporting assessments, and credibility scores for thousands of news publishers worldwide through the Media Bias Fact Check API.
- **Output File**: `data/raw/trust_score/publishers_bias.csv`

**Data Contents**:
- Publisher source names and URLs
- Media bias classifications (Left, Left-Center, Least Biased, Right-Center, Right, etc.)
- Factual reporting ratings (Very High, High, Mostly Factual, Mixed, Low, Very Low)
- Credibility assessments (High, Medium, Low)
- Publisher country information
- Media type classifications (Newspaper, TV News, Website, etc.)
- Media Bias Fact Check URLs for detailed analysis
- Data extraction timestamps

**Requirements**:
- RapidAPI key (set as `RAPID_API_KEY` environment variable)
- `.env` file with API credentials

**Usage**:
```bash
# Set up environment variable
export RAPID_API_KEY="your_rapidapi_key_here"

# Run scraper
python scrapers/trust_score/publishers_bias_scraper.py
```

**Data Source Authority**:
Media Bias Fact Check (MBFC) is a fact-checking website that rates news sources for bias and factual accuracy. Founded by Dave Van Zandt in 2015, it provides systematic analysis of media outlets' political bias, factual reporting quality, and overall credibility.

---

## Data Integration

Both datasets are integrated in the event card processing pipeline (`card/event/process.py`) to provide comprehensive trust scoring:

### Publisher Trust Score Calculation
```python
# Composite score formula (0-1 scale):
composite_score = (
    (factual_score + 1) / 2 * 0.6 +      # 60% weight on factual reporting
    (1 - abs(bias_score)) * 0.3 +        # 30% weight on bias neutrality  
    (credibility_score + 1) / 2 * 0.1    # 10% weight on credibility
)
```

### Score Mappings
- **Bias Score**: Categorical bias → numerical scale (-1 to 1)
- **Factual Score**: Reporting quality → numerical scale (-1 to 1)  
- **Credibility Score**: Assessment → numerical scale (-1 to 1)

## Utility Functions

### Publisher URL Testing

For testing news publisher URLs against the bias database:

```python
from scrapers.trust_score.publishers_bias_scraper import test_news_url

# Test a publisher URL
result = test_news_url("cnn.com")
print(result)
# Output: {'found': True, 'source': 'CNN', 'bias': 'Left', 'factual_reporting': 'Mostly Factual', 'credibility': 'High', 'country': 'United States'}
```

**Parameters**:
- `url` (str): Domain name to test (e.g., "cnn.com", "bbc.com")
- `df` (str): Path to publishers bias CSV file

**Returns**:
- Dictionary with publisher information if found
- `{'found': False, 'url': url}` if not found

## Output Files

### `data/raw/trust_score/country_2025.csv`
- **Source**: RSF Press Freedom Index
- **Frequency**: Annual update
- **Records**: ~180 countries
- **Key Fields**: Score 2025, Rank, Political/Economic/Legal/Social Context scores

### `data/raw/trust_score/publishers_bias.csv`  
- **Source**: Media Bias Fact Check API
- **Frequency**: Updated as needed
- **Records**: ~4000+ publishers
- **Key Fields**: Source, Bias, Factual Reporting, Credibility, Source URL

## Data Quality Notes

- **Country data**: Official RSF rankings, updated annually
- **Publisher data**: Crowd-sourced and expert-reviewed bias assessments
- **Coverage**: Global scope with emphasis on major news outlets
- **Validation**: Cross-referenced with multiple bias assessment methodologies
- **Limitations**: Bias assessments may reflect reviewer subjectivity; not all publishers covered