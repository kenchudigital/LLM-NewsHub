# classifier/category/train.py

import os
import sys
from pathlib import Path
import argparse
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import json

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from classifier.category.models.model_knn import KNNClassifier
from classifier.category.models.model_svc import SVCClassifier
from classifier.category.models.config import DATA_CONFIG, TRAIN_CONFIG

def parse_model_params(params_str: str) -> dict:
    """Parse model parameters from string format"""
    if not params_str:
        return None
    
    params = {}
    for param in params_str.split(','):
        if '=' in param:
            key, value = param.split('=', 1)
            # Try to convert to appropriate type
            try:
                value = eval(value)  # This will handle numbers, booleans, etc.
            except:
                pass  # Keep as string if eval fails
            params[key.strip()] = value
    return params

def load_and_preprocess_data(train_path: str, test_path: str):
    """Load and preprocess the BBC News dataset"""
    print("Loading BBC News Dataset...")
    
    # Load datasets
    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)
    
    print(f"Dataset loaded successfully!")
    print(f"   Training data: {train_df.shape}")
    print(f"   Test data: {test_df.shape}")
    
    # Preprocess data
    print('\nPreprocessing data...')
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
    print(f'Feature matrix created: {X.shape}')
    
    # Split data
    X_train, X_val, y_train, y_val = train_test_split(
        X, y,
        test_size=DATA_CONFIG['test_size'],
        random_state=DATA_CONFIG['random_state'],
        stratify=y
    )
    print(f'Data split: {X_train.shape[0]} train, {X_val.shape[0]} validation')
    
    return train_df, test_df, X_train, y_train, X_val, y_val, vectorizer, label_encoder

def train_model(model_type: str, train_path: str, test_path: str, model_params: str = None):
    """Train either KNN or SVC model"""
    print(f"Starting {model_type} training...")
    
    # Parse model parameters if provided
    params = parse_model_params(model_params) if model_params else None
    
    # Load and preprocess data
    train_df, test_df, X_train, y_train, X_val, y_val, vectorizer, label_encoder = load_and_preprocess_data(
        train_path, test_path
    )
    
    # Initialize and train model
    if model_type.lower() == 'knn':
        model = KNNClassifier(params)
    elif model_type.lower() == 'svc':
        model = SVCClassifier(params)
    else:
        raise ValueError(f"Unknown model type: {model_type}")
    
    # Set model components
    model.vectorizer = vectorizer
    model.label_encoder = label_encoder
    
    # Train model
    metrics = model.train(X_train, y_train, X_val, y_val)
    
    # Print results
    print(f"\n{model_type} Training Complete!")
    print(f"Best Parameters: {metrics['best_params']}")
    print(f"Validation Accuracy: {metrics['accuracy']:.4f}")
    print(f"CV Accuracy: {metrics['cv_scores']['mean']:.4f} ± {metrics['cv_scores']['std']*2:.4f}")
    
    # Make predictions on test set if available
    if 'Text' in test_df.columns:
        print(f'\n🔄 Making predictions on test set...')
        test_texts = test_df['Text'].values
        X_test = vectorizer.transform(test_texts)
        test_predictions, _ = model.predict(X_test)
        test_categories = label_encoder.inverse_transform(test_predictions)
        
        # Save predictions
        model.save_predictions(
            test_categories,
            test_df['ArticleId'].values if 'ArticleId' in test_df.columns else None
        )
    
    return model, metrics

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Train classification models')
    parser.add_argument('--model', type=str, required=True, choices=['knn', 'svc'],
                      help='Model type to train (knn or svc)')
    parser.add_argument('--train', type=str, required=True,
                      help='Path to training data CSV')
    parser.add_argument('--test', type=str, required=True,
                      help='Path to test data CSV')
    parser.add_argument('--model-params', type=str,
                      help='Model parameters in key=value format, comma-separated')
    parser.add_argument('--save-model', type=str,
                      help='Path to save the trained model')
    
    args = parser.parse_args()
    
    model, metrics = train_model(args.model, args.train, args.test, args.model_params)
    
    # Save model if path provided
    if args.save_model:
        save_dir = Path(args.save_model).parent
        save_dir.mkdir(parents=True, exist_ok=True)
        model.save(args.save_model)
        print(f"\nModel saved to: {args.save_model}")