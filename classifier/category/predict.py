# classifier/category/predict.py

import os
import sys
from pathlib import Path
import argparse
import pandas as pd
import numpy as np
import joblib

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from classifier.category.models.model_knn import KNNClassifier
from classifier.category.models.model_svc import SVCClassifier

def predict(model_path: str, input_path: str, output_path: str = None):
    """Make predictions using a saved model"""
    print(f"Loading model from {model_path}...")
    
    # Determine model type from path
    model_type = "KNN" if "knn" in model_path.lower() else "SVC"
    
    # Initialize appropriate model
    if model_type == "KNN":
        model = KNNClassifier()
    else:
        model = SVCClassifier()
    
    # Load model
    model.load_model(model_path)
    
    # Load input data
    input_df = pd.read_csv(input_path)
    if 'Text' not in input_df.columns:
        raise ValueError("Input data must contain 'Text' column")
    
    # Make predictions
    print("Making predictions...")
    X = model.vectorizer.transform(input_df['Text'].values)
    predictions, probabilities = model.predict(X)
    categories = model.label_encoder.inverse_transform(predictions)
    
    # Create output DataFrame
    output_df = pd.DataFrame({
        'ArticleId': input_df['ArticleId'] if 'ArticleId' in input_df.columns else range(len(input_df)),
        'Category': categories
    })
    
    # Save predictions
    if output_path is None:
        output_path = f"{model_type.lower()}_predictions.csv"
    output_df.to_csv(output_path, index=False)
    print(f"Predictions saved to {output_path}")
    
    return output_df

def predict_single_text(text: str, model_path: str = 'classifier/category/models/best_models/best_model.joblib'):
    """
    Predict category probabilities for a single text input
    
    Args:
        text (str): Input text to classify
        model_path (str): Path to saved model file
        
    Returns:
        dict: Dictionary of category probabilities {category: probability}
    """
    print(f"Loading model from {model_path}...")
    
    try:
        # Load the saved model
        loaded_model = joblib.load(model_path)
        
        # Extract components from the loaded model
        if hasattr(loaded_model, 'vectorizer'):
            # Case: The model is the full classifier object
            model = loaded_model.model  # Get the actual sklearn model
            vectorizer = loaded_model.vectorizer
            label_encoder = loaded_model.label_encoder
        else:
            # Case: The model is saved as components dictionary
            model = loaded_model['model'].model  # Get the actual sklearn model
            vectorizer = loaded_model['vectorizer']
            label_encoder = loaded_model['label_encoder']
        
        # Transform input text
        X = vectorizer.transform([text])
        
        # Make prediction
        try:
            # Try using predict_proba directly
            probabilities = model.predict_proba(X)
        except:
            try:
                # Fallback to decision_function if predict_proba is not available
                scores = model.decision_function(X)
                # Convert scores to probabilities using softmax
                scores_exp = np.exp(scores - np.max(scores))
                probabilities = scores_exp / scores_exp.sum(axis=1, keepdims=True)
            except:
                # Last resort: use predict and create one-hot encoding
                predictions = model.predict(X)
                n_classes = len(label_encoder.classes_)
                probabilities = np.zeros((len(predictions), n_classes))
                probabilities[np.arange(len(predictions)), predictions.astype(int)] = 1
        
        # Create probability dictionary
        probability_dict = {
            cat: float(prob) 
            for cat, prob in zip(label_encoder.classes_, probabilities[0])
        }
        
        return probability_dict
        
    except Exception as e:
        print(f"Error making prediction: {str(e)}")
        import traceback
        print(traceback.format_exc())  # This will print the full error trace
        return None

# Example usage
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Make predictions using a trained model')
    parser.add_argument('--model', type=str, required=True,
                      help='Path to saved model file')
    parser.add_argument('--text', type=str, required=True,
                      help='Text to classify')
    
    args = parser.parse_args()
    
    result = predict_single_text(args.text, args.model)
    if result:
        print("\nPrediction probabilities:")
        for category, prob in result.items():
            print(f"{category}: {prob:.3f}")
    else:
        print("\nPrediction failed.")