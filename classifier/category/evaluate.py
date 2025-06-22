# classifier/category/evaluate.py

import os
import sys
from pathlib import Path
import argparse
import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from classifier.category.models.model_knn import KNNClassifier
from classifier.category.models.model_svc import SVCClassifier
from classifier.category.models.config import VIZ_CONFIG

def evaluate_model(model_path: str, test_path: str):
    """Evaluate a saved model on test data"""
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
    
    # Load test data
    test_df = pd.read_csv(test_path)
    if 'Text' not in test_df.columns:
        raise ValueError("Test data must contain 'Text' column")
    
    # Make predictions
    print("Making predictions...")
    X_test = model.vectorizer.transform(test_df['Text'].values)
    predictions, probabilities = model.predict(X_test)
    categories = model.label_encoder.inverse_transform(predictions)
    
    # Save predictions
    predictions_path = model.save_predictions(
        categories,
        test_df['ArticleId'].values if 'ArticleId' in test_df.columns else None
    )
    print(f"Predictions saved to {predictions_path}")
    
    # If we have true labels, calculate metrics
    if 'Category' in test_df.columns:
        true_categories = test_df['Category'].values
        true_labels = model.label_encoder.transform(true_categories)
        
        # Calculate metrics
        accuracy = accuracy_score(true_labels, predictions)
        report = classification_report(true_labels, predictions, 
                                    target_names=model.label_encoder.classes_,
                                    output_dict=True)
        cm = confusion_matrix(true_labels, predictions)
        
        # Print results
        print(f"\nEvaluation Results:")
        print(f"Accuracy: {accuracy:.4f}")
        print("\nClassification Report:")
        print(classification_report(true_labels, predictions, 
                                  target_names=model.label_encoder.classes_))
        
        # Create visualizations
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        viz_dir = model.results_dir / "visualizations"
        
        # Confusion Matrix
        plt.figure(figsize=VIZ_CONFIG['figsize']['confusion_matrix'])
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                   xticklabels=model.label_encoder.classes_,
                   yticklabels=model.label_encoder.classes_)
        plt.title(f'{model_type} Confusion Matrix (Test Set)')
        plt.xlabel('Predicted')
        plt.ylabel('Actual')
        plt.tight_layout()
        plt.savefig(viz_dir / f'test_confusion_matrix_{timestamp}.png')
        plt.close()
        
        # Save metrics
        metrics = {
            'accuracy': accuracy,
            'classification_report': report,
            'confusion_matrix': cm.tolist()
        }
        model.save_metrics(metrics)
        
        return metrics
    
    return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Evaluate a trained model')
    parser.add_argument('--model', type=str, required=True,
                      help='Path to saved model file')
    parser.add_argument('--test', type=str, required=True,
                      help='Path to test data CSV')
    
    args = parser.parse_args()
    
    metrics = evaluate_model(args.model, args.test)