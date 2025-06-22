# Trust Score Data Schema

This directory contains two CSV files with trust-related data:

1. `country_2025.csv` - Country trust scores and rankings
2. `publishers_bias.csv` - Media bias and credibility ratings

## 1. Country Trust Score Data (`country_2025.csv`)

### File Format
- Extension: `.csv`
- Delimiter: `;` (semicolon)
- Encoding: UTF-8
- Year format in filename (e.g., `country_2025.csv`)

### Schema

| Column | Type | Description |
|--------|------|-------------|
| ISO | String | ISO country code (e.g., "FIN", "USA") |
| Score 2025 | Decimal | Overall trust score (0-100) |
| Rank | Integer | Global ranking (1-based, lower is better) |
| Political Context | Decimal | Trust score for political context (0-100) |
| Rank_Pol | Integer | Political context ranking |
| Economic Context | Decimal | Trust score for economic context (0-100) |
| Rank_Eco | Integer | Economic context ranking |
| Legal Context | Decimal | Trust score for legal context (0-100) |
| Rank_Leg | Integer | Legal context ranking |
| Social Context | Decimal | Trust score for social context (0-100) |
| Rank_Soc | Integer | Social context ranking |
| Safety | Decimal | Trust score for safety (0-100) |
| Rank_Saf | Integer | Safety ranking |
| Zone | String | Geographic region (e.g., "UE Balkans", "Asie-Pacifique") |
| Country_FR | String | Country name in French |
| Country_EN | String | Country name in English |
| Country_ES | String | Country name in Spanish |
| Country_PT | String | Country name in Portuguese |
| Country_AR | String | Country name in Arabic |
| Country_FA | String | Country name in Farsi |
| Year (N) | Integer | Year of the data |
| Rank N-1 | Integer | Previous year's rank |
| Rank evolution | Integer | Change in rank (positive = improvement) |
| Score N-1 | Decimal | Previous year's score |
| Score evolution | Decimal | Change in score (positive = improvement) |

### Notes
- All decimal values use comma (,) as decimal separator
- Rankings are 1-based (1 is highest)
- Covers 180 countries
- Includes year-over-year comparisons
- Multilingual country names

## 2. Media Bias Data (`publishers_bias.csv`)

### File Format
- Extension: `.csv`
- Delimiter: `,` (comma)
- Encoding: UTF-8

### Schema

| Column | Type | Description |
|--------|------|-------------|
| Source | String | Name of the media source |
| MBFC URL | String | URL to Media Bias Fact Check review |
| Bias | String | Bias rating (e.g., "Least Biased", "Left-Center", "Right-Center") |
| Country | String | Country of origin |
| Factual Reporting | String | Factual reporting rating (e.g., "High", "Mostly Factual", "Mixed") |
| Media Type | String | Type of media (e.g., "TV Station", "Newspaper", "Website") |
| Source URL | String | URL of the media source |
| Credibility | String | Credibility rating (e.g., "High", "Medium", "Low") |
| Source ID# | Integer | Unique identifier for the source |

### Bias Categories
- Least Biased
- Left-Center
- Right-Center
- Left
- Right
- Pro-Science
- Questionable
- Conspiracy-Pseudoscience
- Satire

### Factual Reporting Categories
- High
- Mostly Factual
- Mixed
- Low
- Very Low
- N/A

### Credibility Categories
- High
- Medium
- Low
- N/A

### Media Types
- TV Station
- Newspaper
- Website
- Radio Station
- Magazine
- News Agency
- Organization/Foundation
- Journal

### Notes
- Data sourced from Media Bias Fact Check
- Includes international media sources
- Covers various media types and formats
- Provides bias, factual reporting, and credibility ratings
- Includes direct links to source reviews