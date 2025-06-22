# classifier/category/run_pipeline.py

import os
import sys
from pathlib import Path
import argparse
import json
import joblib
from datetime import datetime
import shlex

def find_best_model_from_results(results_file: str, model_type: str):
    """Find the best model configuration from results.json"""
    with open(results_file, 'r') as f:
        results = json.load(f)
    
    # Filter experiments by model type and find the one with highest accuracy
    best_exp = None
    best_accuracy = -1
    
    for exp in results['experiments']:
        if exp['model_type'].lower() == model_type.lower():
            if exp['metrics']['accuracy'] > best_accuracy:
                best_accuracy = exp['metrics']['accuracy']
                best_exp = exp
    
    return best_exp

def save_model_info(model_info: dict, save_path: str):
    """Save model information to JSON"""
    with open(save_path, 'w') as f:
        json.dump(model_info, f, indent=4)

def format_params_for_cli(params: dict) -> str:
    """Format parameters as a string that can be safely passed on command line"""
    # Convert each parameter to a string representation
    param_strings = []
    for key, value in params.items():
        if isinstance(value, str):
            param_strings.append(f"{key}={shlex.quote(value)}")
        else:
            param_strings.append(f"{key}={value}")
    
    return ",".join(param_strings)

def run_pipeline(train_path: str, test_path: str):
    """Run the complete model training and evaluation pipeline"""
    print("Starting BBC News Classification Pipeline")
    print("="*60)
    
    # Create necessary directories
    Path("classifier/category/models/best_models/knn").mkdir(parents=True, exist_ok=True)
    Path("classifier/category/models/best_models/svc").mkdir(parents=True, exist_ok=True)
    
    # 1. Train KNN model
    print("\n1.Training KNN models...")
    os.system(f"python classifier/category/train.py --model knn --train {train_path} --test {test_path}")
    
    # 2. Train SVC model
    print("\n2. Training SVC models...")
    os.system(f"python classifier/category/train.py --model svc --train {train_path} --test {test_path}")
    
    # 3. Find best KNN and SVC models
    print("\n3. Finding best models...")
    results_file = "classifier/category/experiments/results.json"
    
    best_knn = find_best_model_from_results(results_file, "KNN")
    best_svc = find_best_model_from_results(results_file, "SVC")
    
    # Save best KNN model
    knn_model_path = "classifier/category/models/best_models/knn/best_knn.joblib"
    knn_info_path = "classifier/category/models/best_models/knn/best_knn.json"
    knn_params = format_params_for_cli(best_knn['model_params'])
    os.system(f"python classifier/category/train.py --model knn --train {train_path} --test {test_path} "
             f"--model-params {knn_params} --save-model {knn_model_path}")
    save_model_info(best_knn, knn_info_path)
    
    # Save best SVC model
    svc_model_path = "classifier/category/models/best_models/svc/best_svc.joblib"
    svc_info_path = "classifier/category/models/best_models/svc/best_svc.json"
    svc_params = format_params_for_cli(best_svc['model_params'])
    os.system(f"python classifier/category/train.py --model svc --train {train_path} --test {test_path} "
             f"--model-params {svc_params} --save-model {svc_model_path}")
    save_model_info(best_svc, svc_info_path)
    
    # 4. Compare best models and select final best
    print("\n4. Selecting final best model...")
    if best_knn['metrics']['accuracy'] > best_svc['metrics']['accuracy']:
        best_model = best_knn
        best_model_src = knn_model_path
    else:
        best_model = best_svc
        best_model_src = svc_model_path
    
    # # Save final best model
    best_model_path = "classifier/category/models/best_models/best_model.joblib"
    best_model_info_path = "classifier/category/models/best_models/best_model.json"
    
    # Copy best model file
    os.system(f"cp {best_model_src} {best_model_path}")
    save_model_info(best_model, best_model_info_path)
    
    # 5. Analyze results (ignoring timestamps)
    print("\n5. Analyzing results...")
    os.system(f"python classifier/category/analyze_results.py --results classifier/category/results")
    
    print("\nPipeline complete!")
    print(f"Results and analysis saved in: classifier/category/results")
    print(f"Best model saved as: {best_model_path}")
    print(f"Best model info saved as: {best_model_info_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run complete classification pipeline')
    parser.add_argument('--train', type=str, required=True,
                      help='Path to training data CSV')
    parser.add_argument('--test', type=str, required=True,
                      help='Path to test data CSV')
    
    args = parser.parse_args()
    
    run_pipeline(args.train, args.test)