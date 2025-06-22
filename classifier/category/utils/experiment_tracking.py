import json
from pathlib import Path
from datetime import datetime
from typing import Dict
import os

def log_experiment(model_type: str, data_params: Dict, model_params: Dict, metrics: Dict):
    """Log experiment parameters and results"""
    experiment = {
        'timestamp': datetime.now().strftime("%Y%m%d_%H%M%S"),
        'model_type': model_type,
        'data_params': data_params,
        'model_params': model_params,
        'metrics': metrics
    }
    
    # Create experiments directory if it doesn't exist
    experiments_dir = Path("classifier/category/experiments")
    results_file = experiments_dir / "results.json"
    
    # Ensure directory exists
    experiments_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize file if it doesn't exist
    if not results_file.exists():
        with open(results_file, 'w') as f:
            json.dump({'experiments': []}, f, indent=4)
    
    try:
        # Read existing results
        with open(results_file, 'r') as f:
            try:
                all_results = json.load(f)
            except json.JSONDecodeError:
                print("Warning: Results file was corrupted. Creating new file.")
                all_results = {'experiments': []}
        
        # Append new experiment
        all_results['experiments'].append(experiment)
        
        # Write back to file
        with open(results_file, 'w') as f:
            json.dump(all_results, f, indent=4)
            
        # Print confirmation
        print(f"\nExperiment logged: {model_type} with parameters:")
        print(f"- Model params: {model_params}")
        print(f"- Accuracy: {metrics.get('accuracy', metrics.get('cv_mean', 'N/A'))}")
        
    except Exception as e:
        print(f"Error logging experiment: {str(e)}")
        # Save to backup file
        backup_file = experiments_dir / f"results_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(backup_file, 'w') as f:
            json.dump({'experiments': [experiment]}, f, indent=4)
        print(f"Backup saved to: {backup_file}")