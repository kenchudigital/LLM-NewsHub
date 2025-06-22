import joblib
import numpy as np
from pathlib import Path
from typing import Union, List, Dict
import pandas as pd
from .utils.feature_extractor import FeatureExtractor
from .utils.sentiment_utils import SentimentAnalyzer

class FakeNewsPredictor:
    def __init__(self, model_path: str = "classifier/fake_news/models/results/random_forest_model.joblib"):
        """Initialize the predictor with model and feature extractors"""
        self.model = joblib.load(model_path)
        self.feature_extractor = FeatureExtractor()
        self.sentiment_analyzer = SentimentAnalyzer()
    
    def prepare_features(self, text: str) -> np.ndarray:
        """Prepare features for a single text"""
        # Create a DataFrame with the text
        df = pd.DataFrame({'text': [text]})
        
        # Get sentiment features
        sentiment_features = self.sentiment_analyzer.extract_features(df)
        
        # Get basic features
        basic_features = self.feature_extractor.extract_all_features(df)
        
        # Combine features
        all_features = pd.concat([sentiment_features, basic_features], axis=1)
        
        return all_features.values
    
    def predict(self, text: Union[str, List[str]]) -> Union[Dict[str, float], List[Dict[str, float]]]:
        """
        Predict fake news probability for text(s)
        
        Args:
            text: Single text string or list of texts
            
        Returns:
            Dictionary or list of dictionaries with probabilities
        """
        if isinstance(text, str):
            features = self.prepare_features(text)
            probas = self.model.predict_proba(features)[0]
            return {
                'real_probability': float(probas[0]),
                'fake_probability': float(probas[1])
            }
        else:
            results = []
            for t in text:
                features = self.prepare_features(t)
                probas = self.model.predict_proba(features)[0]
                results.append({
                    'real_probability': float(probas[0]),
                    'fake_probability': float(probas[1])
                })
            return results

def predict_fake_news(text: Union[str, List[str]], 
                     model_path: str = "classifier/fake_news/models/results/random_forest_model.joblib"
                    ) -> Union[Dict[str, float], List[Dict[str, float]]]:
    """Convenience function for making predictions"""
    predictor = FakeNewsPredictor(model_path)
    return predictor.predict(text)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Predict fake news probability')
    parser.add_argument('--text', type=str, required=True, help='Text to classify')
    parser.add_argument('--model', type=str, 
                      default="classifier/fake_news/models/results/random_forest_model.joblib",
                      help='Path to model file')
    
    args = parser.parse_args()
    
    result = predict_fake_news(args.text, args.model)
    print("\nPrediction probabilities:")
    print(f"Real news probability: {result['real_probability']:.3f}")
    print(f"Fake news probability: {result['fake_probability']:.3f}") 