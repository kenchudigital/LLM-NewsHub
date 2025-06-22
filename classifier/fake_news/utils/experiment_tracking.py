import json
from pathlib import Path
from datetime import datetime
from typing import Dict
import numpy as np

class NumpyEncoder(json.JSONEncoder):
    """Custom encoder for numpy data types"""
    def default(self, obj):
        if isinstance(obj, (np.int_, np.intc, np.intp, np.int8,
                          np.int16, np.int32, np.int64, np.uint8,
                          np.uint16, np.uint32, np.uint64)):
            return int(obj)
        elif isinstance(obj, (np.float_, np.float16, np.float32, np.float64)):
            return float(obj)
        elif isinstance(obj, (np.ndarray,)):
            return obj.tolist()
        return super(NumpyEncoder, self).default(obj)

def log_experiment(model_type: str, data_params: Dict, model_params: Dict, metrics: Dict):
    """Log experiment parameters and results with feature importance"""
    # Ensure metrics are properly formatted
    formatted_metrics = {}
    for key, value in metrics.items():
        if key == 'feature_importance':
            formatted_metrics[key] = value
        elif isinstance(value, (int, float)):
            formatted_metrics[key] = float(value)
        else:
            formatted_metrics[key] = str(value)
    
    experiment = {
        'timestamp': datetime.now().strftime("%Y%m%d_%H%M%S"),
        'model_type': model_type,
        'data_params': data_params,
        'model_params': model_params,
        'metrics': formatted_metrics
    }
    
    results_file = Path("classifier/fake_news/experiments/results.json")
    results_file.parent.mkdir(parents=True, exist_ok=True)
    
    if not results_file.exists():
        with open(results_file, 'w') as f:
            json.dump({'experiments': []}, f, indent=4, cls=NumpyEncoder)
    
    try:
        with open(results_file, 'r') as f:
            all_results = json.load(f)
        
        all_results['experiments'].append(experiment)
        
        with open(results_file, 'w') as f:
            json.dump(all_results, f, indent=4, cls=NumpyEncoder)
            
        print(f"\nExperiment logged: {model_type}")
        print(f"Parameters: {model_params}")
        accuracy = formatted_metrics.get('accuracy')
        if accuracy is not None:
            print(f"Accuracy: {accuracy:.4f}")
        
    except Exception as e:
        print(f"Error logging experiment: {str(e)}")
        backup_file = results_file.parent / f"results_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(backup_file, 'w') as f:
            json.dump({'experiments': [experiment]}, f, indent=4, cls=NumpyEncoder) 