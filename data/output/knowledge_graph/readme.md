# Knowledge Graph Data Schema

## Overview
This directory contains the knowledge graph data generated from article and resource datasets. The knowledge graph creates one row per event by performing a left join between article data and resource data based on matching date and group_id.

## Output Files
- `knowledge_graph.xlsx` - Excel file containing all processed data

## Data Structure
The knowledge graph expands events so that if a group contains multiple events, each event gets its own row. For example, if `group_1` has 6 events, it will create 6 rows in the output.

## Data Schema

### Basic Information
| Column | Data Type | Description |
|--------|-----------|-------------|
| `date` | String | Date in YYYY-MM-DD format |
| `group_id` | String | Group identifier (e.g., "group_1") |

### Article Data
| Column | Data Type | Description |
|--------|-----------|-------------|
| `article_category` | String | Article category (e.g., "Political, Social") |
| `article_headline` | String | Main headline of the article |
| `article_subheadline` | String | Subheadline of the article |
| `article_lead` | String | Lead paragraph/introduction |
| `article_conclusion` | String | Conclusion paragraph |
| `article_cover_image_prompt` | String | Prompt for generating cover image |
| `article_summary_speech` | String | Summary for speech/audio generation |
| `article_event_id_list` | String (JSON) | List of event IDs referenced in article |
| `article_post_id_list` | String (JSON) | List of post IDs referenced in article |
| `article_comment_id_list` | String (JSON) | List of comment IDs referenced in article |

### Resource Summary Data
| Column | Data Type | Description |
|--------|-----------|-------------|
| `resource_events_count` | Integer | Number of events in the resource group |
| `resource_posts_count` | Integer | Number of posts in the resource group |
| `resource_comments_count` | Integer | Number of comments in the resource group |
| `resource_articles_count` | Integer | Number of articles in the resource group |
| `resource_total_items` | Integer | Total number of items in the resource group |

### Event Details
| Column | Data Type | Description |
|--------|-----------|-------------|
| `event_id` | String | Unique identifier for the event |
| `event_type` | String | Type of event (e.g., "political", "social") |
| `event_description` | String | Detailed description of the event |
| `event_date` | String | Date when the event occurred |
| `event_time` | String | Time when the event occurred |
| `event_location` | String | Location where the event took place |
| `event_organizer` | String | Organizer(s) of the event |
| `event_people_involved` | String | People involved in the event |
| `event_connections` | String | Connections to other events |
| `event_statement_or_comment` | String | Key statement or comment from the event |
| `event_statement_source` | String | Source of the statement |
| `event_statement_source_url` | String | URL of the statement source |
| `event_image_caption` | String | Caption for associated image |
| `event_image_url` | String | URL of associated image |
| `event_order` | Integer | Order of the event in the sequence |
| `event_summary` | String | Summary of the event |
| `event_news_category` | String | News category classification |

### Content Analysis
| Column | Data Type | Description |
|--------|-----------|-------------|
| `event_content_sentiment` | Float | Sentiment score of the content (-1 to 1) |
| `event_fake_news_score` | Float | Fake news detection score |
| `event_ai_generated_score` | Float | AI-generated content detection score |
| `event_keywords` | String | Keywords extracted from the content |
| `event_fake_news_probability` | Float | Probability of being fake news (0-1) |
| `event_real_news_probability` | Float | Probability of being real news (0-1) |
| `event_confidence_score` | Float | Confidence score for classification |

### Content Metadata
| Column | Data Type | Description |
|--------|-----------|-------------|
| `event_title` | String | Title of the news article |
| `event_content` | String | Full content of the news article |
| `event_topic` | String | Main topic(s) of the content |
| `event_publish_time` | String | Publication timestamp |
| `event_link` | String | URL of the original article |
| `event_publisher` | String | Publisher name |
| `event_publisher_country` | String | Publisher country code |
| `event_language` | String | Language of the content |
| `event_media_links` | String | Associated media links |
| `event_extract_time` | String | When the content was extracted |
| `event_word_count` | Integer | Number of words in the content |
| `event_url_category` | String | URL category classification |
| `event_url_sub_category` | String | URL sub-category classification |
| `event_url_domain` | String | Domain of the URL |
| `event_publish_date` | String | Publication date |
| `event_domain` | String | Domain name |

### Source Credibility
| Column | Data Type | Description |
|--------|-----------|-------------|
| `event_source` | String | Source name |
| `event_mbfc_url` | String | Media Bias/Fact Check URL |
| `event_bias` | String | Bias rating (e.g., "Right-Center") |
| `event_country` | String | Country of origin |
| `event_factual_reporting` | String | Factual reporting rating |
| `event_media_type` | String | Type of media (e.g., "Website") |
| `event_source_url` | String | Source URL |
| `event_credibility` | String | Credibility rating |
| `event_source_id` | String | Source ID number |
| `event_bias_score` | Float | Numerical bias score |
| `event_factual_score` | Float | Factual accuracy score |
| `event_credibility_score` | Float | Credibility score |
| `event_composite_score` | Float | Composite reliability score |

### Country/Regional Information
| Column | Data Type | Description |
|--------|-----------|-------------|
| `event_iso` | String | ISO country code |
| `event_score_2025` | Float | 2025 country score |
| `event_rank` | Integer | Country ranking |
| `event_political_context` | Float | Political context score |
| `event_rank_pol` | Integer | Political ranking |
| `event_economic_context` | Float | Economic context score |
| `event_rank_eco` | Integer | Economic ranking |
| `event_legal_context` | Float | Legal context score |
| `event_rank_leg` | Integer | Legal ranking |
| `event_social_context` | Float | Social context score |
| `event_rank_soc` | Integer | Social ranking |
| `event_safety` | Float | Safety score |
| `event_rank_saf` | Integer | Safety ranking |
| `event_zone` | String | Geographic zone |
| `event_country_fr` | String | Country name in French |
| `event_country_en` | String | Country name in English |
| `event_country_es` | String | Country name in Spanish |
| `event_country_pt` | String | Country name in Portuguese |
| `event_country_ar` | String | Country name in Arabic |
| `event_country_fa` | String | Country name in Farsi |
| `event_year_n` | Integer | Year of analysis |
| `event_rank_n_1` | Integer | Previous year ranking |
| `event_rank_evolution` | Integer | Ranking evolution |
| `event_score_n_1` | Float | Previous year score |
| `event_score_evolution` | Float | Score evolution |
| `event_country_code` | String | Country code |

### Sentiment Analysis
| Column | Data Type | Description |
|--------|-----------|-------------|
| `event_textblob_polarity` | Float | TextBlob polarity score (-1 to 1) |
| `event_textblob_subjectivity` | Float | TextBlob subjectivity score (0 to 1) |
| `event_vader_neg` | Float | VADER negative sentiment score |
| `event_vader_neu` | Float | VADER neutral sentiment score |
| `event_vader_pos` | Float | VADER positive sentiment score |
| `event_vader_compound` | Float | VADER compound sentiment score |

## Data Processing Notes

1. **Left Join Logic**: Article data is joined with resource data based on matching `date` and `group_id`
2. **Event Expansion**: Each event in the resource data creates a separate row
3. **Missing Data**: If resource data is missing, article data is preserved with null/zero values for event fields
4. **Data Types**: JSON arrays are serialized as strings and need to be parsed if used programmatically

## Example Usage

```python
import pandas as pd

# Read the knowledge graph data
df = pd.read_excel('knowledge_graph.xlsx')

# Filter by date
df_filtered = df[df['date'] == '2025-06-21']

# Group by article to see event counts
event_counts = df.groupby(['date', 'group_id']).size().reset_index(name='event_count')

# Analyze sentiment by event type
sentiment_analysis = df.groupby('event_type')['event_content_sentiment'].mean()
```

## Data Quality

- **Completeness**: Not all fields may be populated for every event
- **Consistency**: Field formats may vary depending on source data quality
- **Accuracy**: Sentiment and credibility scores are algorithmic and may not reflect human judgment

## Last Updated
Generated automatically by the knowledge graph generation script.
