
## CSV Schema

| Column Name | Type | Description | Example |
|------------|------|-------------|---------|
| title | string | Article title | "ANALYTICAL ENGLISH 解析英語(常春藤)" |
| content | string | Full article text | "Some 400 kilometers above the Earth's surface..." |
| topic | string | Article topics/categories | "Technology, Science" |
| publish_time | datetime | UTC timestamp of publication | "2025-06-09T08:00:00.916000+00:00" |
| publish_date | date | Date of publication | "2025-06-09" |
| link | string | URL of the article | "https://www.taipeitimes.com/..." |
| publisher | string | News source name | "Taipei Times" |
| publisher_country | string | Country code of publisher | "tw" |
| language | string | Detected language code | "en" |
| media_links | JSON string | List of media URLs and metadata | `[{"url": "...", "type": "article_image", ...}]` |
| extract_time | datetime | UTC timestamp of extraction | "2024-03-21T14:30:00+00:00" |
| word_count | integer | Number of words in content | 450 |
| url_category | string | Category from URL path | "news" |
| url_sub_category | string | Sub-category from URL path | "technology" |
| url_domain | string | Domain name | "www.taipeitimes.com" |

## Media Links JSON Structure
```json
[
    {
        "url": "string",          // URL of the media
        "description": "string",  // Media description
        "caption": "string",      // Media caption
        "width": integer,         // Image width if available
        "type": "string"          // "cover_image" or "article_image"
    }
]
```

## Notes
- All timestamps are in UTC
- Language detection uses `langdetect` library
- Media links are stored as JSON strings
- URL categories are extracted from the article URL path
- Word count is based on whitespace splitting
- Publisher country codes follow ISO 3166-1 alpha-2 format

## Data Collection
- Articles are collected using the Fundus library
- Each file contains articles published on the same date
- Files are organized by extraction date and publication date
- Duplicate articles are not included
- Articles are sorted by publish_time in descending order (newest first)