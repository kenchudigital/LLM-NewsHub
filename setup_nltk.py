#!/usr/bin/env python3
"""
NLTK Setup Script for LLM-NewsHub
This script downloads all required NLTK data to prevent Resource not found errors.
"""

import nltk
import ssl
import sys

def download_nltk_data():
    """Download all required NLTK data"""
    
    # Create a list of all required NLTK resources
    required_resources = [
        'punkt',
        'stopwords', 
        'wordnet',
        'omw-1.4',
        'vader_lexicon',
        'averaged_perceptron_tagger',
        'maxent_ne_chunker',
        'words',
        'treebank',
        'brown',
        'reuters',
        'movie_reviews',
        'sentence_polarity',
        'subjectivity'
    ]
    
    print("Setting up NLTK data...")
    
    # Try to create an unverified HTTPS context to avoid SSL issues
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context
    
    # Download each resource
    for resource in required_resources:
        try:
            print(f"Downloading {resource}...")
            nltk.download(resource, quiet=False)
            print(f"✓ {resource} downloaded successfully")
        except Exception as e:
            print(f"✗ Error downloading {resource}: {e}")
            # Continue with other resources even if one fails
            continue
    
    print("\nNLTK setup completed!")
    
    # Verify critical resources
    print("\nVerifying critical resources...")
    critical_resources = ['punkt', 'stopwords', 'vader_lexicon']
    
    for resource in critical_resources:
        try:
            if resource == 'punkt':
                from nltk.tokenize import word_tokenize
                test_text = "This is a test sentence."
                tokens = word_tokenize(test_text)
                print(f"✓ {resource} is working (tokenized: {tokens})")
            elif resource == 'stopwords':
                from nltk.corpus import stopwords
                stops = stopwords.words('english')
                print(f"✓ {resource} is working ({len(stops)} stopwords loaded)")
            elif resource == 'vader_lexicon':
                from nltk.sentiment.vader import SentimentIntensityAnalyzer
                analyzer = SentimentIntensityAnalyzer()
                print(f"✓ {resource} is working (sentiment analyzer ready)")
        except Exception as e:
            print(f"✗ {resource} verification failed: {e}")

if __name__ == "__main__":
    download_nltk_data() 