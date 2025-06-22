import pandas as pd
import numpy as np
from pathlib import Path
import json
import ast
import time
from typing import Dict, List
import sys
import os
from textblob import TextBlob
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
import warnings
import uuid
import base64

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from llm_client import alibaba_client
from classifier.fake_news.predict import predict_fake_news
from card.event.prompt import get_event_card_prompt
warnings.filterwarnings('ignore')

nltk.download('vader_lexicon', quiet=True)

def calculate_confidence_score(probability):
    """Calculate confidence score based on probability using linear interpolation"""
    points = {
        0.50: 0.760,
        0.55: 0.784,
        0.60: 0.807,
        0.65: 0.836,
        0.70: 0.861,
        0.75: 0.897,
        0.80: 0.935,
        0.85: 0.964,
        0.90: 0.985
    }
    
    if probability <= 0.5:
        return 0.760
    if probability >= 0.9:
        return 0.985
    
    lower_prob = max(p for p in points.keys() if p <= probability)
    upper_prob = min(p for p in points.keys() if p >= probability)
    
    lower_conf = points[lower_prob]
    upper_conf = points[upper_prob]
    
    ratio = (probability - lower_prob) / (upper_prob - lower_prob)
    confidence = lower_conf + ratio * (upper_conf - lower_conf)
    
    return round(confidence, 3)

def generate_short_uuid() -> str:
    """Generate a 7-character UUID"""
    uuid_bytes = uuid.uuid4().bytes
    b64 = base64.urlsafe_b64encode(uuid_bytes).decode('ascii').rstrip('=')
    return b64[:7]

def load_trust_scores():
    """Load and prepare trust score data"""
    print("Loading trust score data...")
    
    country_df = pd.read_csv(
        'data/raw/trust_score/country_2025.csv',
        sep=';',
        encoding='latin1',
        decimal=',',
        na_values=['', '??????'],
        keep_default_na=True
    )
    
    country_dict = {
        'United States': 'us',
        'United Kingdom': 'uk',
        'Canada': 'ca',
        'Taiwan': 'tw',
        'Malaysia': 'my',
        'Japan': 'jp'
    }
    
    country_df = country_df[country_df['Country_EN'].isin(country_dict.keys())]
    country_df['Country_code'] = country_df['Country_EN'].map(country_dict)
    
    publisher_df = pd.read_csv('data/raw/trust_score/publishers_bias.csv')

    if 'Unnamed: 9' in publisher_df.columns:
        publisher_df = publisher_df.drop('Unnamed: 9', axis=1)
    
    bias_mapping = {
        'Left': -0.8,
        'Left-Center': -0.4,
        'Least Biased': 0.0,
        'Right-Center': 0.4,
        'Right': 0.8,
        'Conspiracy-Pseudoscience': -0.9,
        'Questionable': 0.9,
        'Satire': 0.0,
        'Pro-Science': -0.3
    }
    
    factual_mapping = {
        'Very High': 1.0,
        'High': 0.75,
        'Mostly Factual': 0.5,
        'Mixed': 0.0,
        'Low': -0.5,
        'Very Low': -1.0,
        np.nan: 0.0
    }
    
    credibility_mapping = {
        'High': 1.0,
        'high': 1.0,
        'Medium': 0.5,
        'Low': -1.0,
        np.nan: 0.0
    }
    
    publisher_df['bias_score'] = publisher_df['Bias'].map(bias_mapping)
    publisher_df['factual_score'] = publisher_df['Factual Reporting'].map(factual_mapping)
    publisher_df['credibility_score'] = publisher_df['Credibility'].str.capitalize().map(credibility_mapping)
    
    # according to trust score formula: Trust Score = (R / 64 × 0.6) + [ (50 - |B|) / 50 × 0.3] + (C × 0.1)
    # Converting to 0-1 scale: factual_score is already 0-1 equivalent, bias_score needs scaling
    publisher_df['composite_score'] = (
        (publisher_df['factual_score'] + 1) / 2 * 0.6 +  # Convert -1,1 to 0,1 then apply 0.6 weight
        (1 - publisher_df['bias_score'].abs()) * 0.3 +   # Convert bias to 0-1 scale then apply 0.3 weight  
        (publisher_df['credibility_score'] + 1) / 2 * 0.1  # Convert -1,1 to 0,1 then apply 0.1 weight
    )
    
    return country_df, publisher_df

def analyze_sentiment(text):
    """Perform multi-method sentiment analysis"""
    if not isinstance(text, str) or not text.strip():
        return {
            'textblob_polarity': 0.0,
            'textblob_subjectivity': 0.0,
            'vader_neg': 0.0,
            'vader_neu': 0.0,
            'vader_pos': 0.0,
            'vader_compound': 0.0
        }
    
    # TextBlob analysis
    blob = TextBlob(text)
    tb_polarity = blob.sentiment.polarity
    tb_subjectivity = blob.sentiment.subjectivity
    
    # VADER analysis
    sid = SentimentIntensityAnalyzer()
    vader_scores = sid.polarity_scores(text)
    
    return {
        'textblob_polarity': tb_polarity,
        'textblob_subjectivity': tb_subjectivity,
        'vader_neg': vader_scores['neg'],
        'vader_neu': vader_scores['neu'],
        'vader_pos': vader_scores['pos'],
        'vader_compound': vader_scores['compound']
    }

def generate_event_card(news_content: str, image_captions_with_url: List[Dict], publishing_date: str) -> Dict:
    """Generate event card using LLM"""
    prompt = get_event_card_prompt(news_content, image_captions_with_url, publishing_date)
    
    try:
        response = alibaba_client.generate(
            prompt_content=prompt,
            system_content="You are a news analyst extracting structured event data.",
            temperature=0,
            model='qwen-plus',
            response_format={"type": "json_object"}
        )
        
        if hasattr(response, 'choices'):
            response_data = json.loads(response.choices[0].message.content)
        else:
            response_data = json.loads(response)
        return response_data
    except Exception as e:
        print(f"Failed to generate event card: {e}")
        return {"summary": "", "events": []}

def process_fundus_data(date: str):
    """Process fundus data for a given date"""
    print(f"Processing fundus data for date: {date}")
    
    # Find all fundus data files for the date
    fundus_dir = Path('data/raw/fundus')
    fundus_files = []
    for folder in fundus_dir.iterdir():
        if folder.is_dir():
            date_file = folder / f"{date}.csv"
            if date_file.exists():
                fundus_files.append(date_file)
    
    if not fundus_files:
        print(f"No fundus data found for date: {date}")
        return None
    
    # Load and combine all fundus data
    print("Loading and combining fundus data...")
    fundus_dfs = []
    for file in fundus_files:
        try:
            df = pd.read_csv(file)
            fundus_dfs.append(df)
        except Exception as e:
            print(f"Warning: Failed to load {file}: {e}")
    
    if not fundus_dfs:
        return None
    
    # Combine all dataframes
    combined_df = pd.concat(fundus_dfs, ignore_index=True)
    
    # Remove duplicates based on link
    print("Removing duplicates...")
    combined_df = combined_df.drop_duplicates(subset=['link'])
    
    # Load trust scores
    country_df, publisher_df = load_trust_scores()
  
    # Extract domain from links with more defensive programming
    def extract_domain(link):
        if not isinstance(link, str):
            print(f"Found non-string link: {link} (type: {type(link)})")
            return None
        try:
            for source_url in publisher_df['Source URL']:
                if not isinstance(source_url, str):
                    print(f"Found non-string source_url: {source_url} (type: {type(source_url)})")
                    continue
                if source_url in link:
                    return source_url
            return None
        except Exception as e:
            print(f"Error processing link {link}: {e}")
            return None
    

    combined_df['domain'] = combined_df['link'].apply(extract_domain)    
    # Merge with publisher bias data
    merged_df = pd.merge(
        combined_df,
        publisher_df,
        left_on='domain',
        right_on='Source URL',
        how='left'
    )
    
    # Merge with country context data
    final_df = pd.merge(
        merged_df,
        country_df,
        left_on='publisher_country',
        right_on='Country_code',
        how='left'
    )
    
    # Calculate sentiment scores
    sentiment_scores = []
    for _, row in final_df.iterrows():
        full_content = f"{row['title']} {row['content']}"
        scores = analyze_sentiment(full_content)
        sentiment_scores.append(scores)
    
    sentiment_df = pd.DataFrame(sentiment_scores)
    for col in sentiment_df.columns:
        final_df[col] = sentiment_df[col]
    
    # Process media links
    def process_media_links(x):
        if pd.isna(x):
            return []
        try:
            # First try to evaluate as a literal
            if isinstance(x, str):
                try:
                    return ast.literal_eval(x)
                except (ValueError, SyntaxError):
                    # If that fails, try to parse as JSON
                    try:
                        return json.loads(x)
                    except json.JSONDecodeError:
                        print(f"Warning: Could not parse media links: {x}")
                        return []
            elif isinstance(x, (list, dict)):
                return x
            else:
                print(f"Warning: Unexpected media links type: {type(x)}")
                return []
        except Exception as e:
            print(f"Error processing media links {x}: {e}")
            return []
    
    final_df['media_links'] = final_df['media_links'].apply(process_media_links) 
    # Generate event cards
    all_events = []
    total_rows = len(final_df)
    
    for idx, row in final_df.iterrows():
        # Progress update
        progress = (idx + 1) / total_rows * 100
        print(f"\rProcessing: {idx + 1}/{total_rows} ({progress:.1f}%) | "
              f"Total events: {len(all_events)}", end="", flush=True)
        
        # Generate event card
        image_captions_with_url = row['media_links']
        news_content = f"Title: {row['title']}\nContent: {row['content']}"
        publishing_date = row['publish_time']
        
        result = generate_event_card(news_content, image_captions_with_url, publishing_date)
        events = result.get('events', [])

        # Calculate fake news probabilities for the article
        combined_text = f"{row['title']} {row['content']}"
        fake_news_results = predict_fake_news([combined_text])
        fake_news_result = fake_news_results[0] if fake_news_results else {'real_probability': 0.5, 'fake_probability': 0.5}
        # Calculate confidence score
        max_probability = max(fake_news_result['real_probability'], fake_news_result['fake_probability'])
        confidence_score = calculate_confidence_score(max_probability)
        # Add metadata to each event
        for event in events:
            event_data = event.copy()
            # Add event card data
            event_data.update({
                'summary': result.get('summary', ''),
                'news_category': result.get('news_category', []),
                'content_sentiment': result.get('content_sentiment', ''),
                'fake_news_score': result.get('fake_news_score', ''),
                'ai_generated_score': result.get('ai_generated_score', ''),
                'list_of_keywords': result.get('list_of_keywords', []),
                'fake_news_probability': fake_news_result['fake_probability'],
                'real_news_probability': fake_news_result['real_probability'],
                'confidence_score': confidence_score
            })
            
            # Add original article data
            for col in final_df.columns:
                event_data[col] = row[col]
            
            all_events.append(event_data)
        
        # Save intermediate results
        if (idx + 1) % 10 == 0:  # Save every 10 articles
            temp_df = pd.DataFrame(all_events)
            temp_df.to_csv(f'data/card/event_card/temp_{date}.csv', index=False)
        
        time.sleep(1)  # Rate limiting
    
    print("\nEvent card generation complete!")
    
    # Convert to DataFrame and save
    events_df = pd.DataFrame(all_events)
    events_df['event_id'] = [generate_short_uuid() for _ in range(len(events_df))]
    output_dir = Path('data/card/event_card')
    output_dir.mkdir(parents=True, exist_ok=True)
    events_df.to_csv(output_dir / f"{date}.csv", index=False)
    # Delete temporary file if it exists
    temp_file = Path(f'data/card/event_card/temp_{date}.csv')
    if temp_file.exists():
        temp_file.unlink()
    return events_df

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Process fundus data and generate event cards')
    parser.add_argument('--date', type=str, required=True, help='Date to process (YYYY-MM-DD)')
    
    args = parser.parse_args()
    process_fundus_data(args.date)
