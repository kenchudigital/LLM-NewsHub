# classifier/category/models/config.py

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

# Data paths
DATA_DIR = project_root / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
# PROCESSED_DATA_DIR = DATA_DIR / "processed"

# Model paths
MODEL_DIR = project_root / "classifier" / "category" / "models"
BEST_MODEL_DIR = MODEL_DIR / "best_models"
CHECKPOINT_DIR = MODEL_DIR / "model_checkpoints"

# Results paths
RESULTS_DIR = project_root / "classifier" / "category" / "results"
PREDICTIONS_DIR = RESULTS_DIR / "predictions"
METRICS_DIR = RESULTS_DIR / "metrics"
VISUALIZATIONS_DIR = RESULTS_DIR / "visualizations"

# Create directories if they don't exist
# Commented out empty directories that don't need to be pre-created
for directory in [
    DATA_DIR, RAW_DATA_DIR, 
    MODEL_DIR, BEST_MODEL_DIR, 
    # CHECKPOINT_DIR,  # Commented: model_checkpoints is empty and created on-demand
    RESULTS_DIR,
    # PREDICTIONS_DIR,  # Commented: predictions directory is empty and created on-demand
    # METRICS_DIR,      # Commented: metrics directory is empty and created on-demand  
    # VISUALIZATIONS_DIR # Commented: visualizations directory is empty and created on-demand
]:
    directory.mkdir(parents=True, exist_ok=True)

# Model configurations - Refined based on best performing models
KNN_CONFIG = {
    # Centered around the best performing k=31, with nearby values
    'k_values': [25, 27, 29, 31, 33, 35],
    # Focus on best performing metrics, removed manhattan due to poor performance
    'metrics': ['euclidean', 'cosine'],
    # Distance weights performed better
    'weights': ['distance'],
    # Only include relevant p values for minkowski
    'p': [2]  # Euclidean distance (p=2) performed well
}

SVC_CONFIG = {
    'param_grid': {
        # Linear kernel with C=1 performed best, focus around these values
        'C': [0.5, 0.7, 1.0, 1.3, 1.5],
        # Linear kernel performed best
        'kernel': ['linear'],
        # Scale performed well, but include nearby values
        'gamma': ['scale', 0.1, 1],
        # Degree 2 performed well for polynomial
        'degree': [2],
        # Balanced weights performed well
        'class_weight': ['balanced']
    }
}

# Data processing configuration - Validated by both best models
DATA_CONFIG = {
    'test_size': 0.2,
    'random_state': 42,
    'max_features': 15000,  # This value worked well for both models
    'ngram_range': (1, 2),  # Bigrams helped capture phrase relationships
    'min_df': 2,           # Good balance for rare but meaningful terms
    'max_df': 0.95,        # Good threshold for common terms
    'stop_words': 'english',
    'lowercase': True
}

# Configuration for parameter tuning - More focused ranges
TUNING_CONFIG = {
    'tfidf_params': {
        # Focus around the successful 15000 features
        'max_features': [12000, 15000, 18000],
        # Focus on unigrams and bigrams which performed well
        'ngram_range': [(1, 1), (1, 2)],
        # Tighter range around successful values
        'min_df': [2, 3],
        'max_df': [0.93, 0.95, 0.97],
        'stop_words': ['english']  # English stop words worked well
    }
}

# Training configuration - Optimized based on results
TRAIN_CONFIG = {
    'cv_folds': 5,  # 5-fold CV showed good balance
    'n_jobs': -1,   # Use all available cores
    'random_state': 42,
    'early_stopping_rounds': 3,  # Add early stopping
    'validation_fraction': 0.2   # Consistent with test_size
}

# Visualization configuration
VIZ_CONFIG = {
    'style': 'seaborn-v0_8',
    'palette': 'husl',
    'figsize': {
        'confusion_matrix': (10, 8),
        'learning_curves': (12, 6),
        'feature_importance': (12, 6),
        'comparison': (15, 10)
    }
}

# Cross validation configuration - Simplified based on data nature
CROSS_VALIDATION_CONFIG = {
    'cv_strategy': ['stratified'],  # News classification is better with stratified
    'n_splits': 5,                  # 5-fold showed good stability
    'shuffle': True,                # Shuffling helps prevent order bias
    'metrics': ['accuracy', 'f1_macro', 'precision_macro', 'recall_macro']
}