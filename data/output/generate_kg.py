#!/usr/bin/env python3
"""
Knowledge Graph Generator Script
Processes article and resource data to create a comprehensive dataset.
Creates one row per event by left joining article data with resource data.
"""

import json
import os
import pandas as pd
from pathlib import Path
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_json_file(file_path):
    """Load JSON file with error handling."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading {file_path}: {e}")
        return None

def collect_article_data(article_dir):
    """Collect all article data from the article directory."""
    article_data = {}
    
    if not os.path.exists(article_dir):
        logger.error(f"Article directory {article_dir} does not exist")
        return article_data
    
    # Iterate through date directories
    for date_dir in os.listdir(article_dir):
        date_path = os.path.join(article_dir, date_dir)
        if not os.path.isdir(date_path):
            continue
            
        logger.info(f"Processing date: {date_dir}")
        article_data[date_dir] = {}
        
        # Iterate through group files
        for file_name in os.listdir(date_path):
            if file_name.endswith('.json') and file_name.startswith('group_'):
                group_id = file_name.replace('.json', '')
                file_path = os.path.join(date_path, file_name)
                
                data = load_json_file(file_path)
                if data:
                    article_data[date_dir][group_id] = data
                    logger.info(f"Loaded article data for {date_dir}/{group_id}")
    
    return article_data

def collect_resource_data(resource_dir):
    """Collect all resource data from the resource directory."""
    resource_data = {}
    
    if not os.path.exists(resource_dir):
        logger.error(f"Resource directory {resource_dir} does not exist")
        return resource_data
    
    # Iterate through date directories
    for date_dir in os.listdir(resource_dir):
        date_path = os.path.join(resource_dir, date_dir)
        if not os.path.isdir(date_path):
            continue
            
        logger.info(f"Processing resource date: {date_dir}")
        resource_data[date_dir] = {}
        
        # Iterate through group files
        for file_name in os.listdir(date_path):
            if file_name.endswith('.json') and file_name.startswith('group_'):
                group_id = file_name.replace('.json', '')
                file_path = os.path.join(date_path, file_name)
                
                data = load_json_file(file_path)
                if data:
                    resource_data[date_dir][group_id] = data
                    logger.info(f"Loaded resource data for {date_dir}/{group_id}")
    
    return resource_data

def create_knowledge_graph_data(article_data, resource_data):
    """Create knowledge graph data by left joining article and resource data."""
    kg_data = []
    
    for date_key, date_articles in article_data.items():
        for group_id, article in date_articles.items():
            # Convert date format for resource lookup (2025-06-21 -> 2025-06-21)
            resource_date_key = date_key
            
            # Check if corresponding resource data exists
            if resource_date_key in resource_data and group_id in resource_data[resource_date_key]:
                resource_group = resource_data[resource_date_key][group_id]
                
                # Get events from resource data
                events = resource_group.get('events', [])
                
                if events:
                    # Create one row per event
                    for event in events:
                        row = {
                            # Article data
                            'date': date_key,
                            'group_id': group_id,
                            'article_category': article.get('category', ''),
                            'article_headline': article.get('headline', ''),
                            'article_subheadline': article.get('subheadline', ''),
                            'article_lead': article.get('lead', ''),
                            'article_conclusion': article.get('conclusion', ''),
                            'article_cover_image_prompt': article.get('cover_image_prompt', ''),
                            'article_summary_speech': article.get('summary_speech', ''),
                            'article_event_id_list': json.dumps(article.get('event_id_list', [])),
                            'article_post_id_list': json.dumps(article.get('post_id_list', [])),
                            'article_comment_id_list': json.dumps(article.get('comment_id_list', [])),
                            
                            # Resource summary data
                            'resource_events_count': resource_group.get('summary', {}).get('events_count', 0),
                            'resource_posts_count': resource_group.get('summary', {}).get('posts_count', 0),
                            'resource_comments_count': resource_group.get('summary', {}).get('comments_count', 0),
                            'resource_articles_count': resource_group.get('summary', {}).get('articles_count', 0),
                            'resource_total_items': resource_group.get('summary', {}).get('total_items', 0),
                            
                            # Event data
                            'event_id': event.get('event_id', ''),
                            'event_type': event.get('event_type', ''),
                            'event_description': event.get('event_description', ''),
                            'event_date': event.get('event_date', ''),
                            'event_time': event.get('event_time', ''),
                            'event_location': event.get('event_location', ''),
                            'event_organizer': event.get('event_organizer', ''),
                            'event_people_involved': event.get('event_people_involved', ''),
                            'event_connections': event.get('event_connections', ''),
                            'event_statement_or_comment': event.get('statement_or_comment', ''),
                            'event_statement_source': event.get('statement_source', ''),
                            'event_statement_source_url': event.get('statement_source_url', ''),
                            'event_image_caption': event.get('image_caption', ''),
                            'event_image_url': event.get('image_url', ''),
                            'event_order': event.get('order', 0),
                            'event_summary': event.get('summary', ''),
                            'event_news_category': event.get('news_category', ''),
                            'event_content_sentiment': event.get('content_sentiment', 0),
                            'event_fake_news_score': event.get('fake_news_score', 0),
                            'event_ai_generated_score': event.get('ai_generated_score', 0),
                            'event_keywords': event.get('list_of_keywords', ''),
                            'event_fake_news_probability': event.get('fake_news_probability', 0),
                            'event_real_news_probability': event.get('real_news_probability', 0),
                            'event_confidence_score': event.get('confidence_score', 0),
                            'event_title': event.get('title', ''),
                            'event_content': event.get('content', ''),
                            'event_topic': event.get('topic', ''),
                            'event_publish_time': event.get('publish_time', ''),
                            'event_link': event.get('link', ''),
                            'event_publisher': event.get('publisher', ''),
                            'event_publisher_country': event.get('publisher_country', ''),
                            'event_language': event.get('language', ''),
                            'event_media_links': event.get('media_links', ''),
                            'event_extract_time': event.get('extract_time', ''),
                            'event_word_count': event.get('word_count', 0),
                            'event_url_category': event.get('url_category', ''),
                            'event_url_sub_category': event.get('url_sub_category', ''),
                            'event_url_domain': event.get('url_domain', ''),
                            'event_publish_date': event.get('publish_date', ''),
                            'event_domain': event.get('domain', ''),
                            'event_source': event.get('Source', ''),
                            'event_mbfc_url': event.get('MBFC URL', ''),
                            'event_bias': event.get('Bias', ''),
                            'event_country': event.get('Country', ''),
                            'event_factual_reporting': event.get('Factual Reporting', ''),
                            'event_media_type': event.get('Media Type', ''),
                            'event_source_url': event.get('Source URL', ''),
                            'event_credibility': event.get('Credibility', ''),
                            'event_source_id': event.get('Source ID#', ''),
                            'event_bias_score': event.get('bias_score', 0),
                            'event_factual_score': event.get('factual_score', 0),
                            'event_credibility_score': event.get('credibility_score', 0),
                            'event_composite_score': event.get('composite_score', 0),
                            'event_iso': event.get('ISO', ''),
                            'event_score_2025': event.get('Score 2025', 0),
                            'event_rank': event.get('Rank', 0),
                            'event_political_context': event.get('Political Context', 0),
                            'event_rank_pol': event.get('Rank_Pol', 0),
                            'event_economic_context': event.get('Economic Context', 0),
                            'event_rank_eco': event.get('Rank_Eco', 0),
                            'event_legal_context': event.get('Legal Context', 0),
                            'event_rank_leg': event.get('Rank_Leg', 0),
                            'event_social_context': event.get('Social Context', 0),
                            'event_rank_soc': event.get('Rank_Soc', 0),
                            'event_safety': event.get('Safety', 0),
                            'event_rank_saf': event.get('Rank_Saf', 0),
                            'event_zone': event.get('Zone', ''),
                            'event_country_fr': event.get('Country_FR', ''),
                            'event_country_en': event.get('Country_EN', ''),
                            'event_country_es': event.get('Country_ES', ''),
                            'event_country_pt': event.get('Country_PT', ''),
                            'event_country_ar': event.get('Country_AR', ''),
                            'event_country_fa': event.get('Country_FA', ''),
                            'event_year_n': event.get('Year (N)', 0),
                            'event_rank_n_1': event.get('Rank N-1', 0),
                            'event_rank_evolution': event.get('Rank evolution', 0),
                            'event_score_n_1': event.get('Score N-1', 0),
                            'event_score_evolution': event.get('Score evolution', 0),
                            'event_country_code': event.get('Country_code', ''),
                            'event_textblob_polarity': event.get('textblob_polarity', 0),
                            'event_textblob_subjectivity': event.get('textblob_subjectivity', 0),
                            'event_vader_neg': event.get('vader_neg', 0),
                            'event_vader_neu': event.get('vader_neu', 0),
                            'event_vader_pos': event.get('vader_pos', 0),
                            'event_vader_compound': event.get('vader_compound', 0),
                        }
                        kg_data.append(row)
                        logger.info(f"Added row for {date_key}/{group_id}/event_{event.get('event_id', 'unknown')}")
                else:
                    # No events found, create one row with article data only
                    row = {
                        'date': date_key,
                        'group_id': group_id,
                        'article_category': article.get('category', ''),
                        'article_headline': article.get('headline', ''),
                        'article_subheadline': article.get('subheadline', ''),
                        'article_lead': article.get('lead', ''),
                        'article_conclusion': article.get('conclusion', ''),
                        'article_cover_image_prompt': article.get('cover_image_prompt', ''),
                        'article_summary_speech': article.get('summary_speech', ''),
                        'article_event_id_list': json.dumps(article.get('event_id_list', [])),
                        'article_post_id_list': json.dumps(article.get('post_id_list', [])),
                        'article_comment_id_list': json.dumps(article.get('comment_id_list', [])),
                        'resource_events_count': 0,
                        'resource_posts_count': 0,
                        'resource_comments_count': 0,
                        'resource_articles_count': 0,
                        'resource_total_items': 0,
                    }
                    kg_data.append(row)
                    logger.info(f"Added row without events for {date_key}/{group_id}")
            else:
                # No resource data found, create row with article data only
                row = {
                    'date': date_key,
                    'group_id': group_id,
                    'article_category': article.get('category', ''),
                    'article_headline': article.get('headline', ''),
                    'article_subheadline': article.get('subheadline', ''),
                    'article_lead': article.get('lead', ''),
                    'article_conclusion': article.get('conclusion', ''),
                    'article_cover_image_prompt': article.get('cover_image_prompt', ''),
                    'article_summary_speech': article.get('summary_speech', ''),
                    'article_event_id_list': json.dumps(article.get('event_id_list', [])),
                    'article_post_id_list': json.dumps(article.get('post_id_list', [])),
                    'article_comment_id_list': json.dumps(article.get('comment_id_list', [])),
                    'resource_events_count': 0,
                    'resource_posts_count': 0,
                    'resource_comments_count': 0,
                    'resource_articles_count': 0,
                    'resource_total_items': 0,
                }
                kg_data.append(row)
                logger.info(f"Added row without resource data for {date_key}/{group_id}")
    
    return kg_data

def save_knowledge_graph_data(kg_data, output_dir):
    """Save knowledge graph data to Excel file."""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Create DataFrame
    df = pd.DataFrame(kg_data)
    
    # Select useful columns (excluding metrics)
    useful_columns = [
        # Basic identifiers
        'date',
        'group_id',
        'event_id',
        
        # Article content
        'article_category',
        'article_headline',
        'article_subheadline',
        'article_lead',
        'article_conclusion',
        
        # Event details
        'event_type',
        'event_description',
        'event_date',
        'event_time',
        'event_location',
        'event_organizer',
        'event_people_involved',
        'event_connections',
        'event_statement_or_comment',
        'event_statement_source',
        'event_summary',
        'event_news_category',
        
        # Content information
        'event_title',
        'event_content',
        'event_topic',
        'event_keywords',
        'event_publish_time',
        'event_link',
        'event_publisher',
        'event_publisher_country',
        'event_language',
        'event_word_count',
        'event_publish_date',
        'event_domain',
        
        # Source credibility (basic)
        'event_source',
        'event_country',
        'event_credibility',
        'event_media_type',
        
        # Image information
        'event_image_caption',
        'event_image_url',
    ]
    
    # Filter columns that exist in the dataframe
    existing_columns = [col for col in useful_columns if col in df.columns]
    df_filtered = df[existing_columns].tail(100)
    
    logger.info(f"Filtered from {len(df.columns)} to {len(existing_columns)} columns")
    
    # Save as Excel
    excel_path = os.path.join(output_dir, f"knowledge_graph.xlsx")
    df_filtered.to_excel(excel_path, index=False, engine='openpyxl')
    logger.info(f"Saved Excel file: {excel_path}")
    
    # Print summary
    logger.info(f"Generated knowledge graph with {len(kg_data)} rows")
    logger.info(f"Number of unique dates: {df['date'].nunique()}")
    logger.info(f"Number of unique groups: {df['group_id'].nunique()}")
    
    return excel_path

def main():
    """Main function to process article and resource data."""
    # Define paths
    base_dir = Path(__file__).parent
    article_dir = base_dir / "article"
    resource_dir = base_dir / "resource"
    output_dir = base_dir / "knowledge_graph"
    
    logger.info("Starting knowledge graph generation...")
    
    # Collect article data
    logger.info("Collecting article data...")
    article_data = collect_article_data(article_dir)
    logger.info(f"Collected article data for {len(article_data)} dates")
    
    # Collect resource data
    logger.info("Collecting resource data...")
    resource_data = collect_resource_data(resource_dir)
    logger.info(f"Collected resource data for {len(resource_data)} dates")
    
    # Create knowledge graph data
    logger.info("Creating knowledge graph data...")
    kg_data = create_knowledge_graph_data(article_data, resource_data)
    
    # Save knowledge graph data
    logger.info("Saving knowledge graph data...")
    excel_path = save_knowledge_graph_data(kg_data, output_dir)
    
    logger.info("Knowledge graph generation completed successfully!")
    logger.info(f"Output file: {excel_path}")

if __name__ == "__main__":
    main()
