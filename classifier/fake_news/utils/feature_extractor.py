import numpy as np
import pandas as pd
from typing import Dict, List, Union
import re
from nltk.tokenize import word_tokenize
import nltk
from collections import Counter
import math
from urllib.parse import urlparse

class FeatureExtractor:
    def __init__(self):
        # Download required NLTK data
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
    
    def calculate_entropy(self, text: str) -> float:
        """
        Calculate the entropy of the text, which can help detect AI-generated content.
        AI-generated text often has lower entropy due to more predictable patterns.
        """
        # Tokenize and convert to lowercase
        words = word_tokenize(text.lower())
        if not words:
            return 0.0
            
        # Calculate word frequencies
        word_freq = Counter(words)
        total_words = len(words)
        
        # Calculate entropy
        entropy = 0.0
        for count in word_freq.values():
            probability = count / total_words
            entropy -= probability * math.log2(probability)
            
        return entropy
    
    def extract_basic_features(self, text: str) -> Dict[str, float]:
        """Extract basic features including entropy and URL count"""
        # Tokenize text
        words = word_tokenize(text.lower())
        
        # Calculate features
        features = {
            'unique_word_ratio': len(set(words)) / len(words) if words else 0,
            'url_count': len(re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)),
            'text_entropy': self.calculate_entropy(text)
        }
        
        return features
    
    def get_feature_names(self) -> List[str]:
        """Get names of all features"""
        return ['unique_word_ratio', 'url_count', 'text_entropy']
    
    def extract_all_features(self, df: pd.DataFrame, text_column: str = 'text') -> pd.DataFrame:
        """Extract all features for a DataFrame"""
        # Extract basic features
        basic_features = df[text_column].apply(self.extract_basic_features)
        basic_features_df = pd.json_normalize(basic_features)
        
        return basic_features_df 