from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score
from sklearn.metrics import accuracy_score, classification_report
import numpy as np
from typing import Dict, Any

from .model_base import BaseClassifier
from .config import RF_CONFIG, PRUNING_CONFIG
from ..utils.experiment_tracking import log_experiment
from .config import DATA_CONFIG

class RandomForestFakeNewsClassifier(BaseClassifier):
    def __init__(self):
        super().__init__(model_name="RandomForest")
        self.base_params = RF_CONFIG['base_params']
        self.tuning_params = RF_CONFIG['tuning_params']
        self.best_params = None
        
    def find_optimal_ccp_alpha(self, X_train, y_train):
        """Find optimal pruning parameter using cross-validation"""
        ccp_alphas = PRUNING_CONFIG['ccp_alpha_range']
        cv_scores = []
        
        for ccp_alpha in ccp_alphas:
            rf = RandomForestClassifier(
                **self.base_params,
                ccp_alpha=ccp_alpha
            )
            scores = cross_val_score(
                rf, X_train, y_train,
                cv=PRUNING_CONFIG['cv_folds']
            )
            cv_scores.append(scores.mean())
        
        optimal_alpha = ccp_alphas[np.argmax(cv_scores)]
        return optimal_alpha
        
    def train(self, X_train, y_train, X_val, y_val) -> Dict[str, Any]:
        """Train model with parameter tuning and pruning"""
        print("Training Random Forest with parameter tuning and pruning...")
        
        best_accuracy = 0
        total_combinations = np.prod([len(v) for v in self.tuning_params.values()])
        current_combination = 0
        
        # Find optimal pruning parameter
        optimal_ccp_alpha = self.find_optimal_ccp_alpha(X_train, y_train)
        print(f"Optimal pruning parameter (ccp_alpha): {optimal_ccp_alpha}")
        
        # Grid search with pruning
        for n_estimators in self.tuning_params['n_estimators']:
            for max_depth in self.tuning_params['max_depth']:
                for min_samples_split in self.tuning_params['min_samples_split']:
                    for min_samples_leaf in self.tuning_params['min_samples_leaf']:
                        for max_features in self.tuning_params['max_features']:
                            for class_weight in self.tuning_params['class_weight']:
                                current_combination += 1
                                print(f"\nTrying combination {current_combination}/{total_combinations}")
                                
                                params = {
                                    'n_estimators': n_estimators,
                                    'max_depth': max_depth,
                                    'min_samples_split': min_samples_split,
                                    'min_samples_leaf': min_samples_leaf,
                                    'max_features': max_features,
                                    'class_weight': class_weight,
                                    'ccp_alpha': optimal_ccp_alpha,
                                    **self.base_params
                                }
                                
                                # Train model
                                current_model = RandomForestClassifier(**params)
                                current_model.fit(X_train, y_train)
                                
                                # Evaluate
                                val_pred = current_model.predict(X_val)
                                accuracy = accuracy_score(y_val, val_pred)
                                cv_scores = cross_val_score(current_model, X_val, y_val, cv=5)
                                
                                print(f"Parameters: {params}")
                                print(f"Validation Accuracy: {accuracy:.4f}")
                                print(f"CV Scores Mean: {cv_scores.mean():.4f} (±{cv_scores.std()*2:.4f})")
                                
                                # Log experiment
                                log_experiment(
                                    model_type='RandomForest',
                                    data_params=DATA_CONFIG,
                                    model_params=params,
                                    metrics={
                                        'accuracy': float(accuracy),
                                        'cv_mean': float(cv_scores.mean()),
                                        'cv_std': float(cv_scores.std()),
                                        'cv_scores': cv_scores.tolist()
                                    }
                                )
                                
                                # Update best model
                                if accuracy > best_accuracy:
                                    best_accuracy = accuracy
                                    self.best_params = params
                                    self.model = current_model
                                    self.metrics = {
                                        'accuracy': accuracy,
                                        'cv_scores': {
                                            'mean': cv_scores.mean(),
                                            'std': cv_scores.std(),
                                            'scores': cv_scores.tolist()
                                        },
                                        'best_params': params,
                                        'feature_importance': dict(zip(
                                            range(X_train.shape[1]),
                                            current_model.feature_importances_
                                        ))
                                    }
                                    self.save_model(is_best=True)
        
        print(f"Best parameters: {self.best_params}")
        print(f"Best accuracy: {best_accuracy:.4f}")
        
        return self.metrics