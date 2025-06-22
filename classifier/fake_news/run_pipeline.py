import os
from pathlib import Path
import argparse
from datetime import datetime
import json
from typing import Tuple, List
import pandas as pd
from sklearn.model_selection import train_test_split
import sys
import joblib
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from classifier.fake_news.train import train_model, prepare_features
from classifier.fake_news.utils.sentiment_utils import SentimentAnalyzer
from classifier.fake_news.utils.experiment_tracking import log_experiment, NumpyEncoder

def prepare_data(test_size: float = 0.2, random_state: int = 42) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Prepare train and test datasets from Fake.csv and True.csv"""
    print("\nLoading and preparing data...")
    
    fake_df = pd.read_csv('classifier/fake_news/dataset/Fake.csv')
    true_df = pd.read_csv('classifier/fake_news/dataset/True.csv')
    
    fake_df['label'] = 1  
    true_df['label'] = 0  
    
    df = pd.concat([fake_df, true_df], ignore_index=True)

    train_df, test_df = train_test_split(
        df,
        test_size=test_size,
        random_state=random_state,
        stratify=df['label']  
    )
    return train_df, test_df

def analyze_threshold_performance(predictions_df: pd.DataFrame, thresholds: List[float]) -> Tuple[List[float], List[float], List[float]]:
    """
    Analyze model performance at different probability thresholds.
    
    Args:
        predictions_df: DataFrame with true labels and prediction probabilities
        thresholds: List of probability thresholds to analyze
        
    Returns:
        Tuple of (accuracies, invalid_ratios, thresholds)
    """
    accuracies = []
    invalid_ratios = []
    
    for threshold in thresholds:
        valid_predictions = (predictions_df['real_probability'] > threshold) | (predictions_df['fake_probability'] > threshold)
        invalid_ratio = 1 - valid_predictions.mean()

        if valid_predictions.any():
            valid_accuracy = accuracy_score(
                predictions_df.loc[valid_predictions, 'true_label'],
                predictions_df.loc[valid_predictions, 'predicted_label']
            )
        else:
            valid_accuracy = 0.0
            
        accuracies.append(valid_accuracy)
        invalid_ratios.append(invalid_ratio)
    
    return accuracies, invalid_ratios, thresholds

def plot_threshold_analysis(accuracies: List[float], invalid_ratios: List[float], thresholds: List[float], save_path: str):
    """
    Plot threshold analysis showing accuracy and invalid ratio at different thresholds.
    
    Args:
        accuracies: List of accuracies at each threshold
        invalid_ratios: List of invalid ratios at each threshold
        thresholds: List of thresholds used
        save_path: Path to save the plot
    """
    plt.figure(figsize=(10, 6))
    plt.plot(thresholds, accuracies, 'b-', label='Accuracy', linewidth=2)
    plt.plot(thresholds, invalid_ratios, 'r--', label='Invalid Ratio', linewidth=2)
    plt.xlabel('Probability Threshold')
    plt.ylabel('Score')
    plt.title('Model Performance vs. Prediction Threshold')
    plt.grid(True, alpha=0.3)
    plt.legend()
    max_acc_idx = np.argmax(accuracies)
    plt.annotate(f'Max Accuracy: {accuracies[max_acc_idx]:.3f}\nThreshold: {thresholds[max_acc_idx]:.2f}',
                xy=(thresholds[max_acc_idx], accuracies[max_acc_idx]),
                xytext=(10, 10), textcoords='offset points',
                bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5))
    plt.savefig(save_path)
    plt.close()

def run_pipeline(
    test_size: float = 0.2,
    random_state: int = 42,
) -> Tuple[str, str]:
    """Run the complete fake news detection pipeline"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        print("Starting Fake News Detection Pipeline")
        sentiment_analyzer = SentimentAnalyzer()
        train_df, test_df = prepare_data(test_size, random_state)
        
        model, model_info = train_model(
            train_df=train_df,
            test_df=test_df,
            sentiment_analyzer=sentiment_analyzer
        )
        print("Selecting best model based on F1 score...")
        rf_f1 = model_info['metrics']['random_forest']['f1']
        tree_f1 = model_info['metrics']['decision_tree']['f1']
        best_model_dir = Path("classifier/fake_news/models/best_models")
        best_model_dir.mkdir(parents=True, exist_ok=True)
        
        if rf_f1 >= tree_f1:
            best_model_path = best_model_dir / "best_model.joblib"
            joblib.dump(model, best_model_path)  # model is already the Random Forest model
        else:
            # Load the decision tree model from results directory
            tree_model_path = Path("classifier/fake_news/models/results/decision_tree_model.joblib")
            tree_model = joblib.load(tree_model_path)
            best_model_path = best_model_dir / "best_model.joblib"
            joblib.dump(tree_model, best_model_path)
        
        results_dir = Path("classifier/fake_news/models/results")
        results_dir.mkdir(parents=True, exist_ok=True)     
        results_path = results_dir / f"results.json"
        predictions_path = results_dir / f"predictions.csv"
        
        experiment_info = {
            'timestamp': timestamp,
            'data_split': {
                'test_size': test_size,
                'random_state': random_state,
                'train_samples': len(train_df),
                'test_samples': len(test_df),
                'train_fake_ratio': len(train_df[train_df['label']==1]) / len(train_df),
                'test_fake_ratio': len(test_df[test_df['label']==1]) / len(test_df)
            },
            'model_info': model_info
        }
        
        log_experiment(
            model_type='RandomForest',
            data_params=experiment_info['data_split'],
            model_params=model_info['parameters'],
            metrics=model_info['metrics']
        )
        
        with open(results_path, 'w') as f:
            json.dump(experiment_info, f, indent=4, cls=NumpyEncoder)
        
        print("Making predictions on test set...")
        X_test, _ = prepare_features(test_df, sentiment_analyzer)  # Unpack the tuple, ignore feature names
        test_predictions = model.predict(X_test)
        test_df['predicted_label'] = test_predictions
        test_df.to_csv(predictions_path, index=False)
        
        # Get prediction probabilities
        rf_probs = model.predict_proba(X_test)
        
        # Create predictions DataFrame with probabilities
        predictions_df = pd.DataFrame({
            'text': test_df['text'],
            'true_label': test_df['label'],
            'predicted_label': test_predictions,
            'real_probability': rf_probs[:, 1],  # Probability of real news
            'fake_probability': rf_probs[:, 0]   # Probability of fake news
        })
        
        # Save predictions with probabilities
        predictions_path = results_dir / f"predictions.csv"
        predictions_df.to_csv(predictions_path, index=False)
        
        thresholds = np.arange(0.5, 0.95, 0.05)  # Test thresholds from 0.5 to 0.9
        accuracies, invalid_ratios, thresholds = analyze_threshold_performance(predictions_df, thresholds)
        
        # Plot threshold analysis
        plot_path = results_dir / f"threshold_analysis.png"
        plot_threshold_analysis(accuracies, invalid_ratios, thresholds, str(plot_path))
        return results_path, predictions_path

    except Exception as e:
        print(f"Error in pipeline: {str(e)}")
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run fake news detection pipeline')
    parser.add_argument('--test-size', type=float, default=0.2,
                      help='Proportion of data to use for testing (default: 0.2)')
    parser.add_argument('--random-state', type=int, default=42,
                      help='Random seed for reproducibility (defaultpython classifier/fake_news/run_pipeline.py: 42)')
    
    args = parser.parse_args()
    
    results_path, predictions_path = run_pipeline(
        test_size=args.test_size,
        random_state=args.random_state,
    )