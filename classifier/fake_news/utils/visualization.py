import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import Dict, List
import pandas as pd

def plot_feature_importance(feature_importance: Dict[str, float], top_n: int = 20):
    """Plot top N most important features"""
    plt.figure(figsize=(12, 6))
    
    # Sort features by importance
    sorted_features = sorted(
        feature_importance.items(),
        key=lambda x: x[1],
        reverse=True
    )[:top_n]
    
    # Create plot
    features, importance = zip(*sorted_features)
    plt.barh(range(len(features)), importance)
    plt.yticks(range(len(features)), features)
    plt.xlabel('Importance')
    plt.title(f'Top {top_n} Most Important Features')
    plt.tight_layout()
    
    return plt.gcf()

def plot_sentiment_distribution(df: pd.DataFrame, sentiment_columns: List[str]):
    """Plot distribution of sentiment scores"""
    plt.figure(figsize=(15, 5 * len(sentiment_columns)))
    
    for i, col in enumerate(sentiment_columns, 1):
        plt.subplot(len(sentiment_columns), 1, i)
        sns.histplot(data=df, x=col, hue='label', bins=50)
        plt.title(f'Distribution of {col} by Label')
    
    plt.tight_layout()
    return plt.gcf()

def plot_confusion_matrix(cm: np.ndarray, labels: List[str]):
    """Plot confusion matrix heatmap"""
    plt.figure(figsize=(10, 8))
    sns.heatmap(
        cm,
        annot=True,
        fmt='d',
        cmap='Blues',
        xticklabels=labels,
        yticklabels=labels
    )
    plt.title('Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    return plt.gcf() 