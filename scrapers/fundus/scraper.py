"""
Fundus Scraper

Output:
    data/raw/fundus/{date}.csv
"""

import fundus.parser
fundus.parser.parser_class = "html.parser"
from fundus import Crawler, PublisherCollection, Requires

import os
import sys
import json
import time
import datetime
import argparse
import pandas as pd
from tqdm import tqdm
from langdetect import detect
from dotenv import load_dotenv
from typing import List, Dict, Optional, Union, Any
import signal
from contextlib import contextmanager

def get_publisher(publisher_str: str):
    country, publisher_name = publisher_str.split('.')
    collection = getattr(PublisherCollection, country.lower())
    return getattr(collection, publisher_name)

def detect_language(text: str) -> str:
    return detect(text) if text else 'unknown'

def parse_datetime(dt_str: Optional[str]) -> Optional[datetime.datetime]:
    if not dt_str:
        return None
    try:
        return pd.to_datetime(dt_str, format='ISO8601')
    except ValueError:
        return None

def is_within_date_range(date_str: Optional[str], start: Optional[str], end: Optional[str]) -> bool:
    if not date_str:
        return True  
    try:
        date = parse_datetime(date_str)
        if not date:
            return True   
        date = date.date()
        if start:
            start_date = pd.to_datetime(start).date()
            if date < start_date:
                return False
        if end:
            end_date = pd.to_datetime(end).date()
            if date > end_date:
                return False
        return True
    except (ValueError, TypeError):
        return True 

def process_media_links(media_data) -> List[dict]:
    processed_media = []
    for media_item in media_data:
        try:
            media_type = 'unknown' 
            media_dict = {}
            
            if isinstance(media_item, str):
                lines = media_item.split('\n')
                for line in lines:
                    if 'URL:' in line:
                        media_dict['url'] = line.split("'")[1].strip("'")
                    elif 'Description:' in line:
                        media_dict['description'] = line.split(':', 1)[1].strip()
                    elif 'Caption:' in line:
                        media_dict['caption'] = line.split(':', 1)[1].strip()
                    elif 'Versions:' in line:
                        versions = line.split('[')[1].split(']')[0].split(',')
                        if versions:
                            largest_version = versions[-1].strip()
                            if 'x' in largest_version:
                                try:
                                    media_dict['width'] = int(largest_version.split('x')[0])
                                except ValueError:
                                    pass
                if 'Fundus-Article Cover-Image' in media_item:
                    media_type = 'cover_image'
                elif 'Fundus-Article Image' in media_item:
                    media_type = 'article_image'
                
            elif isinstance(media_item, dict):
                media_dict = {
                    'url': media_item.get('url', ''),
                    'description': media_item.get('description', ''),
                    'caption': media_item.get('caption', ''),
                }
                if 'versions' in media_item:
                    versions = media_item['versions']
                    if versions and isinstance(versions, list):
                        largest = versions[-1]
                        if isinstance(largest, dict) and 'url' in largest:
                            media_dict['url'] = largest['url']
                            if 'width' in largest:
                                media_dict['width'] = largest['width']
                if 'Fundus-Article Cover-Image' in str(media_item):
                    media_type = 'cover_image'
                elif 'Fundus-Article Image' in str(media_item):
                    media_type = 'article_image'
            if 'url' in media_dict and media_dict['url']:
                processed_media.append({
                    'url': media_dict['url'],
                    'description': media_dict.get('description', ''),
                    'caption': media_dict.get('caption', ''),
                    'width': media_dict.get('width', None),
                    'type': media_type  # Include the media type
                })       
        except Exception as e:
            print(f"Error processing media item: {str(e)}")
            continue
    return processed_media


def extract_url_categories(url: str) -> Dict[str, str]:
    try:
        info = [a for a in url.split('/') if a not in ['https:', 'http:', '', '.com']]
        domain_candidates = [i for i in info if any(x in i for x in ['www', 'co.jp', '.'])]
        domain = domain_candidates[0] if domain_candidates else 'unknown'
        info_without_domain = [k for k in info if domain not in k]
        category = info_without_domain[0] if len(info_without_domain) > 0 else 'general'
        sub_category = info_without_domain[1] if len(info_without_domain) > 1 else 'news'
        return {
            'category': category,
            'sub_category': sub_category,
            'domain': domain
        }
    except Exception:
        return {
            'category': 'general',
            'sub_category': 'news',
            'domain': 'unknown'
        }

def date_filter(extracted: Dict[str, Any]) -> bool:
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=1)
    if publishing_date := extracted.get("publishing_date"):
        return not (start_date <= publishing_date.date() <= end_date)
    return True

@contextmanager
def timeout(seconds):
    """Context manager for timeout"""
    def signal_handler(signum, frame):
        raise TimeoutError(f"Operation timed out after {seconds} seconds")
    
    # Set the signal handler
    old_handler = signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    
    try:
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)

def scrape_articles(
    publishers: Union[str, List[str]],
    max_articles: int = 10,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    timeout_seconds: int = 180,  # 3 minutes timeout per publisher
) -> pd.DataFrame:
    if isinstance(publishers, str):
        publishers = [publishers]
    
    all_articles = []
    total_publishers = len(publishers)
    
    with tqdm(total=total_publishers, desc="Scraping publishers") as pbar:
        for publisher_str in publishers:
            try:
                publisher_country = publisher_str.split('.')[0]
                publisher_name = publisher_str.split('.')[1]
                publisher_obj = get_publisher(publisher_str)

                crawler = Crawler(publisher_obj) 
                articles_found = 0
                start_time = time.time()

                pbar.set_description(f"Scraping {publisher_name}")
                
                try:
                    # Add timeout to the crawler loop
                    with timeout(timeout_seconds):
                        for article in crawler.crawl(
                            max_articles=max_articles, 
                            error_handling='suppress',
                            only_complete=date_filter
                        ):
                            # Check if we've exceeded timeout
                            if time.time() - start_time > timeout_seconds:
                                print(f"Timeout reached for {publisher_name}, moving to next publisher")
                                break
                                
                            time.sleep(1)
                            try:
                                title = getattr(article, 'title', '')
                                plaintext = getattr(article, 'plaintext', '')
                                topic = getattr(article, 'topics', '')
                                url = getattr(getattr(article, 'html', None), 'requested_url', '')
                                publish_time = None
                                if hasattr(article, 'publishing_date') and article.publishing_date:
                                    publish_time = article.publishing_date.isoformat()
                                if not is_within_date_range(publish_time, start_date, end_date):
                                    continue

                                media_links = []
                                
                                try:
                                    if hasattr(article, 'images'):
                                        images = article.images
                                        if isinstance(images, list):
                                            media_links.extend(
                                                img['url'] if isinstance(img, dict) and 'url' in img else str(img)
                                                for img in images
                                            )
                                except Exception as e:
                                    pass
                                    
                                language = detect_language(f"{title} {plaintext}".strip()) if title or plaintext else 'en'

                                try:
                                    processed_media_links = process_media_links(media_links)
                                except Exception:
                                    processed_media_links = []
                                url_categories = extract_url_categories(url)

                                article_data = {
                                    'title': title,
                                    'content': plaintext,
                                    'topic': topic,
                                    'publish_time': publish_time,
                                    'link': url,
                                    'publisher': publisher_name,
                                    'publisher_country': publisher_country,
                                    'language': language,
                                    'media_links': json.dumps(processed_media_links),
                                    'extract_time': datetime.datetime.now().isoformat(),
                                    'word_count': len(plaintext.split()) if plaintext else 0,
                                    'url_category': url_categories['category'],
                                    'url_sub_category': url_categories['sub_category'],
                                    'url_domain': url_categories['domain']
                                }
                                
                                all_articles.append(article_data)
                                articles_found += 1
                                print(f"Found article {articles_found} for {publisher_name}")
                                
                                if articles_found >= max_articles:
                                    print(f"Reached max articles ({max_articles}) for {publisher_name}")
                                    break
                                    
                            except Exception as e:
                                print(f"Error processing article: {str(e)}")
                                continue
                                
                except TimeoutError:
                    print(f"Timeout reached for {publisher_name} after {timeout_seconds} seconds")
                except Exception as e:
                    print(f"Error in crawler loop for {publisher_name}: {str(e)}")
                
                pbar.update(1)
                pbar.set_postfix({'articles': articles_found})
                    
            except Exception as e:
                print(f"Error processing publisher {publisher_str}: {str(e)}")
                pbar.update(1)
                continue
    
    df = pd.DataFrame(all_articles)

    if not df.empty:
        df['publish_time'] = pd.to_datetime(df['publish_time'], format='ISO8601', utc=True)
        df['extract_time'] = pd.to_datetime(df['extract_time'], format='ISO8601', utc=True)
        df = df.sort_values(by='publish_time', ascending=False, na_position='last')
        df = df.reset_index(drop=True)  
    return df

def save_data(df: pd.DataFrame) -> str:
    if df.empty:
        return "No data to save"
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    os.makedirs(f'data/raw/fundus/{today}', exist_ok=True)

    df['publish_date'] = df['publish_time'].dt.date
    
    for date, group in df.groupby('publish_date'):
        date_str = date.strftime("%Y-%m-%d")
        filename = f'data/raw/fundus/{today}/{date_str}.csv'
        group.to_csv(filename, index=False)
        

def main(publishers, start_date, end_date, max_articles):
    df = pd.DataFrame()

    df = scrape_articles(
        publishers=publishers,  
        max_articles=max_articles,
        start_date=start_date,  
        end_date=end_date    
    )
    
    if df.empty:
        raise Exception("No articles found")
        
    save_data(df)
        

if __name__ == "__main__":    
    sys.path.append('../..')
    load_dotenv()
    
    parser = argparse.ArgumentParser(description='Fundus News Scraper')
    parser.add_argument('--date', type=str, help='Specific date to scrape (YYYY-MM-DD format). If provided, this will set both start and end date to this date.')
    args = parser.parse_args()
    
    PUBLISHER_LIST = os.getenv('PUBLISHER_LIST').split(',')
    FUNDUS_MAX_ARTICLES = int(os.getenv('FUNDUS_MAX_ARTICLES'))

    end_date = datetime.datetime.strptime(args.date, '%Y-%m-%d')
    start_date = end_date - datetime.timedelta(days=1)
    
    # Convert back to YYYY-MM-DD format
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = args.date
    print('start_date_str', start_date_str)
    print('end_date_str', end_date_str)
    
    main(
        publishers=PUBLISHER_LIST, 
        start_date=start_date_str, 
        end_date=end_date_str, 
        max_articles=FUNDUS_MAX_ARTICLES
    ) 