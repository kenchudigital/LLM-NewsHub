import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union
from ..core.config import settings

# Add fuzzywuzzy import
try:
    from fuzzywuzzy import fuzz
    FUZZYWUZZY_AVAILABLE = True
except ImportError:
    FUZZYWUZZY_AVAILABLE = False
    print("Warning: fuzzywuzzy not installed. Fuzzy search will not work.")

logger = logging.getLogger(__name__)

class NewsService:
    def __init__(self):
        self.articles_cache: Dict[str, Dict] = {}
        self.categories_cache: Dict[str, Dict] = {}
        self.resources_cache: Dict[str, Dict] = {}
        self.conversation_memory: Dict[str, List[Dict]] = {}
    
    def safe_float(self, value: Union[str, int, float], default: float = 0.0) -> float:
        """Safely convert a value to float, handling strings and None"""
        try:
            if value is None:
                return default
            return float(value)
        except (ValueError, TypeError):
            return default
    
    def safe_int(self, value: Union[str, int, float], default: int = 0) -> int:
        """Safely convert a value to int, handling strings and None"""
        try:
            if value is None:
                return default
            return int(float(value))  # Convert to float first to handle "1.0" strings
        except (ValueError, TypeError):
            return default
    
    def load_articles_for_date(self, date: str) -> Dict:
        """Load all articles for a specific date"""
        if date in self.articles_cache:
            return self.articles_cache[date]
        
        articles_dir = Path(f"static/articles/{date}")
        if not articles_dir.exists():
            return {}
        
        articles = {}
        categories = {}
        
        # Load categories
        categories_file = articles_dir / "group_categories.json"
        if categories_file.exists():
            try:
                with open(categories_file, 'r', encoding='utf-8') as f:
                    categories = json.load(f)
            except Exception as e:
                logger.error(f"Error loading categories: {e}")
        
        # Load individual articles
        for article_file in articles_dir.glob("group_*.json"):
            if article_file.name == "group_categories.json":
                continue
                
            group_id = article_file.stem
            try:
                with open(article_file, 'r', encoding='utf-8') as f:
                    article_data = json.load(f)
                    article_data['group_id'] = group_id
                    article_data['category'] = categories.get(group_id, 'general')
                    articles[group_id] = article_data
            except Exception as e:
                logger.error(f"Error loading article {article_file}: {e}")
        
        self.articles_cache[date] = articles
        self.categories_cache[date] = categories
        return articles
    
    def get_article(self, date: str, group_id: str) -> Optional[Dict]:
        """Get a specific article by date and group ID"""
        articles = self.load_articles_for_date(date)
        return articles.get(group_id)
    
    def get_categories(self, date: str) -> Dict:
        """Get categories for a specific date"""
        self.load_articles_for_date(date)  # This loads categories too
        return self.categories_cache.get(date, {})
    
    def get_most_recent_date(self) -> str:
        """Get the most recent available date"""
        static_dir = Path("static/articles")
        if not static_dir.exists():
            return "2025-06-14"  # fallback
        
        date_dirs = [d.name for d in static_dir.iterdir() if d.is_dir()]
        if not date_dirs:
            return "2025-06-14"  # fallback
        
        return max(date_dirs)
    
    def fuzzy_search_articles(self, articles: List[Dict], search_term: str, threshold: int = 70) -> List[Dict]:
        """
        Perform fuzzy search on articles
        """
        if not search_term or not FUZZYWUZZY_AVAILABLE:
            return articles
        
        search_term = search_term.lower()
        scored_articles = []
        
        for article in articles:
            # Get text fields to search
            headline = article.get('headline', '').lower()
            content = article.get('content', '').lower()
            summary = article.get('summary', '').lower()
            
            # Calculate fuzzy scores for each field using different algorithms
            scores = []
            
            # 1. Partial ratio - best for finding substrings with typos
            scores.append(fuzz.partial_ratio(search_term, headline))
            scores.append(fuzz.partial_ratio(search_term, content))
            scores.append(fuzz.partial_ratio(search_term, summary))
            
            # 2. Token sort ratio - good for word order independence
            scores.append(fuzz.token_sort_ratio(search_term, headline))
            scores.append(fuzz.token_sort_ratio(search_term, content))
            scores.append(fuzz.token_sort_ratio(search_term, summary))
            
            # 3. Check individual words in the text
            all_text = f"{headline} {content} {summary}"
            words = all_text.split()
            for word in words:
                if len(word) > 2:  # Only check words longer than 2 characters
                    word_score = fuzz.ratio(search_term, word.lower())
                    scores.append(word_score)
            
            # Take the highest score
            max_score = max(scores) if scores else 0
            
            # If score meets threshold, add to results
            if max_score >= threshold:
                scored_articles.append((article, max_score))
        
        # Sort by score (highest first)
        scored_articles.sort(key=lambda x: x[1], reverse=True)
        
        return [article for article, score in scored_articles]

    def get_filtered_news(self, date: Optional[str] = None, category: Optional[str] = None, search: Optional[str] = None, fuzzy: bool = False) -> List[Dict]:
        """Get news articles with optional filtering"""
        # Use most recent date if no date specified
        if not date:
            date = self.get_most_recent_date()
        
        articles = self.load_articles_for_date(date)
        
        if not articles:
            return []
        
        # Convert to list format expected by frontend
        news_list = []
        for group_id, article in articles.items():
            news_item = {
                "id": hash(group_id),
                "group_id": group_id,
                "headline": article.get("headline", ""),
                "category": article.get("category", "general"),
                "content": article.get("lead", ""),
                "summary": article.get("lead", "")[:200] + "..." if len(article.get("lead", "")) > 200 else article.get("lead", ""),
                "date": date,
                "image_url": f"/static/images/{date}/{group_id}.jpg"
            }
            
            # Apply category filter
            if category and category.lower() != "all":
                if article.get("category", "").lower() != category.lower():
                    continue
            
            news_list.append(news_item)
        
        # Apply search filter
        if search:
            if fuzzy and FUZZYWUZZY_AVAILABLE:
                # Use fuzzy search with lower threshold for better typo tolerance
                news_list = self.fuzzy_search_articles(news_list, search, threshold=70)
                print(f"Fuzzy search for '{search}' returned {len(news_list)} results")
            else:
                # Use exact search (existing logic)
                search_lower = search.lower()
                filtered_list = []
                for news_item in news_list:
                    if any(search_lower in str(news_item.get(field, "")).lower() 
                          for field in ["headline", "content", "summary"]):
                        filtered_list.append(news_item)
                news_list = filtered_list
                print(f"Exact search for '{search}' returned {len(news_list)} results")
        
        return news_list
    
    def get_article_context(self, group_id: str, date: str) -> str:
        """Get article context for the AI assistant - FIXED type handling"""
        articles = self.load_articles_for_date(date)
        if group_id not in articles:
            return ""
        
        article = articles[group_id]
        context = f"""
CURRENT ARTICLE ANALYSIS:
Title: {article.get('headline', '')}
Category: {article.get('category', '')}
Date: {date}

SUMMARY:
{article.get('lead', '')}

ARTICLE STRUCTURE:
- Total Sections: {len(article.get('body', []))}
- Conclusion Available: {'Yes' if article.get('conclusion') else 'No'}
- Timeline Events: {len(article.get('timeline', {}))}
"""
        
        # Add metrics from each section with safe type conversion
        body_sections = article.get('body', [])
        if body_sections:
            try:
                # Safely convert sentiment scores
                sentiment_scores = []
                fake_news_probs = []
                all_publishers = []
                all_regions = []
                
                for section in body_sections:
                    # Handle sentiment with safe conversion
                    sentiment = self.safe_float(section.get('sentisement_from_the_content'))
                    sentiment_scores.append(sentiment)
                    
                    # Handle fake news probability with safe conversion
                    fake_prob = self.safe_float(section.get('fake_news_probability'))
                    fake_news_probs.append(fake_prob)
                    
                    # Handle publishers and regions safely
                    publishers = section.get('Publishers', [])
                    regions = section.get('Publisher_region_diversity', [])
                    
                    if isinstance(publishers, list):
                        all_publishers.extend(publishers)
                    if isinstance(regions, list):
                        all_regions.extend(regions)
                
                # Calculate averages safely
                avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
                avg_fake_prob = sum(fake_news_probs) / len(fake_news_probs) if fake_news_probs else 0
                
                # Get unique values safely
                unique_publishers = list(set(str(p) for p in all_publishers if p))
                unique_regions = list(set(str(r) for r in all_regions if r))
                
                context += f"""
KEY METRICS:
- Average Sentiment: {avg_sentiment:.2f}
- Average Fake News Probability: {avg_fake_prob:.2f}
- Total Unique Publishers: {len(unique_publishers)}
- Regions Covered: {len(unique_regions)}
- Publisher Diversity: {', '.join(unique_publishers[:5])}
- Geographic Coverage: {', '.join(unique_regions)}
"""
            except Exception as e:
                logger.error(f"Error processing article metrics: {e}")
                context += "\nKEY METRICS: Error processing metrics data"
        
        # Add timeline if available
        timeline = article.get('timeline', {})
        if timeline and isinstance(timeline, dict):
            context += f"\nTIMELINE EVENTS:\n"
            try:
                for time, event in list(timeline.items())[:3]:
                    context += f"- {str(time)}: {str(event)}\n"
            except Exception as e:
                logger.error(f"Error processing timeline: {e}")
        
        return context
    
    def get_rag_context(self, group_id: str, date: str, query: str) -> str:
        """Get relevant context from resources for RAG - FIXED type handling"""
        resources_dir = Path(f"static/resources/{date}")
        if not resources_dir.exists():
            return ""
        
        # Load the specific resource file for this group
        group_resource_file = resources_dir / f"{group_id}.json"
        if not group_resource_file.exists():
            return ""
        
        try:
            with open(group_resource_file, 'r', encoding='utf-8') as f:
                resource_data = json.load(f)
            
            # Extract relevant information for AI context
            context_parts = []
            
            # Summary information with safe conversion
            if 'summary' in resource_data and isinstance(resource_data['summary'], dict):
                summary = resource_data['summary']
                context_parts.append(f"""
ARTICLE RESOURCE SUMMARY:
- Total Events: {self.safe_int(summary.get('events_count'))}
- Posts: {self.safe_int(summary.get('posts_count'))} 
- Comments: {self.safe_int(summary.get('comments_count'))}
- Articles: {self.safe_int(summary.get('articles_count'))}
- Total Items: {self.safe_int(summary.get('total_items'))}
""")
            
            # Key events (first 3 most important) with safe handling
            if 'events' in resource_data and isinstance(resource_data['events'], list):
                context_parts.append("\nKEY EVENTS:")
                for i, event in enumerate(resource_data['events'][:3]):
                    if isinstance(event, dict):
                        context_parts.append(f"""
Event {i+1}: {str(event.get('event_description', ''))}
- Type: {str(event.get('event_type', ''))}
- Date: {str(event.get('event_date', ''))}
- Location: {str(event.get('event_location', ''))}
- People Involved: {str(event.get('event_people_involved', ''))}
- Sentiment: {self.safe_float(event.get('content_sentiment'), 'N/A')}
- Fake News Probability: {self.safe_float(event.get('fake_news_probability'), 'N/A')}
- Publisher: {str(event.get('publisher', ''))} ({str(event.get('publisher_country', ''))})
- Credibility Score: {self.safe_float(event.get('credibility_score'), 'N/A')}
""")
            
            # Social media posts if available with safe handling
            if 'posts' in resource_data and isinstance(resource_data['posts'], list):
                posts = resource_data['posts']
                context_parts.append(f"\nSOCIAL MEDIA POSTS ({len(posts)} total):")
                for i, post in enumerate(posts[:2]):  # First 2 posts
                    if isinstance(post, dict):
                        context_parts.append(f"""
Post {i+1}: {str(post.get('title', ''))}
- Platform: {str(post.get('platform', ''))}
- Engagement: {self.safe_int(post.get('ups'))} upvotes, {self.safe_int(post.get('num_comments'))} comments
- Sentiment: {self.safe_float(post.get('sentiment_score'), 'N/A')}
""")
            
            # Comments insights with safe handling
            if 'comments' in resource_data and isinstance(resource_data['comments'], list):
                comments = resource_data['comments']
                context_parts.append(f"\nPUBLIC SENTIMENT FROM COMMENTS ({len(comments)} total):")
                
                # Calculate average sentiment safely
                sentiment_scores = []
                for comment in comments:
                    if isinstance(comment, dict) and comment.get('sentiment_score') is not None:
                        score = self.safe_float(comment.get('sentiment_score'))
                        if score != 0:  # Only include non-zero scores
                            sentiment_scores.append(score)
                
                if sentiment_scores:
                    avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
                    context_parts.append(f"- Average Comment Sentiment: {avg_sentiment:.2f}")
                
                # Top commented themes
                top_comments = []
                for comment in comments:
                    if isinstance(comment, dict):
                        ups = self.safe_int(comment.get('ups'))
                        comment['_ups_safe'] = ups
                        top_comments.append(comment)
                
                top_comments.sort(key=lambda x: x.get('_ups_safe', 0), reverse=True)
                for i, comment in enumerate(top_comments[:2]):
                    body = str(comment.get('body', ''))[:200]
                    context_parts.append(f"Top Comment {i+1}: {body}...")
            
            # Publisher diversity and credibility with safe handling
            if 'events' in resource_data and isinstance(resource_data['events'], list):
                publishers = []
                countries = []
                credibility_scores = []
                
                for event in resource_data['events']:
                    if isinstance(event, dict):
                        if event.get('publisher'):
                            publishers.append(str(event.get('publisher')))
                        if event.get('publisher_country'):
                            countries.append(str(event.get('publisher_country')))
                        
                        cred_score = self.safe_float(event.get('credibility_score'))
                        if cred_score > 0:
                            credibility_scores.append(cred_score)
                
                if publishers:
                    unique_publishers = list(set(publishers))
                    unique_countries = list(set(countries))
                    avg_credibility = sum(credibility_scores) / len(credibility_scores) if credibility_scores else 0
                    
                    context_parts.append(f"""
PUBLISHER ANALYSIS:
- Unique Publishers: {len(unique_publishers)}
- Countries Represented: {', '.join(unique_countries)}
- Average Credibility Score: {avg_credibility:.2f if avg_credibility > 0 else 'N/A'}
- Main Publishers: {', '.join(unique_publishers[:5])}
""")
            
            return "\n".join(context_parts)
            
        except Exception as e:
            logger.error(f"Error loading resource {group_resource_file}: {e}")
            return "Error loading additional resource data."
    
    def load_knowledge_base(self) -> str:
        """Load knowledge from knowledge.txt file"""
        try:
            with open('knowledge.txt', 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            logger.warning("knowledge.txt not found")
            return "AI NewsSense - An intelligent news portal covering gossip, social issues, and technology."
        except Exception as e:
            logger.error(f"Error loading knowledge base: {e}")
            return "AI NewsSense - An intelligent news portal covering gossip, social issues, and technology."
    
    def load_news_data(self) -> str:
        """Load current news data to provide context"""
        try:
            with open('data/news_data.json', 'r', encoding='utf-8') as f:
                news_data = json.load(f)
                news_summary = "Current news articles available:\n"
                for article in news_data[:5]:
                    news_summary += f"- {article['headline']} (Category: {article['category']})\n"
                return news_summary
        except Exception as e:
            logger.error(f"Error loading news data: {e}")
            return "Recent news data is currently unavailable." 