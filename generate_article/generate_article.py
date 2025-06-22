import pandas as pd
import json
import os
from datetime import datetime
from pathlib import Path
import sys
from typing import Dict, List, Optional, Union
import ast
import time
from config.group_settings import get_max_group_size

project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Use relative import
from llm_client import LLMClient
from generate_article.prompt import get_prompt_templates, format_prompt
import argparse

def generate_article(date_str: str):
    """Generate article for a given date"""
    group_df = pd.read_csv(f'data/group/{date_str}/group_result.csv')

    group_id_list = list(group_df['group_id'])

    for group_id in group_id_list:
        # Check group size and skip if too large
        group_row = group_df[group_df['group_id'] == group_id]
        group_size = group_row.iloc[0]['size']
        
        # Import configuration
        MAX_GROUP_SIZE = 60  # Fallback default
            
        if group_size > MAX_GROUP_SIZE:
            print(f"Skipping Group {group_id} - too large (size: {group_size}, max: {MAX_GROUP_SIZE})")
            continue

        output_file_path = Path(f"data/output/article/group_{group_id}.json")
        if output_file_path.exists():
            print(f"Skipping Group {group_id} - output file already exists: {output_file_path}")
            continue

        small_group_df = group_df[group_df['group_id'] == group_id]

        event_id_list = ast.literal_eval(small_group_df.iloc[0]['event_ids'])
        post_id_list = ast.literal_eval(small_group_df.iloc[0]['post_ids'])

        def get_event_by_id(event_id_list, date):
            df = pd.read_csv(f'data/card/event_card/{date}.csv')
            return df[df['event_id'].isin(event_id_list)]

        def get_post_by_id(post_id_list, date):
            df = pd.read_csv(f'data/card/statement_card/posts/{date}.csv')
            return df[df['post_id'].isin(post_id_list)]
    
        def get_article_by_url(url_list, date):
            # Find all CSV files with the date in any subfolder
            fundus_dir = Path('data/raw/fundus')
            csv_files = list(fundus_dir.rglob(f'{date}.csv'))
            if not csv_files:
                print(f"No CSV file found for date {date}")
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
    
        def get_comment_by_id(post_id_list, date):
            df = pd.read_csv(f'data/card/statement_card/comments/{date}.csv')
            return df[df['post_id'].isin(post_id_list)]
        
        event_df = get_event_by_id(event_id_list, date_str)
        url_list = list(set(event_df['link']))
        post_df = get_post_by_id(post_id_list, date_str)
        comment_df = get_comment_by_id(post_id_list, date_str)
        article_df = get_article_by_url(url_list, date_str)

        # Convert DataFrames to JSON format suitable for LLM prompt
        events_json = json.dumps(event_df.to_dict('records'), indent=2, default=str)
        posts_json = json.dumps(post_df.to_dict('records'), indent=2, default=str) 
        comments_json = json.dumps(comment_df.to_dict('records'), indent=2, default=str)

        system_prompt = get_prompt_templates()[0]
        prompt = format_prompt(
            events=events_json,
            posts=posts_json,
            comments=comments_json
        )

        client = LLMClient(publisher='ALIBABA')

        print("\nSending request to LLM...")
        try:
            response = client.generate(
                prompt_content=prompt,
                system_content=system_prompt,
                model="qwen-plus",
                timeout=300  # 120 seconds timeout
            )
            
            print("\nReceived response from LLM")
            article = json.loads(response.choices[0].message.content)
        except Exception as e:
            if "timeout" in str(e).lower():
                print(f"Timeout error for Group {group_id}: {e}")
                print("Skipping this group and continuing...")
                continue
            else:
                print(f"Error for Group {group_id}: {e}")
                print("Skipping this group and continuing...")
                continue
        
        print('saving...')

        # Ensure output directory exists
        output_dir = Path(f"data/output/article/{date_str}")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / f"group_{group_id}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(article, f, indent=2, ensure_ascii=False)
        print(f"Article saved to: {output_file}")

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='Generate news articles from grouped data')
    parser.add_argument('--date', type=str, required=True, help='Date in YYYY-MM-DD format')
    args = parser.parse_args()
    
    try:
        generate_article(args.date)
        print("Article generation completed!")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()