from typing import List, Dict
from scipy.stats import ttest_ind
from sklearn.metrics import confusion_matrix
import numpy as np

def mcnemar_test(y_true, pred1, pred2):
    """
    Custom implementation of McNemar's test
    """
    # Create contingency table
    b01 = np.sum((pred1 == y_true) & (pred2 != y_true))
    b10 = np.sum((pred1 != y_true) & (pred2 == y_true))
    
    # Calculate statistic
    statistic = (abs(b01 - b10) - 1)**2 / (b01 + b10)
    
    # Calculate p-value (chi-squared with df=1)
    from scipy.stats import chi2
    p_value = 1 - chi2.cdf(statistic, df=1)
    
    return statistic, p_value

def compare_models(model1_results: List, model2_results: List, model1_preds: np.ndarray = None, model2_preds: np.ndarray = None, true_labels: np.ndarray = None):
    """Compare two models using statistical tests
    
    Args:
        model1_results: List of CV scores from first model
        model2_results: List of CV scores from second model
        model1_preds: Predictions from first model (for McNemar's test)
        model2_preds: Predictions from second model (for McNemar's test)
        true_labels: True labels (for McNemar's test)
    """
    results = {}
    
    # Perform t-test on CV scores
    t_stat, p_value = ttest_ind(model1_results, model2_results)
    results['t_test'] = {
        'statistic': float(t_stat),
        'p_value': float(p_value)
    }
    
    # Perform McNemar's test if predictions are provided
    if all(v is not None for v in [model1_preds, model2_preds, true_labels]):
        mcnemar_stat, mcnemar_p = mcnemar_test(true_labels, model1_preds, model2_preds)
        
        results['mcnemar'] = {
            'statistic': float(mcnemar_stat),
            'p_value': float(mcnemar_p)
        }
    
    return results