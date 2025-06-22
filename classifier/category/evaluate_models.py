import json
import joblib
from pathlib import Path
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import numpy as np
from datetime import datetime

from classifier.category.models.model_knn import KNNClassifier
from classifier.category.models.model_svc import SVCClassifier

def evaluate_model(model, X_test, y_test):
    """
    Evaluate a model using multiple metrics
    """
    _, probabilities = model.predict(X_test)
    predictions = np.argmax(probabilities, axis=1)
    
    # Calculate metrics
    accuracy = accuracy_score(y_test, predictions)
    precision, recall, f1, _ = precision_recall_fscore_support(y_test, predictions, average='weighted')
    
    return {
        'accuracy': float(accuracy),
        'precision': float(precision),
        'recall': float(recall),
        'f1_score': float(f1)
    }

def compare_and_select_best_model(train_data_path: str, test_data_path: str, output_dir: str = "classifier/category/models/best_models"):
    """
    Compare different models and select the best one based on evaluation metrics
    
    Args:
        train_data_path (str): Path to training data CSV
        test_data_path (str): Path to test data CSV
        output_dir (str): Directory to save the best model and its metadata
    """
    # Create output directory if it doesn't exist
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Define models to compare with their parameters
    models_to_compare = [
        {
            'name': 'KNN',
            'model': KNNClassifier(),
            'params': {'n_neighbors': 5}
        },
        {
            'name': 'KNN',
            'model': KNNClassifier(),
            'params': {'n_neighbors': 3}
        },
        {
            'name': 'SVC',
            'model': SVCClassifier(),
            'params': {'kernel': 'linear', 'probability': True}
        },
        {
            'name': 'SVC',
            'model': SVCClassifier(),
            'params': {'kernel': 'rbf', 'probability': True}
        }
    ]
    
    best_score = -1
    best_model = None
    best_model_info = None
    
    print("Starting model comparison...")
    
    for model_config in models_to_compare:
        model = model_config['model']
        print(f"\nTraining {model_config['name']} with params: {model_config['params']}")
        
        # Train model
        model.train(train_data_path, model_config['params'])
        
        # Load test data and evaluate
        model.load_test_data(test_data_path)
        X_test = model.vectorizer.transform(model.test_df['Text'].values)
        y_test = model.label_encoder.transform(model.test_df['Category'].values)
        
        # Get evaluation metrics
        metrics = evaluate_model(model, X_test, y_test)
        
        print(f"Results for {model_config['name']}:")
        for metric, value in metrics.items():
            print(f"- {metric}: {value:.3f}")
        
        # Use F1 score as the primary metric for model selection
        if metrics['f1_score'] > best_score:
            best_score = metrics['f1_score']
            best_model = model
            best_model_info = {
                'model_type': model_config['name'],
                'parameters': model_config['params'],
                'metrics': metrics,
                'features': {
                    'vectorizer_type': type(model.vectorizer).__name__,
                    'n_features': model.vectorizer.get_feature_names_out().shape[0]
                },
                'categories': list(model.label_encoder.classes_),
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'training_data': train_data_path,
                'test_data': test_data_path
            }
    
    # Save the best model and its metadata
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_path = output_dir / f"best_model.joblib"
    metadata_path = output_dir / f"best_model.json"
    
    print(f"\n✨ Saving best model ({best_model_info['model_type']}) with F1 score: {best_score:.3f}")
    
    # Save model
    best_model.save_model(str(model_path))
    
    # Save metadata
    with open(metadata_path, 'w') as f:
        json.dump(best_model_info, f, indent=4)
    
    print(f"Model saved to: {model_path}")
    print(f"Model metadata saved to: {metadata_path}")
    
    return best_model, best_model_info

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Compare models and select the best one')
    parser.add_argument('--train', type=str, required=True,
                      help='Path to training data CSV')
    parser.add_argument('--test', type=str, required=True,
                      help='Path to test data CSV')
    parser.add_argument('--output', type=str, default="classifier/category/models/best_models",
                      help='Directory to save the best model')
    
    args = parser.parse_args()
    
    best_model, best_info = compare_and_select_best_model(args.train, args.test, args.output) 