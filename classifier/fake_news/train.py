import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier, plot_tree, export_text
from sklearn.model_selection import train_test_split
import joblib
import json
from datetime import datetime
from pathlib import Path
from typing import Tuple, Dict, Any, List
import matplotlib.pyplot as plt
from .utils.sentiment_utils import SentimentAnalyzer
from .utils.visualization import plot_feature_importance, plot_confusion_matrix
from .utils.metrics import calculate_metrics
from .utils.experiment_tracking import log_experiment, NumpyEncoder
from .utils.feature_cache import save_features, load_features
from .utils.feature_extractor import FeatureExtractor
from .utils.tree_visualization import find_optimal_pruning, visualize_tree

def prepare_features(df: pd.DataFrame, sentiment_analyzer: SentimentAnalyzer) -> Tuple[np.ndarray, List[str]]:
    """Prepare features for the model"""
    # Initialize feature extractor
    feature_extractor = FeatureExtractor()
    
    # Get sentiment features
    sentiment_features = sentiment_analyzer.extract_features(df)
    
    # Get additional features
    additional_features = feature_extractor.extract_all_features(df)
    
    # Combine all features
    all_features = pd.concat([sentiment_features, additional_features], axis=1)
    
    # Get feature names
    feature_names = (
        sentiment_analyzer.get_feature_names() + 
        feature_extractor.get_feature_names()
    )
    
    return all_features.values, feature_names

def train_model(
    train_df: pd.DataFrame, 
    test_df: pd.DataFrame,
    sentiment_analyzer: SentimentAnalyzer,
    output_dir: str = "classifier/fake_news/models"
) -> Tuple[RandomForestClassifier, Dict[str, Any]]:
    """Train the fake news detection model"""
    print("Preparing features...")
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create results directory for all output files
    results_dir = output_dir / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    
    # Try to load cached features
    cached_train = load_features('train')
    cached_test = load_features('test')
    
    if cached_train is None or cached_test is None:
        print("Computing features...")
        X_train, feature_names = prepare_features(train_df, sentiment_analyzer)
        y_train = train_df['label'].values
        X_test, _ = prepare_features(test_df, sentiment_analyzer)
        y_test = test_df['label'].values
        
        # Save computed features and feature names
        save_features(X_train, y_train, 'train')
        save_features(X_test, y_test, 'test')
        # Save feature names to results directory
        with open(results_dir / 'feature_names.json', 'w') as f:
            json.dump({'feature_names': feature_names}, f)
    else:
        X_train, y_train = cached_train
        X_test, y_test = cached_test
        # Try to load feature names, if not available, compute them
        feature_names_path = results_dir / 'feature_names.json'
        if feature_names_path.exists():
            with open(feature_names_path, 'r') as f:
                feature_names = json.load(f)['feature_names']
        else:
            print("Feature names not found, computing them...")
            _, feature_names = prepare_features(train_df, sentiment_analyzer)
            # Save feature names for future use
            with open(feature_names_path, 'w') as f:
                json.dump({'feature_names': feature_names}, f)
    
    # Update model parameters for the new feature set
    rf_params = {
        'n_estimators': 200,
        'max_depth': 10,
        'min_samples_split': 5,
        'min_samples_leaf': 2,
        'random_state': 42,
        'n_jobs': -1,
        'class_weight': 'balanced'
    }
    
    tree_params = {
        'max_depth': 3,
        'min_samples_split': 100,
        'min_samples_leaf': 50,
        'random_state': 42
    }
    
    # Split validation set for tree pruning
    X_train_main, X_val, y_train_main, y_val = train_test_split(
        X_train, y_train, test_size=0.2, random_state=42
    )
    
    # Train Random Forest model
    print("Training Random Forest model...")
    rf_model = RandomForestClassifier(**rf_params)
    rf_model.fit(X_train, y_train)
    
    # Train and visualize decision tree
    tree_model, best_ccp_alpha = find_optimal_pruning(
        X_train_main, y_train_main,
        X_val, y_val,
        max_depth=5
    )
    
    print(f"Optimal pruning parameter (ccp_alpha): {best_ccp_alpha:.4f}")
    tree_viz_dir = Path("classifier/fake_news/models/results/tree_visualizations")
    tree_stats = visualize_tree(
        tree_model,
        feature_names,
        tree_viz_dir
    )
    
    rf_pred = rf_model.predict(X_test)
    rf_prob = rf_model.predict_proba(X_test)
    
    tree_pred = tree_model.predict(X_test)
    tree_prob = tree_model.predict_proba(X_test)
    
    feature_importance = dict(zip(feature_names, rf_model.feature_importances_))
    
    rf_metrics = calculate_metrics(y_test, rf_pred, rf_prob)
    tree_metrics = calculate_metrics(y_test, tree_pred, tree_prob)
    
    rf_metrics['feature_importance'] = feature_importance
    
    # Save visualizations to results directory
    plot_feature_importance(feature_importance).savefig(
        results_dir / 'feature_importance.png'
    )
    plot_confusion_matrix(
        rf_metrics['confusion_matrix'], 
        ['Real News', 'Fake News']
    ).savefig(results_dir / 'confusion_matrix.png')
    
    # Plot and save decision tree to results directory
    plt.figure(figsize=(20, 10))
    plot_tree(tree_model, 
             feature_names=feature_names,
             class_names=['Real News', 'Fake News'],
             filled=True,
             rounded=True)
    plt.savefig(results_dir / 'decision_tree.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Save tree rules to results directory
    try:
        tree_rules = export_text(tree_model, feature_names=feature_names)
        with open(results_dir / 'decision_tree_rules.txt', 'w') as f:
            f.write(tree_rules)
    except Exception as e:
        print(f"Error exporting tree rules: {e}")
    
    # Create model info
    model_info = {
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'model_type': 'RandomForest',
        'features': feature_names,
        'feature_importance': feature_importance,
        'metrics': {
            'random_forest': rf_metrics,
            'decision_tree': tree_metrics
        },
        'parameters': {
            'random_forest': rf_params,
            'decision_tree': tree_params
        },
        'tree_stats': tree_stats,
        'tree_ccp_alpha': best_ccp_alpha
    }
    
    # Log experiment
    data_params = {
        'train_samples': len(train_df),
        'test_samples': len(test_df),
        'feature_count': len(feature_names)
    }
    
    log_experiment(
        model_type='RandomForest',
        data_params=data_params,
        model_params=rf_params,
        metrics=rf_metrics
    )
    
    log_experiment(
        model_type='DecisionTree',
        data_params=data_params,
        model_params=tree_params,
        metrics=tree_metrics
    )
    
    # Save models and info to results directory
    joblib.dump(rf_model, results_dir / 'random_forest_model.joblib')
    joblib.dump(tree_model, results_dir / 'decision_tree_model.joblib')
    with open(results_dir / 'model_info.json', 'w') as f:
        json.dump(model_info, f, indent=4, cls=NumpyEncoder)
    
    print("\nTraining completed!")
    return rf_model, model_info

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Train fake news detection model')
    parser.add_argument('--train', type=str, required=True, help='Path to training data')
    parser.add_argument('--test', type=str, required=True, help='Path to test data')
    parser.add_argument('--output', type=str, default='classifier/fake_news/models',
                      help='Output directory for model and metadata')
    
    args = parser.parse_args()
    train_df = pd.read_csv(args.train)
    test_df = pd.read_csv(args.test)
    sentiment_analyzer = SentimentAnalyzer()
    model, model_info = train_model(train_df, test_df, sentiment_analyzer, args.output)