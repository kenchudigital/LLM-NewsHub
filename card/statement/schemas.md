# Statement Card Schema

This document describes the schema for statement card data extracted from social media content (Reddit posts and comments).

## Data Source
Generated by `card/statement/process.py` using GLiNER (Generalist Language Model for Named Entity Recognition) to extract structured information from social media posts and comments.

## Posts Schema

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| post_id | string | Unique Reddit post identifier | "1le6f2x" |
| extract_time | datetime | Data extraction timestamp | "2025-06-21T07:46:47.239898+00:00" |
| source | string | Data source platform | "Reddit" |
| topic/subreddit | string | Reddit subreddit name | "worldnews" |
| title | string | Post title | "Israel - Iran Conflict (Part IV)" |
| content | string | Post content (often empty for link posts) | "" |
| category | string | Content category | "" |
| language | string | Content language code | "en" |
| publish_time_utc | datetime | Post publication time (UTC) | "2025-06-18 10:55:24" |
| link | string | Post URL | "https://reddit.com/r/worldnews/comments/1le6f2x/..." |
| image/video | string | Media URL if present | "https://www.reddit.com/live/1f6c5t0liqj9c/" |
| ups | integer | Number of upvotes | 731 |
| upvote_ratio | float | Ratio of upvotes to total votes | 0.92 |
| score | integer | Post score | 731 |
| location | string | Location information | "" |
| num_comments | integer | Number of comments | 12756 |
| author_id | string | Reddit user ID | "48m9k" |
| author_name | string | Reddit username | "Isentrope" |
| author_post_karma | integer | User's post karma | 97220 |
| author_comment_karma | integer | User's comment karma | 201703 |
| publish_date_utc | string | Publication date (YYYY-MM-DD) | "2025-06-18" |
| title_polarity | float | TextBlob polarity of title | 0.0 |
| title_subjectivity | float | TextBlob subjectivity of title | 0.0 |
| title_vader_neg | float | VADER negative sentiment of title | 0.365 |
| title_vader_neu | float | VADER neutral sentiment of title | 0.635 |
| title_vader_pos | float | VADER positive sentiment of title | 0.0 |
| title_vader_compound | float | VADER compound sentiment of title | -0.3182 |
| content_polarity | float | TextBlob polarity of content | 0.0 |
| content_subjectivity | float | TextBlob subjectivity of content | 0.0 |
| content_vader_neg | float | VADER negative sentiment of content | 0.0 |
| content_vader_neu | float | VADER neutral sentiment of content | 0.0 |
| content_vader_pos | float | VADER positive sentiment of content | 0.0 |
| content_vader_compound | float | VADER compound sentiment of content | 0.0 |
| persons | string | JSON array of extracted person names | "[]" |
| dates | string | JSON array of extracted dates | "[]" |
| organizations | string | JSON array of extracted organizations | "[]" |
| locations | string | JSON array of extracted locations | "['Israel']" |
| actions | string | JSON array of extracted actions | "[]" |
| events | string | JSON array of extracted events | "[]" |
| location_details | string | JSON object with location coordinates | "{""Israel"": {""address"": ""\u05d9\u05e9\u05e8\u05d0\u05dc"", ""latitude"": 30.8124247, ""longitude"": 34.8594762}}" |
| polarity | float | Combined sentiment polarity | 0.0 |
| subjectivity | float | Combined sentiment subjectivity | 0.0 |
| vader_compound | float | Combined VADER compound score | -0.12728 |
| engagement_score | float | Calculated engagement score (0-1) | 0.41 |
| author_total_karma | integer | Total user karma | 298923 |
| author_credibility_score | float | User credibility score | 12.607944639461452 |
| real_news_probability | float | ML model real news probability | 0.018624187108691202 |
| fake_news_probability | float | ML model fake news probability | 0.9813758128913086 |
| confidence_score | float | Model confidence score (0-1) | 0.985 |
| composite_credibility_score | float | Combined credibility score | 8.011174512265216 |

## Comments Schema

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| post_id | string | Parent post identifier | "1le6f2x" |
| comment_id | string | Unique comment identifier | "myj8sid" |
| extract_time | datetime | Data extraction timestamp | "2025-06-21T08:49:22.031320+00:00" |
| comment_body | string | Comment text content | "Putin's press conference when asked if he'll help Iran..." |
| category | string | Comment category | "" |
| language | string | Comment language code | "en" |
| comment_created_utc | datetime | Comment creation time (UTC) | "2025-06-19T06:46:39" |
| comment_permalink | string | Comment URL | "https://reddit.com/r/worldnews/comments/1le6f2x/..." |
| media_links | string | JSON array of media links | "[]" |
| comment_ups | integer | Number of upvotes | 93 |
| comment_score | integer | Comment score | 93 |
| location | string | Location information | "" |
| commenter_name | string | Reddit username | "nerphurp" |
| commenter_id | string | Reddit user ID | "3n1o4vwp" |
| commenter_post_karma | float | User's post karma | 6179.0 |
| commenter_comment_karma | float | User's comment karma | 231582.0 |
| comment_parent_id | string | Parent comment ID (t3_ prefix for posts) | "t3_1le6f2x" |
| publish_date_utc | string | Publication date (YYYY-MM-DD) | "2025-06-18" |
| polarity | float | TextBlob polarity | 0.13636363636363635 |
| subjectivity | float | TextBlob subjectivity | 0.5 |
| vader_neg | float | VADER negative sentiment | 0.0 |
| vader_neu | float | VADER neutral sentiment | 0.858 |
| vader_pos | float | VADER positive sentiment | 0.142 |
| vader_compound | float | VADER compound sentiment | 0.7003 |
| persons | string | JSON array of extracted person names | "['Putin']" |
| dates | string | JSON array of extracted dates | "[]" |
| organizations | string | JSON array of extracted organizations | "[]" |
| locations | string | JSON array of extracted locations | "['Iran']" |
| actions | string | JSON array of extracted actions | "[]" |
| events | string | JSON array of extracted events | "['Live stream']" |
| location_details | string | JSON object with location coordinates | "{""Iran"": {""address"": ""\u0627\u06cc\u0631\u0627\u0646"", ""latitude"": 32.6475314, ""longitude"": 54.5643516}}" |
| controversy_score | float | Calculated controversy score | 0.8488422181524446 |
| engagement_score | float | Calculated engagement score (0-1) | 0.0 |
| real_news_probability | float | ML model real news probability | 0.32884294494598154 |
| fake_news_probability | float | ML model fake news probability | 0.6711570550540183 |
| confidence_score | float | Model confidence score (0-1) | 0.847 |

## Data Processing Notes

- **Entity Extraction**: Uses GLiNER for lightweight NER on social media content
- **Sentiment Analysis**: Multi-method approach using TextBlob and VADER
- **Geographic Enrichment**: Geocoding of extracted locations with coordinates
- **Engagement Scoring**: Calculated based on upvotes, comment depth, and interaction patterns
- **Controversy Detection**: Measures sentiment distribution variance within comment threads
- **Fake News Detection**: ML model probabilities for content authenticity
- **User Credibility**: Based on karma scores and posting history