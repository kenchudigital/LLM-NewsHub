#!/usr/bin/env python3
"""
Resource Gathering Script

This script gathers detailed content from events, posts, comments, and articles
for each group and outputs them as JSON files to data/output/resource/{date}/group_{group_id}.json
"""

import os
import sys
import json
import ast
import argparse
from pathlib import Path
import pandas as pd

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def get_event_by_id(event_id_list, date):
    """Get events by their IDs"""
    try:
        df = pd.read_csv(f'data/card/event_card/{date}.csv')
        return df[df['event_id'].isin(event_id_list)]
    except FileNotFoundError:
        print(f"Warning: Event card file not found for date {date}")
        return pd.DataFrame()
    except Exception as e:
        print(f"Error reading event card: {e}")
        return pd.DataFrame()

def get_post_by_id(post_id_list, date):
    """Get posts by their IDs"""
    try:
        df = pd.read_csv(f'data/card/statement_card/posts/{date}.csv')
        return df[df['post_id'].isin(post_id_list)]
    except FileNotFoundError:
        print(f"Warning: Post card file not found for date {date}")
        return pd.DataFrame()
    except Exception as e:
        print(f"Error reading post card: {e}")
        return pd.DataFrame()

def get_comment_by_id(post_id_list, date):
    """Get comments by post IDs"""
    try:
        df = pd.read_csv(f'data/card/statement_card/comments/{date}.csv')
        return df[df['post_id'].isin(post_id_list)]
    except FileNotFoundError:
        print(f"Warning: Comment card file not found for date {date}")
        return pd.DataFrame()
    except Exception as e:
        print(f"Error reading comment card: {e}")
        return pd.DataFrame()

def get_article_by_url(url_list, date):
    """Get articles by their URLs"""
    # Find all CSV files with the date in any subfolder
    fundus_dir = Path('data/raw/fundus')
    csv_files = list(fundus_dir.rglob(f'{date}.csv'))
    
    if not csv_files:
        print(f"Warning: No fundus CSV file found for date {date}")
        return pd.DataFrame()

    # Read and combine all matching CSV files
    dfs = []
    for file in csv_files:
        try:
            df = pd.read_csv(file)
            dfs.append(df)
        except Exception as e:
            print(f"Error reading {file}: {e}")
            continue
    
    if not dfs:
        return pd.DataFrame()
    
    # Combine all dataframes
    combined_df = pd.concat(dfs, ignore_index=True)
    
    # Filter by url_list
    return combined_df[combined_df['link'].isin(url_list)]

def gather_resources_for_group(group_id, group_data, date_str):
    """Gather all resources for a specific group"""
    print(f"Gathering resources for Group {group_id}...")
    
    # Parse the IDs from string representation
    try:
        event_id_list = ast.literal_eval(group_data['event_ids']) if pd.notna(group_data['event_ids']) else []
        post_id_list = ast.literal_eval(group_data['post_ids']) if pd.notna(group_data['post_ids']) else []
    except (ValueError, SyntaxError) as e:
        print(f"Error parsing IDs for group {group_id}: {e}")
        return None
    
    print(f"Event IDs: {len(event_id_list)}")
    print(f"Post IDs: {len(post_id_list)}")
    
    # Get data from different sources
    event_df = get_event_by_id(event_id_list, date_str)
    post_df = get_post_by_id(post_id_list, date_str)
    comment_df = get_comment_by_id(post_id_list, date_str)
    
    # Get articles from event URLs
    url_list = list(set(event_df['link'].dropna())) if not event_df.empty else []
    article_df = get_article_by_url(url_list, date_str)
    
    # Convert DataFrames to JSON format
    detailed_content = {
        "group_id": int(group_id),
        "date": date_str,
        "summary": {
            "events_count": len(event_df),
            "posts_count": len(post_df),
            "comments_count": len(comment_df),
            "articles_count": len(article_df),
            "total_items": len(event_df) + len(post_df) + len(comment_df) + len(article_df)
        },
        "events": event_df.to_dict('records') if not event_df.empty else [],
        "posts": post_df.to_dict('records') if not post_df.empty else [],
        "comments": comment_df.to_dict('records') if not comment_df.empty else [],
        "articles": article_df.to_dict('records') if not article_df.empty else []
    }
    
    return detailed_content

def gather_resources(date_str: str):
    """Gather resources for all groups on a given date"""
    print(f"Starting resource gathering for date: {date_str}")
    
    # Read group result data
    group_file = f'data/group/{date_str}/group_result.csv'
    if not Path(group_file).exists():
        print(f"Group result file not found: {group_file}")
        return
    
    try:
        group_df = pd.read_csv(group_file)
        print(f"Found {len(group_df)} groups to process")
    except Exception as e:
        print(f"Error reading group file: {e}")
        return
    
    # Create output directory
    output_dir = Path(f"data/output/resource/{date_str}")
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {output_dir}")
    
    # Process each group
    processed_count = 0
    skipped_count = 0
    error_count = 0
    
    for idx, row in group_df.iterrows():
        group_id = row['group_id']
        output_file = output_dir / f"group_{group_id}.json"
        
        # Skip if output file already exists
        if output_file.exists():
            print(f"Skipping Group {group_id} - output file already exists")
            skipped_count += 1
            continue
        
        try:
            # Gather resources for this group
            detailed_content = gather_resources_for_group(group_id, row, date_str)
            
            if detailed_content is None:
                print(f"Failed to gather resources for Group {group_id}")
                error_count += 1
                continue
            
            # Save to JSON file
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(detailed_content, f, indent=2, ensure_ascii=False, default=str)
            
            print(f"Group {group_id} resources saved to {output_file}")
            processed_count += 1
            
        except Exception as e:
            print(f"Error processing Group {group_id}: {e}")
            error_count += 1
            continue
    

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Gather detailed resources for article groups')
    parser.add_argument('--date', type=str, required=True,
                      help='Date to process (YYYY-MM-DD format)')
    
    args = parser.parse_args()
    
    # Validate date format
    try:
        from datetime import datetime
        datetime.strptime(args.date, '%Y-%m-%d')
    except ValueError:
        print("Invalid date format. Please use YYYY-MM-DD format.")
        return
    
    gather_resources(args.date)

if __name__ == "__main__":
    main()


