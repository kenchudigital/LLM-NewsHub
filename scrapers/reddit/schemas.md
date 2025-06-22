
## Posts CSV Schema (YYYY-MM-DD-HHMM.csv in posts/)

| Column Name | Type | Description | Example |
|------------|------|-------------|---------|
| post_id | string | Unique Reddit post ID | "abc123" |
| extract_time | datetime | UTC timestamp of extraction | "2024-03-21T14:30:00+00:00" |
| source | string | Always "Reddit" | "Reddit" |
| topic/subreddit | string | Subreddit name | "news" |
| title | string | Post title | "Breaking News: ..." |
| content | string | Post text content | "This is the main post content..." |
| category | string | Category (empty by default) | "" |
| language | string | Detected language code | "en" |
| publish_time_utc | datetime | UTC timestamp of post creation | "2025-01-14T00:00:00+00:00" |
| link | string | Reddit post URL | "https://reddit.com/r/news/..." |
| image/video | string | URL of media if present | "https://i.redd.it/..." |
| ups | integer | Upvotes count | 1000 |
| upvote_ratio | float | Ratio of upvotes to total votes | 0.95 |
| score | integer | Post score | 950 |
| location | string | Location (empty by default) | "" |
| num_comments | integer | Number of comments | 150 |
| author_id | string | Reddit user ID | "user123" |
| author_name | string | Reddit username | "username" |
| author_post_karma | integer | Author's post karma | 50000 |
| author_comment_karma | integer | Author's comment karma | 25000 |

## Comments CSV Schema (YYYY-MM-DD-HHMM.csv in comments/)

| Column Name | Type | Description | Example |
|------------|------|-------------|---------|
| post_id | string | ID of parent post | "abc123" |
| comment_id | string | Unique comment ID | "def456" |
| extract_time | datetime | UTC timestamp of extraction | "2024-03-21T14:30:00+00:00" |
| comment_body | string | Comment text content | "This is a comment..." |
| category | string | Category (empty by default) | "" |
| language | string | Detected language code | "en" |
| comment_created_utc | datetime | UTC timestamp of comment creation | "2025-01-14T00:05:00+00:00" |
| comment_permalink | string | Reddit comment URL | "https://reddit.com/r/news/..." |
| media_links | JSON string | List of media URLs in comment | `["https://imgur.com/..."]` |
| comment_ups | integer | Comment upvotes | 50 |
| comment_score | integer | Comment score | 45 |
| location | string | Location (empty by default) | "" |
| commenter_name | string | Reddit username | "username" |
| commenter_id | string | Reddit user ID | "user123" |
| commenter_post_karma | integer | Commenter's post karma | 50000 |
| commenter_comment_karma | integer | Commenter's comment karma | 25000 |
| comment_parent_id | string | ID of parent comment (or post) | "abc123" |
| publish_date_utc | date | Date of comment creation | "2025-01-14" |

## Notes
- All timestamps are in UTC
- Language detection uses langdetect library
- Media links in comments are stored as JSON strings
- Post and comment IDs are unique across Reddit
- Karma values represent user reputation points
- Comments can be nested (use comment_parent_id to reconstruct threads)
- Files are named using the publish time in YYYY-MM-DD-HHMM format
- Posts and comments are collected from specified subreddits
- Data is collected with respect to Reddit's API rate limits

## Data Collection
- Posts are collected from specified subreddits
- Comments are collected for each post up to the specified limit
- Files are organized by extraction date and publication date
- Posts and comments are stored in separate directories
- Data is collected using PRAW (Python Reddit API Wrapper)
- Rate limiting is implemented to respect Reddit's API limits