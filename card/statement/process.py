import pandas as pd
import numpy as np
from pathlib import Path
from textblob import TextBlob
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
from scipy.stats import entropy
from collections import defaultdict
import warnings
import sys
import os
from gliner import GLiNER
from geopy.geocoders import Nominatim
import time
import json

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from classifier.fake_news.predict import predict_fake_news
warnings.filterwarnings('ignore')

# Download required NLTK data
nltk.download('vader_lexicon', quiet=True)

# Initialize GLiNER model
print("Loading GLiNER model...")
gliner_model = GLiNER.from_pretrained("urchade/gliner_largev2")

# Initialize geocoder with increased timeout and rate limiting
geolocator = Nominatim(user_agent="llm_news_app", timeout=10)  # Increased from default 1 second to 10 seconds

def extract_entities(text, max_length=512):
    """
    Extract entities from text using GLiNER with length limit
    
    Args:
        text (str): Input text to process
        max_length (int): Maximum length of text to process (default: 512 tokens)
    """
    if not isinstance(text, str) or not text.strip():
        return {
            'person': [],
            'date': [],
            'organization': [],
            'location': [],
            'action': [],
            'event': []
        }
    
    # Truncate text if it's too long
    if len(text.split()) > max_length:
        text = ' '.join(text.split()[:max_length])
        print(f"Warning: Text truncated to {max_length} tokens")
    
    labels = ["person", "date", "organization", "location", "action", "event"]
    try:
        entities = gliner_model.predict_entities(text, labels)
        
        # Group entities by label
        entity_dict = {label: [] for label in labels}
        for entity in entities:
            entity_dict[entity['label']].append(entity['text'])
        
        return entity_dict
    except Exception as e:
        print(f"Warning: Entity extraction failed: {e}")
        return {label: [] for label in labels}

def get_location_details(location_name):
    """Get detailed location information using geopy"""
    try:
        location = geolocator.geocode(location_name)
        if location:
            return {
                'address': location.address,
                'latitude': location.latitude,
                'longitude': location.longitude
            }
        return None
    except Exception as e:
        print(f"Warning: Geocoding failed for {location_name}: {e}")
        return None
    finally:
        # Add delay to respect rate limits (1 request per second)
        time.sleep(1.1)

def process_entities(text, max_length=512):
    """Process text to extract and enrich entities"""
    # Extract entities with max_length parameter
    entities = extract_entities(text, max_length=max_length)
    
    # Get location details for each location
    location_details = {}
    for loc in entities['location']:
        details = get_location_details(loc)
        if details:
            location_details[loc] = details
    
    return {
        'entities': entities,
        'location_details': location_details
    }

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

def calculate_post_controversy(comment_group):
    """Calculate controversy score for a group of comments (one post)"""
    compounds = comment_group['vader_compound'].values
    bin_counts = np.histogram(compounds, bins=5, range=(-1,1))[0]
    prob = bin_counts / len(compounds)
    uniform = np.ones_like(prob)/len(prob)
    return 1 - entropy(prob, uniform)/np.log(len(prob))

def calculate_engagement_score(comments_df):
    """Calculate engagement score (0-1 range)"""
    # Normalize upvotes
    comment_ups_norm = (comments_df['comment_ups'] - comments_df['comment_ups'].min()) / \
                       (comments_df['comment_ups'].max() - comments_df['comment_ups'].min() + 1e-8)
    
    # Build comment tree and calculate max depth
    parent_to_children = defaultdict(list)
    for _, row in comments_df.iterrows():
        parent_to_children[row['comment_parent_id']].append(row['comment_id'])
    
    def get_depth(comment_id):
        if not parent_to_children.get(comment_id, []):
            return 0
        return 1 + max(get_depth(child) for child in parent_to_children[comment_id])
    
    # Find root comments
    root_candidates = []
    nan_roots = [root for root in parent_to_children.keys() if pd.isna(root)]
    if nan_roots:
        root_candidates.extend(nan_roots)
    
    if not root_candidates:
        all_comment_ids = set(comments_df['comment_id'].values)
        all_parent_ids = set(comments_df['comment_parent_id'].dropna().values)
        potential_roots = all_comment_ids - all_parent_ids
        root_candidates.extend(potential_roots)
    
    max_depth = max(get_depth(root) for root in root_candidates) if root_candidates else 1
    depth_norm = min(max_depth / 10, 1.0)
    
    # Normalize total comments
    total_comments = len(comments_df)
    comments_norm = min(total_comments / 100, 1.0)
    
    # Calculate weighted score
    engagement_score = 0.4 * comment_ups_norm.mean() + \
                      0.3 * depth_norm + \
                      0.3 * comments_norm
    return engagement_score.round(2)

def calculate_post_engagement_score(posts_df):
    """Calculate engagement score for posts (0-1 range)"""
    # Normalize upvotes
    ups_norm = (posts_df['ups'] - posts_df['ups'].min()) / \
               (posts_df['ups'].max() - posts_df['ups'].min() + 1e-8)
    
    # Normalize comment count
    comments_norm = (posts_df['num_comments'] - posts_df['num_comments'].min()) / \
                   (posts_df['num_comments'].max() - posts_df['num_comments'].min() + 1e-8)
    
    # Calculate weighted score (60% upvotes, 40% comments)
    engagement_score = 0.6 * ups_norm + 0.4 * comments_norm
    return engagement_score.round(2)

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

def process_comments(comments_df, date: str):
    """Process comments DataFrame with various metrics"""
    print("Processing comments...")
    total_comments = len(comments_df)
    
    # Calculate sentiment scores
    print("Calculating sentiment scores...")
    sentiment_scores = []
    for i, comment in enumerate(comments_df['comment_body']):
        sentiment_scores.append(analyze_sentiment(comment))
        if (i + 1) % 100 == 0:
            print(f"Sentiment analysis: {i + 1}/{total_comments} ({((i + 1)/total_comments)*100:.1f}%)")
    
    # Add sentiment columns
    comments_df['polarity'] = [ss['textblob_polarity'] for ss in sentiment_scores]
    comments_df['subjectivity'] = [ss['textblob_subjectivity'] for ss in sentiment_scores]
    comments_df['vader_neg'] = [ss['vader_neg'] for ss in sentiment_scores]
    comments_df['vader_neu'] = [ss['vader_neu'] for ss in sentiment_scores]
    comments_df['vader_pos'] = [ss['vader_pos'] for ss in sentiment_scores]
    comments_df['vader_compound'] = [ss['vader_compound'] for ss in sentiment_scores]
    
    # Extract entities with length limit
    print("Extracting entities from comments...")
    entity_results = []
    for i, text in enumerate(comments_df['comment_body']):
        entity_results.append(process_entities(text, max_length=512))
        if (i + 1) % 50 == 0:  # Progress every 50 comments due to geocoding delays
            print(f"Entity extraction: {i + 1}/{total_comments} ({((i + 1)/total_comments)*100:.1f}%)")
    
    # Add entity columns
    comments_df['persons'] = [result['entities']['person'] for result in entity_results]
    comments_df['dates'] = [result['entities']['date'] for result in entity_results]
    comments_df['organizations'] = [result['entities']['organization'] for result in entity_results]
    comments_df['locations'] = [result['entities']['location'] for result in entity_results]
    comments_df['actions'] = [result['entities']['action'] for result in entity_results]
    comments_df['events'] = [result['entities']['event'] for result in entity_results]
    comments_df['location_details'] = [json.dumps(result['location_details']) for result in entity_results]
    
    # Calculate controversy scores by post
    print("Calculating controversy scores...")
    comments_df['controversy_score'] = comments_df.groupby('post_id')['vader_compound'].transform(
        lambda x: calculate_post_controversy(pd.DataFrame({'vader_compound': x}))
    )
    
    # Calculate engagement scores
    print("Calculating engagement scores...")
    comments_df['engagement_score'] = comments_df.groupby('post_id').apply(
        lambda x: calculate_engagement_score(x)
    ).reset_index(level=0, drop=True)
    
    # Calculate fake news probabilities
    print("Calculating fake news probabilities...")
    fake_news_results = predict_fake_news(comments_df['comment_body'].tolist())
    
    # Add fake news probabilities to DataFrame
    comments_df['real_news_probability'] = [result['real_probability'] for result in fake_news_results]
    comments_df['fake_news_probability'] = [result['fake_probability'] for result in fake_news_results]
    
    # Calculate confidence scores
    print("Calculating confidence scores...")
    comments_df['confidence_score'] = comments_df.apply(
        lambda row: calculate_confidence_score(
            max(row['real_news_probability'], row['fake_news_probability'])
        ),
        axis=1
    )
    
    return comments_df

def process_posts(posts_df, date: str):
    """Process posts DataFrame with various metrics"""
    print("Processing posts...")
    total_posts = len(posts_df)
    
    # Calculate sentiment scores for title and content
    print("Calculating sentiment scores...")
    title_sentiment = []
    content_sentiment = []
    for i, (title, content) in enumerate(zip(posts_df['title'], posts_df['content'])):
        title_sentiment.append(analyze_sentiment(title))
        content_sentiment.append(analyze_sentiment(content))
        if (i + 1) % 50 == 0:
            print(f"Sentiment analysis: {i + 1}/{total_posts} ({((i + 1)/total_posts)*100:.1f}%)")
    
    # Add sentiment columns for title
    posts_df['title_polarity'] = [ss['textblob_polarity'] for ss in title_sentiment]
    posts_df['title_subjectivity'] = [ss['textblob_subjectivity'] for ss in title_sentiment]
    posts_df['title_vader_neg'] = [ss['vader_neg'] for ss in title_sentiment]
    posts_df['title_vader_neu'] = [ss['vader_neu'] for ss in title_sentiment]
    posts_df['title_vader_pos'] = [ss['vader_pos'] for ss in title_sentiment]
    posts_df['title_vader_compound'] = [ss['vader_compound'] for ss in title_sentiment]
    
    # Add sentiment columns for content
    posts_df['content_polarity'] = [ss['textblob_polarity'] for ss in content_sentiment]
    posts_df['content_subjectivity'] = [ss['textblob_subjectivity'] for ss in content_sentiment]
    posts_df['content_vader_neg'] = [ss['vader_neg'] for ss in content_sentiment]
    posts_df['content_vader_neu'] = [ss['vader_neu'] for ss in content_sentiment]
    posts_df['content_vader_pos'] = [ss['vader_pos'] for ss in content_sentiment]
    posts_df['content_vader_compound'] = [ss['vader_compound'] for ss in content_sentiment]
    
    # Extract entities from title and content with length limits
    print("Extracting entities from posts...")
    # For titles, use shorter limit since they're typically shorter
    title_entities = []
    content_entities = []
    for i, (title, content) in enumerate(zip(posts_df['title'], posts_df['content'])):
        title_entities.append(process_entities(title, max_length=256))
        content_entities.append(process_entities(content, max_length=512))
        if (i + 1) % 25 == 0:  # Progress every 25 posts due to geocoding delays
            print(f"Entity extraction: {i + 1}/{total_posts} ({((i + 1)/total_posts)*100:.1f}%)")
    
    # Combine entities from title and content
    combined_entities = []
    for t_ent, c_ent in zip(title_entities, content_entities):
        combined = {
            'entities': {
                label: list(set(t_ent['entities'][label] + c_ent['entities'][label]))
                for label in ['person', 'date', 'organization', 'location', 'action', 'event']
            },
            'location_details': {**t_ent['location_details'], **c_ent['location_details']}
        }
        combined_entities.append(combined)
    
    # Add entity columns
    posts_df['persons'] = [result['entities']['person'] for result in combined_entities]
    posts_df['dates'] = [result['entities']['date'] for result in combined_entities]
    posts_df['organizations'] = [result['entities']['organization'] for result in combined_entities]
    posts_df['locations'] = [result['entities']['location'] for result in combined_entities]
    posts_df['actions'] = [result['entities']['action'] for result in combined_entities]
    posts_df['events'] = [result['entities']['event'] for result in combined_entities]
    posts_df['location_details'] = [json.dumps(result['location_details']) for result in combined_entities]
    
    # Calculate combined sentiment
    posts_df['polarity'] = (posts_df['title_polarity'] * 0.4 + posts_df['content_polarity'] * 0.6)
    posts_df['subjectivity'] = (posts_df['title_subjectivity'] * 0.4 + posts_df['content_subjectivity'] * 0.6)
    posts_df['vader_compound'] = (posts_df['title_vader_compound'] * 0.4 + posts_df['content_vader_compound'] * 0.6)
    
    # Calculate engagement scores
    print("Calculating engagement scores...")
    posts_df['engagement_score'] = calculate_post_engagement_score(posts_df)
    
    # Calculate author credibility
    print("Calculating author credibility...")
    posts_df['author_total_karma'] = posts_df['author_post_karma'] + posts_df['author_comment_karma']
    posts_df['author_credibility_score'] = np.log1p(posts_df['author_total_karma'])
    
    # Calculate fake news probabilities
    print("Calculating fake news probabilities...")
    combined_texts = posts_df.apply(lambda row: f"{row['title']} {row['content']}", axis=1)
    fake_news_results = predict_fake_news(combined_texts.tolist())
    
    # Add fake news probabilities to DataFrame
    posts_df['real_news_probability'] = [result['real_probability'] for result in fake_news_results]
    posts_df['fake_news_probability'] = [result['fake_probability'] for result in fake_news_results]
    
    # Calculate confidence scores
    print("Calculating confidence scores...")
    posts_df['confidence_score'] = posts_df.apply(
        lambda row: calculate_confidence_score(
            max(row['real_news_probability'], row['fake_news_probability'])
        ),
        axis=1
    )
    
    # Calculate composite credibility score
    posts_df['composite_credibility_score'] = (
        posts_df['real_news_probability'] * 0.6 +  # Model prediction weight
        np.clip(posts_df['author_credibility_score'] * 10, 0, 40) * 0.2 +  # Author credibility
        np.clip((1 - (1 / (posts_df['upvote_ratio'] + 0.01))) * 100, 0, 40) * 0.2  # Low controversy bonus
    )
    
    return posts_df

def main(date='2025-06-14'):
    """Process both posts and comments for a given date"""
    print(f"Processing data for date: {date}")
    
    # Process posts
    posts_dir = f"data/raw/reddit/{date}/posts"
    posts_files = list(Path(posts_dir).glob('*.csv'))
    if posts_files:
        print(f"Processing {len(posts_files)} post files...")
        posts_df = pd.concat([pd.read_csv(f) for f in posts_files])
        processed_posts = process_posts(posts_df, date)
        
        # Save processed posts
        output_dir = f"data/card/statement_card/posts"
        os.makedirs(output_dir, exist_ok=True)
        processed_posts.to_csv(f"{output_dir}/{date}.csv", index=False)
        print(f"Saved processed posts to {output_dir}/{date}.csv")
    
    # Process comments
    comments_dir = f"data/raw/reddit/{date}/comments"
    comments_files = list(Path(comments_dir).glob('*.csv'))
    if comments_files:
        print(f"Processing {len(comments_files)} comment files...")
        comments_df = pd.concat([pd.read_csv(f) for f in comments_files])
        processed_comments = process_comments(comments_df, date)
        
        # Save processed comments
        output_dir = f"data/card/statement_card/comments"
        os.makedirs(output_dir, exist_ok=True)
        processed_comments.to_csv(f"{output_dir}/{date}.csv", index=False)
        print(f"Saved processed comments to {output_dir}/{date}.csv")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Process fundus data and generate event cards')
    parser.add_argument('--date', type=str, required=True, help='Date to process (YYYY-MM-DD)')
    
    args = parser.parse_args()
    main(args.date)