# classifier/category/select_best_model.py

import os
import sys
from pathlib import Path
import argparse
import json
import shutil
from datetime import datetime

def select_best_model(results_dir: str, output_dir: str = None) -> str:
    """Select the best performing model based on validation accuracy"""
    results_dir = Path(results_dir)
    
    # Find all model results
    knn_results = list(results_dir.glob("knn/best_models/*.joblib"))
    svc_results = list(results_dir.glob("svc/best_models/*.joblib"))
    
    if not knn_results and not svc_results:
        print("No model results found!")
        return None
    
    # Compare models and select best
    best_model_path = None
    best_accuracy = -1
    
    for model_path in knn_results + svc_results:
        metrics_path = model_path.parent.parent / "metrics" / f"{model_path.stem}_metrics.json"
        if metrics_path.exists():
            with open(metrics_path, 'r') as f:
                metrics = json.load(f)
                accuracy = metrics.get('accuracy', 0)
                if accuracy > best_accuracy:
                    best_accuracy = accuracy
                    best_model_path = model_path
    
    if best_model_path is None:
        print("No valid model metrics found!")
        return None
    
    # Copy best model to output directory if specified
    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        new_model_path = output_dir / best_model_path.name
        shutil.copy2(best_model_path, new_model_path)
        print(f"Best model copied to: {new_model_path}")
        return str(new_model_path)
    
    return str(best_model_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Select best performing model')
    parser.add_argument('--results', type=str, required=True,
                      help='Path to results directory')
    parser.add_argument('--output', type=str,
                      help='Path to output directory for best model')
    
    args = parser.parse_args()
    
    best_model_path = select_best_model(args.results, args.output)