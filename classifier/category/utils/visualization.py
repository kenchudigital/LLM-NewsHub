# classifier/category/utils/visualization.py

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import List, Dict, Any
from datetime import datetime
import os

from ..models.config import VIZ_CONFIG

def plot_confusion_matrix(cm: np.ndarray, classes: List[str], 
                         model_name: str, save_path: str = None):
    """Plot and save confusion matrix"""
    plt.figure(figsize=VIZ_CONFIG['figsize']['confusion_matrix'])
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=classes,
                yticklabels=classes)
    plt.title(f'{model_name} Confusion Matrix')
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path)
        plt.close()
    else:
        plt.show()

def plot_learning_curves(train_sizes: np.ndarray, train_scores: np.ndarray,
                        val_scores: np.ndarray, model_name: str, save_path: str = None):
    """Plot and save learning curves"""
    plt.figure(figsize=VIZ_CONFIG['figsize']['learning_curves'])
    plt.plot(train_sizes, np.mean(train_scores, axis=1), label='Training score')
    plt.plot(train_sizes, np.mean(val_scores, axis=1), label='Cross-validation score')
    plt.xlabel('Training Examples')
    plt.ylabel('Score')
    plt.title(f'{model_name} Learning Curves')
    plt.legend(loc='best')
    plt.grid(True)
    
    if save_path:
        plt.savefig(save_path)
        plt.close()
    else:
        plt.show()