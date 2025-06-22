#!/usr/bin/env python3
"""
Reddit Data Scraper

ENV VAR:
    - REDDIT_ID
    - REDDIT_KEY
    - SUBREDDIT_LIST
    - REDDIT_MAX_POST
    - REDDIT_MAX_COMMENT

Input: None

Output: 
    - data/raw/reddit/extract_date/posts/publish_date_time.csv
    - data/raw/reddit/extract_date/comments/publish_date_time.csv

Usage:
    if there is unfortunate interruption, you can resume the scraping by using the --mode 1 argument.
    python scrapers/reddit/scraper.py --mode 1
"""

SLEEP_TIME_LONG = 2
SLEEP_TIME_SHORT = 1

import sys
import os
import time
import argparse
from dotenv import load_dotenv
from datetime import datetime, timezone

import re
import pandas as pd
from langdetect import detect
from tqdm import tqdm

import praw

def detect_language(text):
    try:
        return detect(text) if text else 'unknown'
    except:
        return 'unknown'

# temp_comments is for resuming the scraping !
def resume_scraping(reddit, max_comments):
    if not (os.path.exists('temp_posts.csv') and os.path.exists('temp_comments.csv')):
        return None, None, "No temporary files found to resume from"

    try:
        posts_df = pd.read_csv('temp_posts.csv')
        posts_df['publish_time_utc'] = pd.to_datetime(posts_df['publish_time_utc'])
        posts_df['publish_date_utc'] = posts_df['publish_time_utc'].dt.date
        
        all_comments = pd.read_csv('temp_comments.csv')
        
        processed_post_ids = set(all_comments['post_id'].unique())
        id_list = list(posts_df['post_id'])
        date_list = list(posts_df['publish_date_utc'])
        
        remaining_posts = [(i, post_id, date) for i, (post_id, date) in enumerate(zip(id_list, date_list)) 
                          if post_id not in processed_post_ids]
        
        if not remaining_posts:
            return posts_df, all_comments, "All posts have been processed"
            
        for i, post_id, temp_date in tqdm(remaining_posts, desc="Resuming comment collection"):
            time.sleep(SLEEP_TIME_LONG) 
            submission = reddit.submission(post_id)
            all_comments_for_post = submission.comments.list()
            
            comments_data = []
            for comment in all_comments_for_post[:max_comments]:
                time.sleep(SLEEP_TIME_SHORT)
                
                author = comment.author
                author_name = author.name if author else "[deleted]"
                author_id = getattr(author, 'id', None) if author else None
                
                try:
                    author_post_karma = comment.author.link_karma if comment.author else None
                except:
                    author_post_karma = None
                try:
                    author_comment_karma = comment.author.comment_karma if comment.author else None
                except:
                    author_comment_karma = None

                if author_name and not author_post_karma:
                    try:
                        author_post_karma = reddit.redditor(author_name).link_karma
                        author_comment_karma = reddit.redditor(author_name).comment_karma
                    except:
                        pass

                comment_body = comment.body
                media_links = []
                if "http" in comment_body:
                    media_links = re.findall(r'(https?://[^\s]+)', comment_body)

                comments_data.append({
                    "post_id": post_id,
                    "comment_id": comment.id,
                    "extract_time": datetime.now(timezone.utc).isoformat(),
                    "comment_body": comment_body,
                    "category": "",
                    "language": detect_language(comment_body),
                    "comment_created_utc": datetime.fromtimestamp(comment.created_utc).isoformat(),
                    "comment_permalink": f"https://reddit.com{comment.permalink}",
                    "media_links": media_links,
                    "comment_ups": comment.ups,
                    "comment_score": comment.score,
                    "location": "",
                    "commenter_name": author_name,
                    "commenter_id": author_id,
                    "commenter_post_karma": author_post_karma,
                    "commenter_comment_karma": author_comment_karma,    
                    "comment_parent_id": comment.parent_id,
                    "publish_date_utc": temp_date
                })
            
            df_comments = pd.DataFrame(comments_data)
            all_comments = pd.concat([all_comments, df_comments], ignore_index=True)
            all_comments.to_csv('temp_comments.csv', index=False)
        
        return posts_df, all_comments, f"Successfully resumed scraping for {len(remaining_posts)} posts"
    except Exception as e:
        return None, None, f"Error during resume: {str(e)}"

def get_reddit_data(subreddit_list, max_posts, max_comments, reddit, resume_mode=False):
    if resume_mode:
        posts_df, all_comments, message = resume_scraping(reddit, max_comments)
        if posts_df is None:
            print(message)
            return message
    else:
        extract_time = datetime.now(timezone.utc)
        extract_date = extract_time.strftime('%Y-%m-%d')
        posts = []

    if not resume_mode:
        for item in tqdm(subreddit_list, desc=f"Collecting posts from Subreddits List, {max_posts} posts / subreddits"):
            subreddit = reddit.subreddit(item)
            for post in subreddit.hot(limit=max_posts):
                
                time.sleep(SLEEP_TIME_LONG)
                
                temp_time = datetime.fromtimestamp(post.created_utc)
                author_name = post.author.name if post.author else "[deleted]"
                author_id = getattr(post.author, 'id', None) if post.author else None
                
                try:
                    author_post_karma = post.author.link_karma if post.author else None
                except:
                    author_post_karma = None
                
                try:
                    author_comment_karma = post.author.comment_karma if post.author else None
                except:
                    author_comment_karma = None
                
                post_json = {
                    'post_id': post.id,
                    'extract_time': datetime.now(timezone.utc).isoformat(),
                    'source': 'Reddit',
                    'topic/subreddit': str(post.subreddit),
                    'title': post.title,
                    'content': post.selftext,
                    'category': '',
                    'language': detect_language(post.title + ' ' + post.selftext),
                    'publish_time_utc': temp_time.isoformat(),
                    'link': f"https://reddit.com{post.permalink}",
                    'image/video': post.url,
                    'ups': post.ups,
                    'upvote_ratio': post.upvote_ratio,
                    'score': post.score,
                    'location': '',
                    'num_comments': post.num_comments,
                    'author_id': author_id,
                    'author_name': author_name,
                    'author_post_karma': author_post_karma,
                    'author_comment_karma': author_comment_karma
                }
                posts.append(post_json)
        
        posts_df = pd.DataFrame(posts)
        posts_df['publish_time_utc'] = pd.to_datetime(posts_df['publish_time_utc'])
        posts_df['publish_date_utc'] = posts_df['publish_time_utc'].dt.date

        posts_df.to_csv('temp_posts.csv', index=False)

        all_comments = pd.DataFrame()
        id_list = list(posts_df['post_id'])
        date_list = list(posts_df['publish_date_utc'])


        for i, post_id in tqdm(enumerate(id_list), total=len(id_list), desc="Collecting comments"):
            time.sleep(SLEEP_TIME_LONG)  
            temp_date = date_list[i]  
            submission = reddit.submission(post_id)
            all_comments_for_post = submission.comments.list()
        
            comments_data = []
            for comment in all_comments_for_post[:max_comments]:
                
                time.sleep(SLEEP_TIME_SHORT)
                author = comment.author
                author_name = author.name if author else "[deleted]"
                author_id = getattr(author, 'id', None) if author else None
                
                try:
                    author_post_karma = comment.author.link_karma if comment.author else None
                except:
                    author_post_karma = None
                try:
                    author_comment_karma = comment.author.comment_karma if comment.author else None
                except:
                    author_comment_karma = None

                if author_name and not author_post_karma:
                    try:
                        author_post_karma = reddit.redditor(author_name).link_karma
                        author_comment_karma = reddit.redditor(author_name).comment_karma
                    except:
                        pass

                comment_body = comment.body
                media_links = []
                if "http" in comment_body:
                    media_links = re.findall(r'(https?://[^\s]+)', comment_body)

                comments_data.append({
                    "post_id": post_id,
                    "comment_id": comment.id,
                    "extract_time": datetime.now(timezone.utc).isoformat(),
                    "comment_body": comment_body,
                    "category": "",
                    "language": detect_language(comment_body),
                    "comment_created_utc": datetime.fromtimestamp(comment.created_utc).isoformat(),
                    "comment_permalink": f"https://reddit.com{comment.permalink}",
                    "media_links": media_links,
                    "comment_ups": comment.ups,
                    "comment_score": comment.score,
                    "location": "",
                    "commenter_name": author_name,
                    "commenter_id": author_id,
                    "commenter_post_karma": author_post_karma,
                    "commenter_comment_karma": author_comment_karma,    
                    "comment_parent_id": comment.parent_id,
                    "publish_date_utc": temp_date
                })
            
            df_comments = pd.DataFrame(comments_data)
            all_comments = pd.concat([all_comments, df_comments], ignore_index=True)
            all_comments.to_csv('temp_comments.csv', index=False)
        
    # Move file saving logic outside the if/else block
    extract_date = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    base_dir = 'data/raw/reddit'
    posts_dir = os.path.join(base_dir, extract_date, 'posts')
    comments_dir = os.path.join(base_dir, extract_date, 'comments')
    os.makedirs(posts_dir, exist_ok=True)
    os.makedirs(comments_dir, exist_ok=True)
    
    try:
        for date, group in posts_df.groupby('publish_date_utc'):
            timestamp = date.strftime('%Y-%m-%d-%H%M')
            posts_path = os.path.join(posts_dir, f'{timestamp}.csv')
            group.to_csv(posts_path, index=False)

        for date, group in all_comments.groupby('publish_date_utc'):
            timestamp = pd.to_datetime(date).strftime('%Y-%m-%d-%H%M')
            comments_path = os.path.join(comments_dir, f'{timestamp}.csv')
            group.to_csv(comments_path, index=False)
        
        os.remove('temp_posts.csv')
        os.remove('temp_comments.csv')
        
        return f'Files saved to {posts_dir} and {comments_dir}'
    except Exception as e:
        return f"Error saving files: {str(e)}"

def main():
    parser = argparse.ArgumentParser(description='Reddit Data Scraper')
    parser.add_argument('--mode', type=int, default=0, choices=[0, 1],
                      help='Mode: 0 for new scraping, 1 for resume scraping')
    args = parser.parse_args()

    sys.path.append('../..')
    load_dotenv()

    REDDIT_ID = os.getenv('REDDIT_ID')
    REDDIT_KEY = os.getenv('REDDIT_KEY')
    reddit = praw.Reddit(client_id=REDDIT_ID, client_secret=REDDIT_KEY, user_agent="FakeNewsDetector/1.0")
    
    SUBREDDIT_LIST = os.getenv('SUBREDDIT_LIST').split(',')
    REDDIT_MAX_POST = int(os.getenv('REDDIT_MAX_POST'))
    REDDIT_MAX_COMMENT = int(os.getenv('REDDIT_MAX_COMMENT'))

    message = get_reddit_data(
        subreddit_list=SUBREDDIT_LIST,
        max_posts=REDDIT_MAX_POST,
        max_comments=REDDIT_MAX_COMMENT,
        reddit=reddit,
        resume_mode=args.mode == 1
    )
    
    print(message)

if __name__ == "__main__":
    main()
