# classifier/category/utils/data_utils.py

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from typing import Tuple, Any
from sklearn.pipeline import Pipeline

from ..models.config import DATA_CONFIG

def load_and_preprocess_data(train_path: str, test_path: str) -> Tuple[pd.DataFrame, pd.DataFrame, Any, Any, Any, Any, Any, Any]:
    """Load and preprocess the BBC News dataset"""
    # Load datasets
    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)
    
    # Preprocess data
    texts = train_df['Text'].values
    categories = train_df['Category'].values
    
    # Encode labels
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(categories)
    
    # TF-IDF vectorization
    vectorizer = TfidfVectorizer(
        max_features=DATA_CONFIG['max_features'],
        stop_words=DATA_CONFIG['stop_words'],
        lowercase=DATA_CONFIG['lowercase'],
        ngram_range=DATA_CONFIG['ngram_range'],
        min_df=DATA_CONFIG['min_df'],
        max_df=DATA_CONFIG['max_df']
    )
    X = vectorizer.fit_transform(texts)
    
    # Split data
    X_train, X_val, y_train, y_val = train_test_split(
        X, y,
        test_size=DATA_CONFIG['test_size'],
        random_state=DATA_CONFIG['random_state'],
        stratify=y
    )
    
    return train_df, test_df, X_train, y_train, X_val, y_val, vectorizer, label_encoder

def create_tfidf_pipeline(params):
    """Create a pipeline with TF-IDF vectorizer"""
    return Pipeline([
        ('tfidf', TfidfVectorizer(
            max_features=params['max_features'],
            ngram_range=params['ngram_range'],
            min_df=params['min_df'],
            max_df=params['max_df'],
            stop_words=params['stop_words'],
            lowercase=params['lowercase']
        ))
    ])