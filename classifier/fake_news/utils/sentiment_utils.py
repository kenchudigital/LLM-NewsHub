from typing import Dict, List
import pandas as pd
import numpy as np
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

class SentimentAnalyzer:
    def __init__(self):
        self.vader = SentimentIntensityAnalyzer()
        # Define feature names
        self._feature_names = [
            'polarity',
            'subjectivity',
            'vader_neg',
            'vader_neu',
            'vader_pos',
            'vader_compound'
        ]
        
    def get_feature_names(self) -> List[str]:
        """Get the names of sentiment features"""
        return self._feature_names
        
    def analyze_text(self, text: str) -> Dict[str, float]:
        """Extract sentiment features from text using multiple analyzers"""
        # VADER analysis
        vader_scores = self.vader.polarity_scores(str(text))
        
        # TextBlob analysis
        blob = TextBlob(str(text))
        
        return {
            'polarity': blob.sentiment.polarity,
            'subjectivity': blob.sentiment.subjectivity,
            'vader_neg': vader_scores['neg'],
            'vader_neu': vader_scores['neu'],
            'vader_pos': vader_scores['pos'],
            'vader_compound': vader_scores['compound']
        }
    
    def extract_features(self, df: pd.DataFrame, text_column: str = 'text') -> pd.DataFrame:
        """Extract sentiment features from text column"""
        features = df[text_column].apply(self.analyze_text)
        return pd.json_normalize(features)