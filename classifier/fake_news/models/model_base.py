# classifier/fake_news/models/model_base.py

import os
import sys
from pathlib import Path
import joblib
from datetime import datetime
import json
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator
from typing import Dict, Any, Tuple, Optional

project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

from classifier.fake_news.models.config import (
    BEST_MODEL_DIR, MODEL_DIR, RESULTS_DIR
)

class BaseClassifier:
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.model_dir = MODEL_DIR / model_name.lower()
        self.best_model_dir = BEST_MODEL_DIR / model_name.lower()
        self.results_dir = RESULTS_DIR / model_name.lower()
        self._create_directories()
        self.model: Optional[BaseEstimator] = None
        self.vectorizer = None
        self.label_encoder = None
        self.metrics: Dict[str, Any] = {}
        self.best_params = None
        
    def _create_directories(self):
        """Create necessary directories if they don't exist"""
        directories = [
            self.model_dir,
            self.best_model_dir,
            self.results_dir / "predictions",
            self.results_dir / "metrics",
            self.results_dir / "visualizations"
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def save_model(self, is_best: bool = False) -> str:
        """Save the model and its components"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if is_best:
            save_dir = self.best_model_dir
            filename = f"best_{self.model_name.lower()}_{timestamp}.joblib"
        else:
            save_dir = self.model_dir
            filename = f"model_{timestamp}.joblib"
        
        save_path = save_dir / filename
        model_components = {
            'model': self.model,
            'vectorizer': self.vectorizer,
            'label_encoder': self.label_encoder,
            'metrics': self.metrics,
            'best_params': self.best_params
        }
        joblib.dump(model_components, save_path)
        return str(save_path)
    
    def load_model(self, model_path: str):
        """Load a saved model and its components"""
        components = joblib.load(model_path)
        self.model = components['model']
        self.vectorizer = components.get('vectorizer')
        self.label_encoder = components.get('label_encoder')
        self.metrics = components.get('metrics', {})
        self.best_params = components.get('best_params')
    
    def save_metrics(self, metrics: Dict[str, Any]):
        """Save model metrics to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        metrics_path = self.results_dir / "metrics" / f"{self.model_name.lower()}_metrics_{timestamp}.json"
        with open(metrics_path, 'w') as f:
            json.dump(metrics, f, indent=4)
    
    def save_predictions(self, predictions: np.ndarray, ids: Optional[np.ndarray] = None):
        """Save model predictions to CSV file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        predictions_path = self.results_dir / "predictions" / f"{self.model_name.lower()}_predictions_{timestamp}.csv"
        
        if ids is not None:
            df = pd.DataFrame({'ArticleId': ids, 'Label': predictions})
        else:
            df = pd.DataFrame({'Label': predictions})
        
        df.to_csv(predictions_path, index=False)
        return str(predictions_path)
    
    def predict(self, X) -> Tuple[np.ndarray, np.ndarray]:
        """Make predictions and return both predictions and probabilities"""
        if self.model is None:
            raise ValueError("Model not trained or loaded")
        predictions = self.model.predict(X)
        probabilities = self.model.predict_proba(X)
        return predictions, probabilities
    
    def save(self, path: str):
        """Save the model to disk"""
        save_path = Path(path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, str(save_path))
        print(f"\nModel saved to: {path}") 