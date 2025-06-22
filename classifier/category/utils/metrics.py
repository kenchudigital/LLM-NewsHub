# classifier/category/utils/metrics.py

import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report
)
from typing import Dict, Any

def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray, 
                     y_prob: np.ndarray = None) -> Dict[str, Any]:
    """Calculate comprehensive model evaluation metrics"""
    metrics = {
        'accuracy': accuracy_score(y_true, y_pred),
        'precision': precision_score(y_true, y_pred, average='weighted'),
        'recall': recall_score(y_true, y_pred, average='weighted'),
        'f1': f1_score(y_true, y_pred, average='weighted'),
        'confusion_matrix': confusion_matrix(y_true, y_pred).tolist(),
        'classification_report': classification_report(y_true, y_pred, output_dict=True)
    }
    
    if y_prob is not None:
        from sklearn.metrics import log_loss, roc_auc_score
        metrics['log_loss'] = log_loss(y_true, y_prob)
        metrics['roc_auc'] = roc_auc_score(y_true, y_prob, multi_class='ovr')
    
    return metrics