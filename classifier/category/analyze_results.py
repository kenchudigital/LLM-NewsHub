# classifier/category/analyze_results.py

import os
import sys
from pathlib import Path
import argparse
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix
import matplotlib.gridspec as gridspec

def create_parameter_correlation_plot(results_df: pd.DataFrame, analysis_dir: Path, model_type: str):
    """Create correlation heatmap for numerical parameters and accuracy"""
    # Filter for specific model type
    model_df = results_df[results_df['model_type'] == model_type].copy()
    
    # Get numerical parameters
    param_cols = [col for col in model_df.columns if col.startswith('param_') and 
                 pd.api.types.is_numeric_dtype(model_df[col])]
    if not param_cols:
        return
    
    # Add accuracy and cv_mean
    analysis_cols = param_cols + ['accuracy', 'cv_mean']
    corr_matrix = model_df[analysis_cols].corr()
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, cmap='RdYlBu', center=0, fmt='.2f')
    plt.title(f'{model_type} Parameter Correlation Matrix')
    plt.tight_layout()
    plt.savefig(analysis_dir / f'parameter_correlation_{model_type.lower()}.png')
    plt.close()

def create_parameter_impact_plot(results_df: pd.DataFrame, analysis_dir: Path, model_type: str):
    """Create parameter impact visualization"""
    model_df = results_df[results_df['model_type'] == model_type].copy()
    param_cols = [col for col in model_df.columns if col.startswith('param_')]
    
    if not param_cols:
        return
        
    # Create a figure with subplots for each parameter
    n_params = len(param_cols)
    n_cols = 2
    n_rows = (n_params + 1) // 2  # Ceiling division
    
    fig = plt.figure(figsize=(15, 5 * n_rows))
    
    for idx, param in enumerate(param_cols):
        ax = plt.subplot(n_rows, n_cols, idx + 1)
        param_name = param.replace('param_', '')
        
        try:
            if pd.api.types.is_numeric_dtype(model_df[param]):
                # For numerical parameters
                sns.scatterplot(data=model_df, x=param, y='accuracy', ax=ax)
                
                # Add trend line
                z = np.polyfit(model_df[param], model_df['accuracy'], 1)
                p = np.poly1d(z)
                x_range = np.linspace(model_df[param].min(), model_df[param].max(), 100)
                ax.plot(x_range, p(x_range), "r--", alpha=0.8)
                
                # Add correlation coefficient
                corr = model_df[[param, 'accuracy']].corr().iloc[0, 1]
                ax.text(0.05, 0.95, f'Correlation: {corr:.2f}', 
                       transform=ax.transAxes, 
                       verticalalignment='top')
            else:
                # For categorical parameters
                # Calculate mean accuracy for each category
                mean_acc = model_df.groupby(param)['accuracy'].agg(['mean', 'std']).reset_index()
                
                # Create bar plot
                sns.barplot(data=mean_acc, x=param, y='mean', ax=ax)
                
                # Add error bars
                ax.errorbar(x=range(len(mean_acc)), 
                          y=mean_acc['mean'],
                          yerr=mean_acc['std'],
                          fmt='none',
                          color='black',
                          capsize=5)
                
                # Add value counts
                value_counts = model_df[param].value_counts()
                ax.text(0.05, 0.95, 
                       f'Sample sizes:\n' + '\n'.join([f'{k}: {v}' for k, v in value_counts.items()]),
                       transform=ax.transAxes,
                       verticalalignment='top',
                       fontsize=8)
            
            ax.set_title(f'Impact of {param_name} on Accuracy')
            ax.set_xlabel(param_name)
            ax.set_ylabel('Accuracy')
            
            if not pd.api.types.is_numeric_dtype(model_df[param]):
                plt.xticks(rotation=45)
                
        except Exception as e:
            print(f"Warning: Could not create plot for parameter {param_name}: {str(e)}")
            continue
    
    plt.tight_layout()
    plt.savefig(analysis_dir / f'parameter_impact_{model_type.lower()}.png')
    plt.close()

def create_performance_distribution_plot(results_df: pd.DataFrame, analysis_dir: Path):
    """Create advanced performance distribution visualization"""
    plt.figure(figsize=(12, 6))
    
    # Create violin plots with embedded box plots
    sns.violinplot(data=results_df, x='model_type', y='accuracy', inner='box', cut=0)
    
    # Add individual points
    sns.stripplot(data=results_df, x='model_type', y='accuracy', color='red', alpha=0.3, jitter=0.2, size=4)
    
    # Add statistics annotations
    for i, model in enumerate(results_df['model_type'].unique()):
        model_data = results_df[results_df['model_type'] == model]['accuracy']
        stats = {
            'μ': model_data.mean(),
            'σ': model_data.std(),
            'max': model_data.max(),
            'min': model_data.min()
        }
        stats_text = '\n'.join([f'{k}: {v:.3f}' for k, v in stats.items()])
        plt.text(i, results_df['accuracy'].min(), stats_text,
                horizontalalignment='center', verticalalignment='top')
    
    plt.title('Model Performance Distribution')
    plt.xlabel('Model Type')
    plt.ylabel('Accuracy')
    plt.tight_layout()
    plt.savefig(analysis_dir / 'performance_distribution.png')
    plt.close()

def create_cv_stability_plot(results_df: pd.DataFrame, analysis_dir: Path):
    """Create cross-validation stability plot"""
    plt.figure(figsize=(12, 6))
    
    # Calculate CV vs Validation difference
    results_df['cv_val_diff'] = results_df['cv_mean'] - results_df['accuracy']
    
    # Create scatter plot
    for model in results_df['model_type'].unique():
        model_data = results_df[results_df['model_type'] == model]
        plt.scatter(model_data['accuracy'], model_data['cv_mean'], 
                   alpha=0.6, label=model)
    
    # Add diagonal line
    min_val = min(results_df['accuracy'].min(), results_df['cv_mean'].min())
    max_val = max(results_df['accuracy'].max(), results_df['cv_mean'].max())
    plt.plot([min_val, max_val], [min_val, max_val], 'k--', alpha=0.5)
    
    plt.title('Cross-validation vs Validation Stability')
    plt.xlabel('Validation Accuracy')
    plt.ylabel('Cross-validation Mean Accuracy')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(analysis_dir / 'cv_stability.png')
    plt.close()

def analyze_results(results_dir: str):
    """Analyze and visualize model results with advanced insights"""
    results_path = Path(results_dir)
    
    # Load experiments from results.json
    experiments_file = Path("classifier/category/experiments/results.json")
    if not experiments_file.exists():
        print(f"Warning: No results file found at {experiments_file}")
        return {}
        
    with open(experiments_file, 'r') as f:
        data = json.load(f)
        experiments = data.get('experiments', [])
    
    # Convert experiments to DataFrame
    results_list = []
    for exp in experiments:
        result = {
            'model_type': exp['model_type'],
            'accuracy': exp['metrics']['accuracy'],
            'cv_mean': exp['metrics']['cv_mean'],
            'cv_std': exp['metrics']['cv_std']
        }
        # Add model parameters
        for param, value in exp['model_params'].items():
            result[f'param_{param}'] = value
        results_list.append(result)
    
    if not results_list:
        print("Warning: No experiments found in results file")
        return {}
        
    results_df = pd.DataFrame(results_list)
    
    # Create analysis directory
    analysis_dir = results_path / "analysis"
    analysis_dir.mkdir(exist_ok=True)
    
    # Create visualizations
    print("\n📊 Creating analysis visualizations...")
    
    try:
        print("  - Creating performance distribution plot...")
        create_performance_distribution_plot(results_df, analysis_dir)
    except Exception as e:
        print(f"Warning: Could not create performance distribution plot: {str(e)}")
    
    try:
        print("  - Creating CV stability plot...")
        create_cv_stability_plot(results_df, analysis_dir)
    except Exception as e:
        print(f"Warning: Could not create CV stability plot: {str(e)}")
    
    # Parameter analysis for each model type
    for model_type in results_df['model_type'].unique():
        try:
            print(f"  - Creating parameter impact plots for {model_type}...")
            create_parameter_impact_plot(results_df, analysis_dir, model_type)
        except Exception as e:
            print(f"Warning: Could not create parameter impact plots for {model_type}: {str(e)}")
    
    # Generate summary statistics
    summary = {
        'models': {
            model_type: {
                'accuracy_stats': {
                    'mean': float(model_results['accuracy'].mean()),
                    'std': float(model_results['accuracy'].std()),
                    'min': float(model_results['accuracy'].min()),
                    'max': float(model_results['accuracy'].max()),
                    'median': float(model_results['accuracy'].median()),
                    'q1': float(model_results['accuracy'].quantile(0.25)),
                    'q3': float(model_results['accuracy'].quantile(0.75))
                },
                'cv_stats': {
                    'mean': float(model_results['cv_mean'].mean()),
                    'std': float(model_results['cv_std'].mean()),
                    'cv_stability': float(1 - abs(model_results['cv_mean'] - model_results['accuracy']).mean())
                },
                'n_experiments': len(model_results),
                'best_configuration': {
                    'accuracy': float(model_results['accuracy'].max()),
                    'parameters': {k.replace('param_', ''): v for k, v in 
                                 model_results.loc[model_results['accuracy'].idxmax()].items()
                                 if k.startswith('param_')}
                }
            }
            for model_type, model_results in results_df.groupby('model_type')
        }
    }
    
    # Save summary
    with open(analysis_dir / 'analysis_summary.json', 'w') as f:
        json.dump(summary, f, indent=4)
    
    return summary

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Analyze model results')
    parser.add_argument('--results', type=str, required=True,
                      help='Path to results directory')
    
    args = parser.parse_args()
    summary = analyze_results(args.results)