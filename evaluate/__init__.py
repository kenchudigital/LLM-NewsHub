"""
Evaluation module for LLM-NewsHub

This module provides comprehensive evaluation tools for generated articles,
including single article evaluation and multi-model comparison.
"""

from .evaluate import ArticleEvaluator
from .evaluate_compare import ModelComparisonEvaluator

__all__ = ['ArticleEvaluator', 'ModelComparisonEvaluator'] 