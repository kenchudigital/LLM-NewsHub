from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import json
from pathlib import Path
from datetime import datetime
from fuzzywuzzy import fuzz, process
from typing import List, Optional, Tuple
import re

router = APIRouter()

def load_news_data(date: Optional[str] = None) -> List[dict]:
    """
    Load news data from JSON files.
    If date is provided, only load news from that date.
    Otherwise, load all available news.
    """
    try:
        # Get the absolute path to the static directory
        static_dir = Path(__file__).parent.parent.parent.parent / "static"
        articles_dir = static_dir / "articles"
        
        print(f"Loading news from directory: {articles_dir.absolute()}")
        print(f"Directory exists: {articles_dir.exists()}")
        
        if not articles_dir.exists():
            print(f"Articles directory not found at: {articles_dir.absolute()}")
            return []
        
        all_news = []
        
        if date:
            # Load news for specific date
            date_dir = articles_dir / date
            print(f"Loading news for date: {date_dir.absolute()}")
            print(f"Date directory exists: {date_dir.exists()}")
            
            if not date_dir.exists():
                print(f"Date directory not found: {date}")
                return []
                
            # Load all group files for the date
            group_files = list(date_dir.glob("group_*.json"))
            print(f"Found {len(group_files)} group files")
            
            for group_file in group_files:
                if group_file.name == "group_categories.json":
                    continue  # Skip the categories file
                    
                print(f"Loading group file: {group_file.name}")
                try:
                    with open(group_file, 'r', encoding='utf-8') as f:
                        article_data = json.load(f)
                        # Transform the article data into the format expected by frontend
                        transformed_article = {
                            "id": int(group_file.stem.split('_')[1]),  # Extract number from group_X.json
                            "group_id": group_file.stem,  # Use the filename as group_id
                            "headline": article_data.get("headline", ""),
                            "category": article_data.get("category", ""),
                            "content": article_data.get("lead", ""),  # Use lead as content
                            "summary": article_data.get("conclusion", ""),  # Use conclusion as summary
                            "date": date,
                            "image_url": f"/static/images/{date}/{group_file.stem}.jpg",
                            "subheadline": article_data.get("subheadline", ""),
                            "body": article_data.get("body", []),
                            "timeline": article_data.get("timeline", {}),
                            "sentiment": article_data.get("body", [{}])[0].get("sentisement_from_the_content", "0") if article_data.get("body") else "0",
                            "fake_news_probability": article_data.get("body", [{}])[0].get("fake_news_probability", 0) if article_data.get("body") else 0,
                            "lead": article_data.get("lead", ""),
                            "conclusion": article_data.get("conclusion", ""),
                            "cover_image_prompt": article_data.get("cover_image_prompt", ""),
                            "event_id_list": article_data.get("event_id_list", []),
                            "post_id_list": article_data.get("post_id_list", []),
                            "comment_id_list": article_data.get("comment_id_list", [])
                        }
                        all_news.append(transformed_article)
                        print(f"Successfully loaded article: {transformed_article['headline']}")
                except Exception as e:
                    print(f"Error loading group file {group_file.name}: {str(e)}")
                    import traceback
                    print(f"Traceback: {traceback.format_exc()}")
        else:
            # Load all available news
            date_dirs = [d for d in articles_dir.iterdir() if d.is_dir()]
            print(f"Found {len(date_dirs)} date directories")
            
            for date_dir in date_dirs:
                print(f"Processing date directory: {date_dir.name}")
                group_files = list(date_dir.glob("group_*.json"))
                print(f"Found {len(group_files)} group files in {date_dir.name}")
                
                for group_file in group_files:
                    if group_file.name == "group_categories.json":
                        continue  # Skip the categories file
                        
                    print(f"Loading group file: {group_file.name}")
                    try:
                        with open(group_file, 'r', encoding='utf-8') as f:
                            article_data = json.load(f)
                            # Transform the article data into the format expected by frontend
                            transformed_article = {
                                "id": int(group_file.stem.split('_')[1]),  # Extract number from group_X.json
                                                            "group_id": group_file.stem,  # Use the filename as group_id
                            "headline": article_data.get("headline", ""),
                            "category": article_data.get("category", ""),
                            "content": article_data.get("lead", ""),  # Use lead as content
                            "summary": article_data.get("conclusion", ""),  # Use conclusion as summary
                            "date": date_dir.name,
                            "image_url": f"/static/images/{date_dir.name}/{group_file.stem}.jpg",
                                "subheadline": article_data.get("subheadline", ""),
                                "body": article_data.get("body", []),
                                "timeline": article_data.get("timeline", {}),
                                "sentiment": article_data.get("body", [{}])[0].get("sentisement_from_the_content", "0"),
                                "fake_news_probability": article_data.get("body", [{}])[0].get("fake_news_probability", 0)
                            }
                            all_news.append(transformed_article)
                            print(f"Successfully loaded article: {transformed_article['headline']}")
                    except Exception as e:
                        print(f"Error loading group file {group_file.name}: {str(e)}")
                        import traceback
                        print(f"Traceback: {traceback.format_exc()}")
        
        print(f"Total articles loaded: {len(all_news)}")
        return all_news
    except Exception as e:
        print(f"Error in load_news_data: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return []

def fuzzy_search_articles(articles: List[dict], search_term: str, threshold: int = 50) -> List[dict]:
    """
    Enhanced fuzzy search on articles with better typo tolerance
    """
    if not search_term:
        return articles
    
    search_term = search_term.lower().strip()
    scored_articles = []
    
    print(f"Fuzzy searching for: '{search_term}' with threshold {threshold}")
    
    for article in articles:
        # Get text fields to search
        headline = article.get('headline', '').lower()
        content = article.get('content', '').lower()
        summary = article.get('summary', '').lower()
        
        scores = []
        
        # Check headline with multiple algorithms
        if headline:
            scores.append(fuzz.ratio(search_term, headline))
            scores.append(fuzz.partial_ratio(search_term, headline))
            scores.append(fuzz.token_sort_ratio(search_term, headline))
            scores.append(fuzz.token_set_ratio(search_term, headline))
            
            # Check individual words in headline
            headline_words = headline.split()
            for word in headline_words:
                if len(word) > 2:
                    word_score = fuzz.ratio(search_term, word)
                    scores.append(word_score)
                    # Also check partial match within words
                    if len(search_term) > 3:
                        scores.append(fuzz.partial_ratio(search_term, word))
        
        # Check content with multiple algorithms
        if content:
            scores.append(fuzz.partial_ratio(search_term, content))
            scores.append(fuzz.token_set_ratio(search_term, content))
            
            # Check individual words in content (first 100 words to avoid slow performance)
            content_words = content.split()[:100]
            for word in content_words:
                if len(word) > 2:
                    word_score = fuzz.ratio(search_term, word)
                    if word_score > 70:  # Only add high-scoring word matches
                        scores.append(word_score)
        
        # Check summary
        if summary:
            scores.append(fuzz.partial_ratio(search_term, summary))
            scores.append(fuzz.token_set_ratio(search_term, summary))
        
        # Get the highest score
        max_score = max(scores) if scores else 0
        
        print(f"Article '{headline[:50]}...' scored {max_score}")
        
        # If score meets threshold, add to results
        if max_score >= threshold:
            scored_articles.append((article, max_score))
    
    # Sort by score (highest first)
    scored_articles.sort(key=lambda x: x[1], reverse=True)
    
    result_articles = [article for article, score in scored_articles]
    print(f"Fuzzy search returned {len(result_articles)} results")
    
    return result_articles

@router.get("/news")
async def get_news(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    category: Optional[str] = None,
    date: Optional[str] = None,
    sort: str = "newest",
    fuzzy: bool = Query(False, description="Enable fuzzy search")  # New parameter
):
    """
    Get news articles with filtering and pagination.
    """
    try:
        print(f"\n=== Processing /news request ===")
        print(f"Parameters: page={page}, per_page={per_page}, search={search}, category={category}, date={date}, sort={sort}")
        
        # Load news data
        news_data = load_news_data(date)
        print(f"Retrieved {len(news_data)} articles before filtering")
        
        # Apply search filter
        if search:
            if fuzzy:
                # Use fuzzy search
                news_data = fuzzy_search_articles(news_data, search, threshold=50)
            else:
                # Use exact search (existing logic)
                search = search.lower()
                news_data = [
                    article for article in news_data
                    if search in article.get('headline', '').lower() or
                       search in article.get('content', '').lower() or
                       search in article.get('summary', '').lower()
                ]
            print(f"After search filter: {len(news_data)} articles")
        
        # Apply category filter
        if category and category != 'all':
            # Load categories to map group_id to category
            static_dir = Path(__file__).parent.parent.parent.parent / "static"
            articles_dir = static_dir / "articles"
            
            # Find the most recent date directory for categories
            date_dirs = [d for d in articles_dir.iterdir() if d.is_dir()]
            if date_dirs:
                latest_date = max(date_dirs, key=lambda x: x.name)
                categories_file = latest_date / "group_categories.json"
                
                group_to_category = {}
                if categories_file.exists():
                    try:
                        with open(categories_file, 'r', encoding='utf-8') as f:
                            group_to_category = json.load(f)
                    except Exception as e:
                        print(f"Error loading categories for filtering: {str(e)}")
                
                # Filter articles based on actual category mapping
                filtered_news = []
                for article in news_data:
                    article_category = group_to_category.get(article.get('group_id', ''), '').lower()
                    if article_category == category.lower():
                        filtered_news.append(article)
                news_data = filtered_news
                print(f"After category filter ({category}): {len(news_data)} articles")
            else:
                # Fallback to original filtering if no categories file
                news_data = [
                    article for article in news_data
                    if article.get('category', '').lower() == category.lower()
                ]
                print(f"After fallback category filter: {len(news_data)} articles")
        
        # Sort news
        if sort == "newest":
            news_data.sort(key=lambda x: x.get('date', ''), reverse=True)
        elif sort == "oldest":
            news_data.sort(key=lambda x: x.get('date', ''))
        
        # Calculate pagination
        total = len(news_data)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_news = news_data[start_idx:end_idx]
        
        print(f"Returning {len(paginated_news)} articles for page {page}")
        print("=== End of /news request ===\n")
        
        return {
            "news": paginated_news,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page
        }
    except Exception as e:
        print(f"Error in get_news: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching news: {str(e)}"
        )

@router.get("/news/categories")
async def get_categories():
    """
    Get all available news categories from group_categories.json.
    """
    try:
        static_dir = Path(__file__).parent.parent.parent / "static"
        articles_dir = static_dir / "articles"
        
        print(f"Looking for articles in: {articles_dir.absolute()}")
        
        # Find the most recent date directory
        date_dirs = [d for d in articles_dir.iterdir() if d.is_dir()]
        if not date_dirs:
            print("No date directories found in articles directory")
            return {"categories": {
                "social": "social",
                "entertainment": "entertainment",
                "tech": "tech",
                "sport": "sport"
            }, "total": 4}
            
        latest_date = max(date_dirs, key=lambda x: x.name)
        print(f"Latest date directory: {latest_date}")
        
        categories_file = latest_date / "group_categories.json"
        print(f"Looking for categories file: {categories_file.absolute()}")
        
        if not categories_file.exists():
            print(f"Categories file not found at: {categories_file}")
            return {"categories": {
                "social": "social",
                "entertainment": "entertainment",
                "tech": "tech",
                "sport": "sport"
            }, "total": 4}
            
        # Read and parse the categories file
        try:
            with open(categories_file, 'r', encoding='utf-8') as f:
                group_categories = json.load(f)
                print(f"Successfully loaded categories: {group_categories}")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from categories file: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Invalid categories file format: {str(e)}"
            )
        except Exception as e:
            print(f"Error reading categories file: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error reading categories file: {str(e)}"
            )
            
        # Get unique categories
        unique_categories = sorted(set(group_categories.values()))
        print(f"Unique categories found: {unique_categories}")
        
        # Create category dictionary
        category_dict = {cat: cat for cat in unique_categories}
        
        return {
            "categories": category_dict,
            "total": len(category_dict)
        }
    except Exception as e:
        print(f"Error in get_categories: {str(e)}")
        # Return default categories instead of raising an error
        return {"categories": {
            "social": "social",
            "entertainment": "entertainment",
            "tech": "tech",
            "sport": "sport"
        }, "total": 4}

@router.get("/news/articles/{date}/{group_id}")
async def get_article(date: str, group_id: str):
    """Get a specific article by date and group ID"""
    try:
        print(f"\n=== Processing /news/articles/{date}/{group_id} request ===")
        
        # Get the absolute path to the static directory
        static_dir = Path(__file__).parent.parent.parent.parent / "static"
        articles_dir = static_dir / "articles"
        date_dir = articles_dir / date
        
        print(f"Looking for article in: {date_dir.absolute()}")
        print(f"Date directory exists: {date_dir.exists()}")
        
        if not date_dir.exists():
            print(f"Date directory not found: {date}")
            raise HTTPException(status_code=404, detail="Article not found")
        
        # Load the specific article file
        article_file = date_dir / f"{group_id}.json"
        print(f"Article file path: {article_file.absolute()}")
        print(f"Article file exists: {article_file.exists()}")
        
        if not article_file.exists():
            print(f"Article file not found: {group_id}.json")
            raise HTTPException(status_code=404, detail="Article not found")
        
        try:
            with open(article_file, 'r', encoding='utf-8') as f:
                article_data = json.load(f)
                
                # Load categories
                categories_file = date_dir / "group_categories.json"
                category = "general"
                if categories_file.exists():
                    try:
                        with open(categories_file, 'r', encoding='utf-8') as cf:
                            categories = json.load(cf)
                            category = categories.get(group_id, "general")
                    except Exception as e:
                        print(f"Error loading categories: {str(e)}")
                
                # Transform the article data into the format expected by frontend
                transformed_article = {
                    "id": int(group_id.split('_')[1]),  # Extract number from group_X
                    "group_id": group_id,
                    "headline": article_data.get("headline", ""),
                    "category": category,
                    "content": article_data.get("lead", ""),  # Use lead as content
                    "summary": article_data.get("conclusion", ""),  # Use conclusion as summary
                    "date": date,
                    "image_url": f"/static/images/{date}/{group_id}.jpg",
                    "subheadline": article_data.get("subheadline", ""),
                    "body": article_data.get("body", []),
                    "timeline": article_data.get("timeline", {}),
                    "sentiment": article_data.get("body", [{}])[0].get("sentisement_from_the_content", "0") if article_data.get("body") else "0",
                    "fake_news_probability": article_data.get("body", [{}])[0].get("fake_news_probability", 0) if article_data.get("body") else 0,
                    "lead": article_data.get("lead", ""),
                    "conclusion": article_data.get("conclusion", ""),
                    "cover_image_prompt": article_data.get("cover_image_prompt", ""),
                    "event_id_list": article_data.get("event_id_list", []),
                    "post_id_list": article_data.get("post_id_list", []),
                    "comment_id_list": article_data.get("comment_id_list", [])
                }
                
                print(f"Successfully loaded article: {transformed_article['headline']}")
                print("=== End of /news/articles request ===\n")
                
                return transformed_article
                
        except Exception as e:
            print(f"Error loading article file: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail="Failed to load article")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_article: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Failed to fetch article") 

@router.get("/test-fuzzy")
async def test_fuzzy_search(
    search: str = Query(..., description="Search term to test"),
    threshold: int = Query(50, description="Fuzzy search threshold")
):
    """Test fuzzy search functionality"""
    try:
        from fuzzywuzzy import fuzz
        
        # Test with some sample data
        test_articles = [
            {"headline": "Trump announces new policy", "content": "Former president Trump...", "summary": "Trump policy news"},
            {"headline": "Biden administration updates", "content": "President Biden...", "summary": "Biden news"},
            {"headline": "Technology advances", "content": "New tech developments...", "summary": "Tech news"},
        ]
        
        results = fuzzy_search_articles(test_articles, search, threshold)
        
        return {
            "search_term": search,
            "threshold": threshold,
            "results_count": len(results),
            "results": [{"headline": r["headline"], "score": "calculated"} for r in results],
            "fuzzywuzzy_available": True,
            "test_scores": {
                "Trump vs trump": fuzz.ratio("trump", "trump"),
                "Trump vs trunp": fuzz.ratio("trump", "trunp"),
                "Trump vs trumpp": fuzz.ratio("trump", "trumpp"),
            }
        }
    except ImportError:
        return {
            "error": "fuzzywuzzy not installed",
            "fuzzywuzzy_available": False
        } 