# classifier/category/models/model_svc.py

import os
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.svm import SVC
from sklearn.model_selection import GridSearchCV, cross_val_score
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from datetime import datetime
import json
import time
from typing import Dict, Any, Tuple, Optional

from classifier.category.models.model_base import BaseClassifier
from classifier.category.models.config import SVC_CONFIG, DATA_CONFIG, VIZ_CONFIG
from ..utils.experiment_tracking import log_experiment

class SVCClassifier(BaseClassifier):
    def __init__(self, model_params: Optional[Dict[str, Any]] = None):
        super().__init__(model_name="SVC")
        # If model_params is provided, use them; otherwise use default config
        if model_params is not None:
            self.param_grid = {k: [v] for k, v in model_params.items()}
            self.best_params = model_params
        else:
            self.param_grid = SVC_CONFIG['param_grid']
            self.best_params = None
        
    def train(self, X_train: np.ndarray, y_train: np.ndarray, 
            X_val: np.ndarray, y_val: np.ndarray) -> Dict[str, Any]:
        """Train SVC model with GridSearchCV"""
        print("Training SVC model with GridSearchCV...")
        
        # Initialize base model
        base_model = SVC(probability=True)
        
        # Calculate total combinations
        total_combinations = (
            len(self.param_grid['C']) * 
            len(self.param_grid['kernel']) * 
            len(self.param_grid['gamma']) *
            len(self.param_grid.get('degree', [2])) *
            len(self.param_grid.get('class_weight', [None]))
        )
        print(f"\nWill try {total_combinations} parameter combinations")
        
        best_accuracy = 0
        best_params = None
        current_combination = 0
        
        # Try each parameter combination
        for C in self.param_grid['C']:
            for kernel in self.param_grid['kernel']:
                for gamma in self.param_grid['gamma']:
                    for degree in self.param_grid.get('degree', [2]):
                        for class_weight in self.param_grid.get('class_weight', [None]):
                            current_combination += 1
                            print(f"\nTrying combination {current_combination}/{total_combinations}")
                            
                            params = {
                                'C': C,
                                'kernel': kernel,
                                'gamma': gamma,
                                'degree': degree,
                                'class_weight': class_weight
                            }
                            print(f"Parameters: C={C}, kernel={kernel}, gamma={gamma}, degree={degree}, class_weight={class_weight}")
                            
                            # Train model with current parameters
                            current_model = SVC(probability=True, **params)
                            current_model.fit(X_train, y_train)
                            
                            # Evaluate
                            val_pred = current_model.predict(X_val)
                            accuracy = accuracy_score(y_val, val_pred)
                            cv_scores = cross_val_score(current_model, X_val, y_val, cv=5)
                            
                            print(f"Validation Accuracy: {accuracy:.4f}")
                            print(f"CV Scores Mean: {cv_scores.mean():.4f} (±{cv_scores.std()*2:.4f})")
                            
                            # Log experiment
                            log_experiment(
                                model_type='SVC',
                                data_params=DATA_CONFIG,
                                model_params=params,
                                metrics={
                                    'accuracy': float(accuracy),
                                    'cv_mean': float(cv_scores.mean()),
                                    'cv_std': float(cv_scores.std()),
                                    'cv_scores': cv_scores.tolist()
                                }
                            )
                            
                            # Update best model if current is better
                            if accuracy > best_accuracy:
                                print("📈 New best model found!")
                                best_accuracy = accuracy
                                best_params = params
                                self.model = current_model
                                self.best_params = params
                                self.metrics = {
                                    'accuracy': accuracy,
                                    'cv_scores': {
                                        'mean': cv_scores.mean(),
                                        'std': cv_scores.std(),
                                        'scores': cv_scores.tolist()
                                    },
                                    'best_params': params
                                }
                                # Save best model
                                self.save_model(is_best=True)
        
        print("\nSVC training completed!")
        print(f"Best parameters: {self.best_params}")
        print(f"Best accuracy: {best_accuracy:.4f}")
        
        return self.metrics
    
    def evaluate(self, X_val: np.ndarray, y_val: np.ndarray) -> Dict[str, Any]:
        """Evaluate the model and return comprehensive metrics"""
        val_pred = self.model.predict(X_val)
        val_prob = self.model.predict_proba(X_val)
        
        # Calculate metrics
        accuracy = accuracy_score(y_val, val_pred)
        cv_scores = cross_val_score(self.model, X_val, y_val, cv=5)
        report = classification_report(y_val, val_pred, output_dict=True)
        cm = confusion_matrix(y_val, val_pred)
        
        return {
            'accuracy': accuracy,
            'cv_scores': {
                'mean': cv_scores.mean(),
                'std': cv_scores.std(),
                'scores': cv_scores.tolist()
            },
            'classification_report': report,
            'confusion_matrix': cm.tolist(),
            'best_params': self.best_params
        }
    
    def _create_visualizations(self, metrics: Dict[str, Any]):
        """Create and save model visualizations"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        viz_dir = self.results_dir / "visualizations"
        
        # 1. Confusion Matrix
        cm = np.array(metrics['confusion_matrix'])
        plt.figure(figsize=VIZ_CONFIG['figsize']['confusion_matrix'])
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                   xticklabels=self.label_encoder.classes_,
                   yticklabels=self.label_encoder.classes_)
        plt.title('SVC Confusion Matrix')
        plt.xlabel('Predicted')
        plt.ylabel('Actual')
        plt.tight_layout()
        plt.savefig(viz_dir / f'confusion_matrix_{timestamp}.png')
        plt.close()
        
        # 2. Cross-validation scores
        cv_scores = metrics['cv_scores']['scores']
        plt.figure(figsize=VIZ_CONFIG['figsize']['comparison'])
        plt.boxplot(cv_scores)
        plt.title('SVC Cross-validation Scores')
        plt.ylabel('Accuracy')
        plt.savefig(viz_dir / f'cv_scores_{timestamp}.png')
        plt.close()
        
        # 3. Per-class accuracy
        class_acc = cm.diagonal() / cm.sum(axis=1)
        plt.figure(figsize=VIZ_CONFIG['figsize']['comparison'])
        bars = plt.bar(self.label_encoder.classes_, class_acc, 
                      color=sns.color_palette("viridis", len(class_acc)))
        plt.title('SVC Per-Class Accuracy')
        plt.xlabel('Category')
        plt.ylabel('Accuracy')
        plt.xticks(rotation=45)
        
        # Add value labels on bars
        for bar, acc in zip(bars, class_acc):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, 
                    f'{acc:.3f}', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(viz_dir / f'per_class_accuracy_{timestamp}.png')
        plt.close()