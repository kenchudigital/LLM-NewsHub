import matplotlib.pyplot as plt
from sklearn.tree import plot_tree, export_text, DecisionTreeClassifier
from sklearn.metrics import accuracy_score
import numpy as np
from pathlib import Path
from typing import Tuple, Dict, Any
import graphviz
from sklearn import tree

def find_optimal_pruning(X_train: np.ndarray, y_train: np.ndarray, 
                        X_val: np.ndarray, y_val: np.ndarray,
                        max_depth: int = 5) -> Tuple[DecisionTreeClassifier, float]:
    """
    Find the optimal pruning parameters for the decision tree
    """
    best_accuracy = 0
    best_tree = None
    best_ccp_alpha = 0
    
    # Try different pruning parameters
    for ccp_alpha in np.arange(0.0, 0.1, 0.01):
        tree_model = DecisionTreeClassifier(
            max_depth=max_depth,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            ccp_alpha=ccp_alpha
        )
        tree_model.fit(X_train, y_train)
        
        # Evaluate on validation set
        val_pred = tree_model.predict(X_val)
        accuracy = accuracy_score(y_val, val_pred)
        
        if accuracy > best_accuracy:
            best_accuracy = accuracy
            best_tree = tree_model
            best_ccp_alpha = ccp_alpha
    
    return best_tree, best_ccp_alpha

def visualize_tree(tree_model: DecisionTreeClassifier, 
                  feature_names: list,
                  output_dir: Path,
                  max_depth: int = 3) -> Dict[str, Any]:
    """
    Generate and save tree visualizations
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    tree_text = export_text(
        tree_model,
        feature_names=feature_names,
        max_depth=max_depth,
        show_weights=True
    )
    
    with open(output_dir / 'tree_rules.txt', 'w') as f:
        f.write(tree_text)

    dot_data = tree.export_graphviz(
        tree_model,
        feature_names=feature_names,
        class_names=['Real', 'Fake'],
        filled=True,
        rounded=True,
        max_depth=max_depth,
        special_characters=True
    )
    graph = graphviz.Source(dot_data)
    graph.render(output_dir / 'tree_detailed', format='png', cleanup=True)
    
    tree_stats = {
        'n_nodes': tree_model.tree_.node_count,
        'n_leaves': tree_model.tree_.n_leaves,
        'max_depth': tree_model.tree_.max_depth,
        'ccp_alpha': tree_model.ccp_alpha,
        'feature_importance': dict(zip(feature_names, tree_model.feature_importances_))
    }
    
    return tree_stats
