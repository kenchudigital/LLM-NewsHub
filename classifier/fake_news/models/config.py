import os
from pathlib import Path
import numpy as np

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent.parent
DATA_DIR = project_root / "data"

# Model paths
MODEL_DIR = project_root / "classifier" / "fake_news" / "models"
BEST_MODEL_DIR = MODEL_DIR / "best_models"

# Results paths
RESULTS_DIR = project_root / "classifier" / "fake_news" / "models" / "results"
EXPERIMENTS_DIR = project_root / "classifier" / "fake_news" / "experiments"

# Create directories
for directory in [DATA_DIR, MODEL_DIR, BEST_MODEL_DIR, RESULTS_DIR, EXPERIMENTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Random Forest configurations
RF_CONFIG = {
    'base_params': {
        'n_estimators': 100,
        'random_state': 42,
        'n_jobs': -1,
        'max_depth': 8,
        'min_impurity_decrease': 0.001,
        'max_leaf_nodes': 32
    },
    'tuning_params': {
        'n_estimators': [50, 100],
        'max_depth': [4, 6, 8, 10],
        'min_samples_split': [5, 10, 20],
        'min_samples_leaf': [4, 8, 16],
        'max_features': ['sqrt'],
        'class_weight': ['balanced', None],
        'min_impurity_decrease': [0.001, 0.005, 0.01]
    }
}

# Sentiment Analysis configurations
SENTIMENT_CONFIG = {
    'analyzers': ['vader', 'textblob'],
    'features': [
        'compound_score',
        'positive_score',
        'negative_score',
        'neutral_score',
        'subjectivity',
        'polarity'
    ]
}

# Data processing configuration
DATA_CONFIG = {
    'test_size': 0.2,
    'random_state': 42,
    'text_columns': ['title', 'text'],  # Columns to analyze
    'target_column': 'label',
    'preprocessing': {
        'remove_stopwords': True,
        'remove_punctuation': True,
        'lowercase': True,
        'lemmatize': True
    }
}

# Pruning configuration
PRUNING_CONFIG = {
    'ccp_alpha_range': np.arange(0.0, 0.03, 0.001),
    'cv_folds': 5
}

# Visualization configuration
VIZ_CONFIG = {
    'tree_visualization': {
        'max_depth_to_show': 4,  # Only show top 4 levels of the tree
        'feature_names': None,  # Will be set during training
        'class_names': ['Real', 'Fake'],  # Assuming binary classification
        'output_format': 'png',
        'export_path': RESULTS_DIR / 'tree_visualizations'
    }
}

# Create visualization directory
VIZ_CONFIG['tree_visualization']['export_path'].mkdir(parents=True, exist_ok=True)

# Feature caching configuration
FEATURE_CACHE_CONFIG = {
    'cache_dir': project_root / "classifier" / "fake_news" / "dataset" / "feature_cache",
    'feature_version': 'v3',  # Increment this when feature extraction changes
    'force_recompute': True  # Set to True to force feature recomputation
}

# Create cache directory
FEATURE_CACHE_CONFIG['cache_dir'].mkdir(parents=True, exist_ok=True)