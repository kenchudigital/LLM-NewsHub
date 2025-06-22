import os
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import cross_val_score
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from datetime import datetime
import json
import time
from typing import Dict, Any, Tuple, List, Optional

from classifier.category.models.model_base import BaseClassifier
from classifier.category.models.config import KNN_CONFIG, VIZ_CONFIG, DATA_CONFIG

from ..utils.experiment_tracking import log_experiment
from ..utils.statistical_tests import compare_models

class KNNClassifier(BaseClassifier):
    def __init__(self, model_params: Optional[Dict[str, Any]] = None):
        super().__init__(model_name="KNN")
        # If model_params is provided, use them; otherwise use default config
        if model_params is not None:
            self.k_values = [model_params.get('n_neighbors', KNN_CONFIG['k_values'][0])]
            self.distance_metrics = [model_params.get('metric', KNN_CONFIG['metrics'][0])]
            self.weights = [model_params.get('weights', KNN_CONFIG['weights'][0])]
            self.best_params = model_params
        else:
            self.k_values = KNN_CONFIG['k_values']
            self.distance_metrics = KNN_CONFIG['metrics']
            self.weights = KNN_CONFIG['weights']
            self.best_params = None
        self.metrics = {}
        
    def train(self, X_train: np.ndarray, y_train: np.ndarray, 
              X_val: np.ndarray, y_val: np.ndarray) -> Dict[str, Any]:
        """Train KNN models with different parameters"""
        print("Training KNN models with different parameters...")
        
        best_accuracy = 0
        best_model = None
        total_combinations = len(self.k_values) * len(self.distance_metrics) * len(self.weights)
        current_combination = 0
        
        for k in self.k_values:
            for metric in self.distance_metrics:
                for weight in self.weights:
                    current_combination += 1
                    print(f"\nTrying combination {current_combination}/{total_combinations}")
                    print(f"Parameters: k={k}, metric={metric}, weights={weight}")
                    
                    params = {
                        'n_neighbors': k,
                        'metric': metric,
                        'weights': weight
                    }
                    
                    # Train model with current parameters
                    current_model = KNeighborsClassifier(**params)
                    current_model.fit(X_train, y_train)
                    
                    # Evaluate
                    val_pred = current_model.predict(X_val)
                    accuracy = accuracy_score(y_val, val_pred)
                    cv_scores = cross_val_score(current_model, X_val, y_val, cv=5)
                    
                    print(f"Validation Accuracy: {accuracy:.4f}")
                    print(f"CV Scores Mean: {cv_scores.mean():.4f} (±{cv_scores.std()*2:.4f})")
                    
                    # Log experiment immediately
                    log_experiment(
                        model_type='KNN',
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
                        best_model = current_model
                        self.best_params = params
                        self.model = best_model
                        self.metrics = {
                            'accuracy': accuracy,
                            'cv_scores': {
                                'mean': cv_scores.mean(),
                                'std': cv_scores.std(),
                                'scores': cv_scores.tolist()
                            },
                            'best_params': params
                        }
                        # Save best model immediately
                        self.save_model(is_best=True)
        
        print("\nKNN training completed!")
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
    
    def _create_visualizations(self, results_df: pd.DataFrame, metrics: Dict[str, Any]):
        """Create and save model visualizations"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        viz_dir = self.results_dir / "visualizations"
        
        # 1. Accuracy vs K for different metrics
        plt.figure(figsize=VIZ_CONFIG['figsize']['comparison'])
        plt.subplot(2, 3, 1)
        for metric in self.distance_metrics:
            for weight in self.weights:
                subset = results_df[(results_df['metric'] == metric) & 
                                  (results_df['weights'] == weight)]
                plt.plot(subset['k'], subset['accuracy'], marker='o', 
                        label=f'{metric}-{weight}')
        plt.title('KNN Accuracy vs K Value')
        plt.xlabel('K Value')
        plt.ylabel('Validation Accuracy')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.savefig(viz_dir / f'accuracy_vs_k_{timestamp}.png')
        plt.close()
        
        # 2. Training time vs K
        plt.figure(figsize=VIZ_CONFIG['figsize']['comparison'])
        plt.subplot(2, 3, 2)
        for metric in self.distance_metrics:
            subset = results_df[results_df['metric'] == metric]
            avg_time = subset.groupby('k')['time'].mean()
            plt.plot(avg_time.index, avg_time.values, marker='s', label=metric)
        plt.title('Training Time vs K Value')
        plt.xlabel('K Value')
        plt.ylabel('Training Time (seconds)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.savefig(viz_dir / f'training_time_{timestamp}.png')
        plt.close()
        
        # 3. Confusion Matrix
        cm = np.array(metrics['confusion_matrix'])
        plt.figure(figsize=VIZ_CONFIG['figsize']['confusion_matrix'])
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                   xticklabels=self.label_encoder.classes_,
                   yticklabels=self.label_encoder.classes_)
        plt.title('KNN Confusion Matrix')
        plt.xlabel('Predicted')
        plt.ylabel('Actual')
        plt.tight_layout()
        plt.savefig(viz_dir / f'confusion_matrix_{timestamp}.png')
        plt.close()
        
        # 4. Cross-validation scores
        cv_scores = metrics['cv_scores']['scores']
        plt.figure(figsize=VIZ_CONFIG['figsize']['comparison'])
        plt.boxplot(cv_scores)
        plt.title('KNN Cross-validation Scores')
        plt.ylabel('Accuracy')
        plt.savefig(viz_dir / f'cv_scores_{timestamp}.png')
        plt.close()