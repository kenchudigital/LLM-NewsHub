import joblib
from pathlib import Path
import pandas as pd
import numpy as np
from typing import Tuple, Optional
from ..models.config import FEATURE_CACHE_CONFIG

def get_cache_path(split_type: str, feature_version: str) -> Path:
    """Get the path for cached features"""
    return FEATURE_CACHE_CONFIG['cache_dir'] / f"{split_type}_features_{feature_version}.joblib"

def save_features(X: np.ndarray, y: np.ndarray, split_type: str) -> None:
    """Save prepared features to cache"""
    cache_path = get_cache_path(split_type, FEATURE_CACHE_CONFIG['feature_version'])
    joblib.dump({
        'X': X,
        'y': y,
        'feature_version': FEATURE_CACHE_CONFIG['feature_version']
    }, cache_path)
    print(f"Saved {split_type} features to {cache_path}")

def load_features(split_type: str) -> Optional[Tuple[np.ndarray, np.ndarray]]:
    """Load prepared features from cache if they exist"""
    if FEATURE_CACHE_CONFIG['force_recompute']:
        return None
        
    cache_path = get_cache_path(split_type, FEATURE_CACHE_CONFIG['feature_version'])
    
    if not cache_path.exists():
        return None
        
    try:
        cached_data = joblib.load(cache_path)
        if cached_data['feature_version'] != FEATURE_CACHE_CONFIG['feature_version']:
            print(f"⚠️ Cached features version mismatch. Recomputing...")
            return None
            
        print(f"📂 Loaded {split_type} features from cache")
        return cached_data['X'], cached_data['y']
    except Exception as e:
        print(f"⚠️ Error loading cached features: {str(e)}")
        return None 