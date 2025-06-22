#!/usr/bin/env python3
"""
Article Quality Evaluation Script

This script evaluates the quality of generated articles using both LLM-based 
and simple machine learning approaches, including comparison with original articles.

Usage:
    python evaluate/evaluate.py --date "2025-06-14"
"""

import os
import json
import argparse
import glob
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Tuple
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import re
from collections import Counter
from textstat import flesch_reading_ease, flesch_kincaid_grade, coleman_liau_index
import warnings
warnings.filterwarnings('ignore')

import sys

# Add parent directory to path to import llm_client
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from llm_client import alibaba_client

# Import prompt functions using relative import
import importlib.util
spec = importlib.util.spec_from_file_location("prompt", Path(__file__).parent / "prompt.py")
prompt_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prompt_module)

SYSTEM_PROMPT = prompt_module.SYSTEM_PROMPT
EVALUATION_PROMPTS = prompt_module.EVALUATION_PROMPTS
get_evaluation_prompt = prompt_module.get_evaluation_prompt

class ArticleEvaluator:
    """Comprehensive article evaluation using LLM and ML approaches."""
    
    def __init__(self, date: str):
        self.date = date
        self.article_dir = Path(f"data/output/article/{date}")
        self.resource_dir = Path(f"data/output/resource/{date}")
        self.output_dir = Path(f"data/eval/{date}")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Evaluation criteria - now imported from prompt.py
        self.evaluation_prompts = EVALUATION_PROMPTS
    
    def load_articles(self) -> List[Dict[str, Any]]:
        """Load all article JSON files for the given date."""
        articles = []
        json_files = glob.glob(str(self.article_dir / "group_*.json"))
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    article = json.load(f)
                    article['file_name'] = os.path.basename(json_file)
                    article['group_id'] = os.path.basename(json_file).replace('group_', '').replace('.json', '')
                    articles.append(article)
            except Exception as e:
                print(f"Error loading {json_file}: {e}")
                
        return articles
    
    def load_original_articles(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load original articles from resource files for comparison."""
        original_articles = {}
        json_files = glob.glob(str(self.resource_dir / "group_*.json"))
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    resource_data = json.load(f)
                    group_id = os.path.basename(json_file).replace('group_', '').replace('.json', '')
                    
                    if 'articles' in resource_data:
                        original_articles[group_id] = resource_data['articles']
                        print(f"Loaded {len(resource_data['articles'])} original articles for group {group_id}")
                    else:
                        original_articles[group_id] = []
                        print(f"No articles found in {json_file}")
                        
            except Exception as e:
                print(f"Error loading original articles from {json_file}: {e}")
                group_id = os.path.basename(json_file).replace('group_', '').replace('.json', '')
                original_articles[group_id] = []
                
        return original_articles
    
    def extract_content(self, article: Dict[str, Any]) -> str:
        """Extract the main content from an article for evaluation."""
        content_parts = []
        
        # Add headline and subheadline
        if 'headline' in article:
            content_parts.append(f"Headline: {article['headline']}")
        if 'subheadline' in article:
            content_parts.append(f"Subheadline: {article['subheadline']}")
        
        # Add lead
        if 'lead' in article:
            content_parts.append(f"Lead: {article['lead']}")
        
        # Add body sections
        if 'body' in article and isinstance(article['body'], list):
            for section in article['body']:
                if isinstance(section, dict) and 'section' in section and 'content' in section:
                    content_parts.append(f"{section['section']}: {section['content']}")
        
        # Add conclusion
        if 'conclusion' in article:
            content_parts.append(f"Conclusion: {article['conclusion']}")
            
        return "\n\n".join(content_parts)
    
    def calculate_readability_metrics(self, text: str) -> Dict[str, float]:
        """Calculate readability metrics for the text."""
        try:
            return {
                'flesch_reading_ease': flesch_reading_ease(text),
                'flesch_kincaid_grade': flesch_kincaid_grade(text),
                'coleman_liau_index': coleman_liau_index(text)
            }
        except:
            return {
                'flesch_reading_ease': 0.0,
                'flesch_kincaid_grade': 0.0,
                'coleman_liau_index': 0.0
            }
    
    def calculate_text_metrics(self, text: str) -> Dict[str, Any]:
        """Calculate basic text metrics."""
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        paragraphs = text.split('\n\n')
        
        return {
            'word_count': len(words),
            'sentence_count': len([s for s in sentences if s.strip()]),
            'paragraph_count': len([p for p in paragraphs if p.strip()]),
            'avg_word_length': np.mean([len(word) for word in words]) if words else 0,
            'avg_sentence_length': len(words) / len([s for s in sentences if s.strip()]) if sentences else 0
        }
    
    def analyze_sentiment_consistency(self, article: Dict[str, Any]) -> Dict[str, float]:
        """Analyze sentiment consistency across different parts of the article."""
        sentiments = []
        
        # Extract sentiment scores from body sections
        if 'body' in article and isinstance(article['body'], list):
            for section in article['body']:
                if isinstance(section, dict):
                    if 'sentisement_from_the_content' in section:
                        try:
                            sentiments.append(float(section['sentisement_from_the_content']))
                        except:
                            pass
                    if 'sentisement_from_the_posts_or_comments' in section:
                        try:
                            sentiments.append(float(section['sentisement_from_the_posts_or_comments']))
                        except:
                            pass
        
        if sentiments:
            return {
                'sentiment_mean': np.mean(sentiments),
                'sentiment_std': np.std(sentiments),
                'sentiment_consistency': 1 / (1 + np.std(sentiments))  # Higher consistency = lower std
            }
        else:
            return {
                'sentiment_mean': 0.0,
                'sentiment_std': 0.0,
                'sentiment_consistency': 1.0
            }
    
    def analyze_fake_news_probability(self, article: Dict[str, Any]) -> Dict[str, float]:
        """Analyze fake news probability metrics."""
        fake_probs = []
        
        if 'body' in article and isinstance(article['body'], list):
            for section in article['body']:
                if isinstance(section, dict) and 'fake_news_probability' in section:
                    try:
                        fake_probs.append(float(section['fake_news_probability']))
                    except:
                        pass
        
        if fake_probs:
            return {
                'avg_fake_news_prob': np.mean(fake_probs),
                'max_fake_news_prob': np.max(fake_probs),
                'fake_news_consistency': 1 / (1 + np.std(fake_probs))
            }
        else:
            return {
                'avg_fake_news_prob': 0.0,
                'max_fake_news_prob': 0.0,
                'fake_news_consistency': 1.0
            }
    
    def llm_evaluate_article(self, content: str, article_meta: Dict[str, Any]) -> Dict[str, float]:
        """Use LLM to evaluate article quality across multiple dimensions."""
        evaluations = {}
        
        for criterion, prompt in self.evaluation_prompts.items():
            try:
                full_prompt = get_evaluation_prompt(criterion, content)
                
                response = alibaba_client.generate(
                    prompt_content=full_prompt,
                    system_content=SYSTEM_PROMPT,
                    temperature=0.1,
                    model='qwen-max-latest'
                )
                
                # Extract numeric score from response
                score_text = response.choices[0].message.content.strip()
                score = float(re.search(r'\d+(?:\.\d+)?', score_text).group())
                evaluations[f'llm_{criterion}'] = min(10.0, max(1.0, score))
                
            except Exception as e:
                print(f"Error in LLM evaluation for {criterion}: {e}")
                evaluations[f'llm_{criterion}'] = 5.0  # Default neutral score
        
        return evaluations
    
    def calculate_diversity_metrics(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate diversity metrics for publishers and regions."""
        publishers = set()
        regions = set()
        
        if 'body' in article and isinstance(article['body'], list):
            for section in article['body']:
                if isinstance(section, dict):
                    if 'Publishers' in section and isinstance(section['Publishers'], list):
                        publishers.update(section['Publishers'])
                    if 'Publisher_region_diversity' in section and isinstance(section['Publisher_region_diversity'], list):
                        regions.update(section['Publisher_region_diversity'])
        
        return {
            'publisher_diversity': len(publishers),
            'region_diversity': len(regions),
            'total_diversity_score': len(publishers) + len(regions)
        }
    
    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity using basic metrics."""
        # Simple word overlap similarity
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
            
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def calculate_content_similarity(self, generated_content: str, original_articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate similarity between generated content and original articles."""
        if not original_articles:
            return {
                'max_similarity': 0.0,
                'avg_similarity': 0.0,
                'similarity_std': 0.0,
                'count_original_articles': 0
            }
        
        similarities = []
        for article in original_articles:
            if 'content' in article and article['content']:
                similarity = self.calculate_text_similarity(generated_content, article['content'])
                similarities.append(similarity)
        
        if similarities:
            return {
                'max_similarity': max(similarities),
                'avg_similarity': np.mean(similarities),
                'similarity_std': np.std(similarities),
                'count_original_articles': len(original_articles)
            }
        else:
            return {
                'max_similarity': 0.0,
                'avg_similarity': 0.0,
                'similarity_std': 0.0,
                'count_original_articles': len(original_articles)
            }
    
    def evaluate_original_articles(self, original_articles: List[Dict[str, Any]]) -> Dict[str, float]:
        """Evaluate original articles using the same LLM criteria."""
        if not original_articles:
            return {}
        
        all_scores = {criterion: [] for criterion in self.evaluation_prompts.keys()}
        
        for article in original_articles:
            if 'content' in article and article['content']:
                content = f"Title: {article.get('title', '')}\n\nContent: {article['content']}"
                
                for criterion in self.evaluation_prompts.keys():
                    try:
                        full_prompt = get_evaluation_prompt(criterion, content)
                        
                        response = alibaba_client.generate(
                            prompt_content=full_prompt,
                            system_content=SYSTEM_PROMPT,
                            temperature=0.1,
                            model='qwen-max-latest'
                        )
                        
                        # Extract numeric score from response
                        score_text = response.choices[0].message.content.strip()
                        score = float(re.search(r'\d+(?:\.\d+)?', score_text).group())
                        all_scores[criterion].append(min(10.0, max(1.0, score)))
                        
                    except Exception as e:
                        print(f"Error in LLM evaluation of original article for {criterion}: {e}")
                        all_scores[criterion].append(5.0)  # Default neutral score
        
        # Calculate average scores for each criterion
        avg_scores = {}
        for criterion, scores in all_scores.items():
            if scores:
                avg_scores[f'original_avg_{criterion}'] = np.mean(scores)
            else:
                avg_scores[f'original_avg_{criterion}'] = 5.0
        
        # Calculate overall original score
        original_scores = [v for k, v in avg_scores.items() if k.startswith('original_avg_')]
        avg_scores['original_overall_score'] = np.mean(original_scores) if original_scores else 5.0
        
        return avg_scores
    
    def evaluate_single_article(self, article: Dict[str, Any], original_articles: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Evaluate a single article using all available methods."""
        print(f"Evaluating article: {article.get('file_name', 'Unknown')}")
        
        content = self.extract_content(article)
        
        # Initialize evaluation results
        evaluation = {
            'group_id': article.get('group_id', ''),
            'file_name': article.get('file_name', ''),
            'category': article.get('category', ''),
            'headline': article.get('headline', ''),
        }
        
        # Text metrics
        evaluation.update(self.calculate_text_metrics(content))
        
        # Readability metrics
        evaluation.update(self.calculate_readability_metrics(content))
        
        # Sentiment analysis
        evaluation.update(self.analyze_sentiment_consistency(article))
        
        # Fake news probability
        evaluation.update(self.analyze_fake_news_probability(article))
        
        # Diversity metrics
        evaluation.update(self.calculate_diversity_metrics(article))
        
        # LLM evaluation
        evaluation.update(self.llm_evaluate_article(content, article))
        
        # Calculate overall quality score
        llm_scores = [v for k, v in evaluation.items() if k.startswith('llm_')]
        evaluation['llm_overall_score'] = np.mean(llm_scores) if llm_scores else 5.0
        
        # Simple ML-based quality score
        ml_score = self.calculate_ml_quality_score(evaluation)
        evaluation['ml_quality_score'] = ml_score
        
        # Combined quality score
        evaluation['combined_quality_score'] = (evaluation['llm_overall_score'] + ml_score) / 2
        
        # Content similarity with original articles
        if original_articles:
            similarity_metrics = self.calculate_content_similarity(content, original_articles)
            evaluation.update(similarity_metrics)
            
            # Evaluate original articles
            original_scores = self.evaluate_original_articles(original_articles)
            evaluation.update(original_scores)
            
            # Calculate quality improvement/difference
            if 'original_overall_score' in original_scores:
                evaluation['quality_difference'] = evaluation['llm_overall_score'] - original_scores['original_overall_score']
                evaluation['quality_improvement_ratio'] = evaluation['llm_overall_score'] / original_scores['original_overall_score'] if original_scores['original_overall_score'] > 0 else 1.0
        else:
            # Default values when no original articles
            evaluation.update({
                'max_similarity': 0.0,
                'avg_similarity': 0.0,
                'similarity_std': 0.0,
                'count_original_articles': 0,
                'original_overall_score': 5.0,
                'quality_difference': 0.0,
                'quality_improvement_ratio': 1.0
            })
        
        return evaluation
    
    def calculate_ml_quality_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate a quality score using simple ML/heuristic approach."""
        score = 5.0  # Base score
        
        # Word count factor (optimal range: 800-2000 words)
        word_count = metrics.get('word_count', 0)
        if 800 <= word_count <= 2000:
            score += 1.0
        elif word_count < 400:
            score -= 1.5
        elif word_count > 3000:
            score -= 0.5
        
        # Readability factor
        flesch_score = metrics.get('flesch_reading_ease', 50)
        if 30 <= flesch_score <= 70:  # Good readability range
            score += 1.0
        elif flesch_score < 10 or flesch_score > 90:
            score -= 1.0
        
        # Fake news probability factor
        fake_prob = metrics.get('avg_fake_news_prob', 0.5)
        if fake_prob < 0.3:
            score += 1.0
        elif fake_prob > 0.7:
            score -= 2.0
        
        # Sentiment consistency factor
        sent_consistency = metrics.get('sentiment_consistency', 0.5)
        if sent_consistency > 0.7:
            score += 0.5
        elif sent_consistency < 0.3:
            score -= 0.5
        
        # Diversity factor
        diversity = metrics.get('total_diversity_score', 0)
        if diversity >= 4:
            score += 0.5
        elif diversity < 2:
            score -= 0.5
        
        # Content similarity factor (bonus for moderate similarity, penalty for too high/low)
        avg_similarity = metrics.get('avg_similarity', 0.0)
        if 0.1 <= avg_similarity <= 0.4:  # Good balance of similarity
            score += 0.5
        elif avg_similarity > 0.7:  # Too similar (potential plagiarism)
            score -= 1.0
        elif avg_similarity < 0.05:  # Too different (may not be relevant)
            score -= 0.5
        
        # Quality improvement factor
        quality_diff = metrics.get('quality_difference', 0.0)
        if quality_diff > 1.0:  # Significant improvement
            score += 1.0
        elif quality_diff < -1.0:  # Significant degradation
            score -= 1.0
        
        return max(1.0, min(10.0, score))
    
    def create_visualizations(self, df: pd.DataFrame):
        """Create visualization charts for the evaluation results."""
        plt.style.use('seaborn-v0_8')
        fig, axes = plt.subplots(3, 3, figsize=(20, 15))
        fig.suptitle(f'Article Quality Evaluation - {self.date}', fontsize=16)
        
        # 1. Overall Quality Scores Distribution
        axes[0, 0].hist([df['llm_overall_score'], df['ml_quality_score'], df['combined_quality_score']], 
                       bins=10, alpha=0.7, label=['LLM Score', 'ML Score', 'Combined Score'])
        axes[0, 0].set_title('Quality Scores Distribution')
        axes[0, 0].set_xlabel('Score')
        axes[0, 0].set_ylabel('Frequency')
        axes[0, 0].legend()
        
        # 2. Category vs Quality
        if 'category' in df.columns:
            category_scores = df.groupby('category')['combined_quality_score'].mean()
            axes[0, 1].bar(category_scores.index, category_scores.values)
            axes[0, 1].set_title('Average Quality by Category')
            axes[0, 1].set_xlabel('Category')
            axes[0, 1].set_ylabel('Average Quality Score')
            plt.setp(axes[0, 1].get_xticklabels(), rotation=45)
        
        # 3. Word Count vs Quality
        axes[0, 2].scatter(df['word_count'], df['combined_quality_score'], alpha=0.7)
        axes[0, 2].set_title('Word Count vs Quality Score')
        axes[0, 2].set_xlabel('Word Count')
        axes[0, 2].set_ylabel('Quality Score')
        
        # 4. Readability vs Quality
        axes[1, 0].scatter(df['flesch_reading_ease'], df['combined_quality_score'], alpha=0.7)
        axes[1, 0].set_title('Readability vs Quality Score')
        axes[1, 0].set_xlabel('Flesch Reading Ease')
        axes[1, 0].set_ylabel('Quality Score')
        
        # 5. Fake News Probability Distribution
        axes[1, 1].hist(df['avg_fake_news_prob'], bins=15, alpha=0.7, color='red')
        axes[1, 1].set_title('Fake News Probability Distribution')
        axes[1, 1].set_xlabel('Average Fake News Probability')
        axes[1, 1].set_ylabel('Frequency')
        
        # 6. LLM Criteria Scores
        llm_columns = [col for col in df.columns if col.startswith('llm_') and col != 'llm_overall_score']
        if llm_columns:
            llm_means = df[llm_columns].mean()
            axes[1, 2].bar(range(len(llm_means)), llm_means.values)
            axes[1, 2].set_title('Average LLM Evaluation Scores')
            axes[1, 2].set_xlabel('Evaluation Criteria')
            axes[1, 2].set_ylabel('Average Score')
            axes[1, 2].set_xticks(range(len(llm_means)))
            axes[1, 2].set_xticklabels([col.replace('llm_', '') for col in llm_columns], rotation=45)
        
        # 7. Content Similarity Distribution
        if 'avg_similarity' in df.columns:
            axes[2, 0].hist(df['avg_similarity'], bins=15, alpha=0.7, color='green')
            axes[2, 0].set_title('Content Similarity Distribution')
            axes[2, 0].set_xlabel('Average Similarity Score')
            axes[2, 0].set_ylabel('Frequency')
        
        # 8. Generated vs Original Quality Comparison
        if 'original_overall_score' in df.columns:
            axes[2, 1].scatter(df['original_overall_score'], df['llm_overall_score'], alpha=0.7)
            axes[2, 1].plot([1, 10], [1, 10], 'r--', alpha=0.5)  # Diagonal line
            axes[2, 1].set_title('Generated vs Original Quality')
            axes[2, 1].set_xlabel('Original Article Quality Score')
            axes[2, 1].set_ylabel('Generated Article Quality Score')
        
        # 9. Quality Improvement Distribution
        if 'quality_difference' in df.columns:
            axes[2, 2].hist(df['quality_difference'], bins=15, alpha=0.7, color='blue')
            axes[2, 2].axvline(x=0, color='red', linestyle='--', alpha=0.7)
            axes[2, 2].set_title('Quality Improvement Distribution')
        axes[2, 2].set_xlabel('Quality Difference (Generated - Original)')
        axes[2, 2].set_ylabel('Frequency')
        
        plt.tight_layout()
        chart_path = self.output_dir / f'evaluation_charts_{self.date}.png'
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Charts saved to: {chart_path}")
    
    def run_evaluation(self):
        """Run the complete evaluation process."""
        print(f"Starting evaluation for date: {self.date}")
        
        # Load articles
        articles = self.load_articles()
        if not articles:
            print(f"No articles found for date {self.date}")
            return
        
        print(f"Found {len(articles)} articles to evaluate")
        
        # Load original articles
        original_articles = self.load_original_articles()
        
        # Evaluate each article
        evaluations = []
        for article in articles:
            try:
                evaluation = self.evaluate_single_article(article, original_articles.get(article['group_id'], []))
                evaluations.append(evaluation)
            except Exception as e:
                print(f"Error evaluating article {article.get('file_name', 'Unknown')}: {e}")
        
        # Create DataFrame and save results
        df = pd.DataFrame(evaluations)
        
        # Save CSV
        csv_path = self.output_dir / 'eval.csv'
        df.to_csv(csv_path, index=False)
        print(f"Evaluation results saved to: {csv_path}")
        
        # Create visualizations
        if len(df) > 0:
            self.create_visualizations(df)
            
            # Generate and save summary report
            summary_report = self.generate_summary_report(df)
            report_path = self.output_dir / f'evaluation_summary_{self.date}.txt'
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(summary_report)
            print(f"Summary report saved to: {report_path}")
            
            # Print summary to console
            print("\n" + "="*50)
            print("EVALUATION SUMMARY")
            print("="*50)
            print(summary_report)

        return df

    def generate_summary_report(self, df: pd.DataFrame) -> str:
        """Generate a comprehensive summary report of the evaluation results."""
        if df.empty:
            return "No evaluation data available."
        
        report_lines = []
        report_lines.append(f"=== Article Quality Evaluation Summary - {self.date} ===")
        report_lines.append(f"Total Articles Evaluated: {len(df)}")
        report_lines.append("")
        
        # LLM Evaluation Summary
        report_lines.append("--- LLM Evaluation Scores ---")
        llm_columns = [col for col in df.columns if col.startswith('llm_') and col != 'llm_overall_score']
        for col in llm_columns:
            criterion = col.replace('llm_', '')
            avg_score = df[col].mean()
            report_lines.append(f"{criterion.replace('_', ' ').title()}: {avg_score:.2f}/10")
        
        report_lines.append(f"Overall LLM Score: {df['llm_overall_score'].mean():.2f}/10")
        report_lines.append("")
        
        # ML Quality Score
        report_lines.append("--- ML-Based Quality Score ---")
        report_lines.append(f"Average ML Quality Score: {df['ml_quality_score'].mean():.2f}/10")
        report_lines.append(f"Combined Quality Score: {df['combined_quality_score'].mean():.2f}/10")
        report_lines.append("")
        
        # Original Article Comparison
        if 'original_overall_score' in df.columns:
            report_lines.append("--- Original Article Comparison ---")
            report_lines.append(f"Average Original Article Score: {df['original_overall_score'].mean():.2f}/10")
            report_lines.append(f"Average Quality Difference: {df['quality_difference'].mean():.2f}")
            report_lines.append(f"Quality Improvement Ratio: {df['quality_improvement_ratio'].mean():.2f}")
            report_lines.append("")
            
            # Original article scores by criterion
            original_columns = [col for col in df.columns if col.startswith('original_avg_')]
            if original_columns:
                report_lines.append("Original Article Scores by Criterion:")
                for col in original_columns:
                    criterion = col.replace('original_avg_', '')
                    avg_score = df[col].mean()
                    report_lines.append(f"  {criterion.replace('_', ' ').title()}: {avg_score:.2f}/10")
                report_lines.append("")
        
        # Content Similarity
        if 'avg_similarity' in df.columns:
            report_lines.append("--- Content Similarity Metrics ---")
            report_lines.append(f"Average Similarity: {df['avg_similarity'].mean():.3f}")
            report_lines.append(f"Max Similarity: {df['max_similarity'].mean():.3f}")
            report_lines.append(f"Similarity Standard Deviation: {df['similarity_std'].mean():.3f}")
            report_lines.append(f"Average Original Articles Count: {df['count_original_articles'].mean():.1f}")
            report_lines.append("")
        
        # Text Metrics Summary
        report_lines.append("--- Text Metrics Summary ---")
        report_lines.append(f"Average Word Count: {df['word_count'].mean():.0f}")
        report_lines.append(f"Average Readability Score: {df['flesch_reading_ease'].mean():.1f}")
        report_lines.append(f"Average Fake News Probability: {df['avg_fake_news_prob'].mean():.3f}")
        report_lines.append("")
        
        # Category Performance
        if 'category' in df.columns:
            report_lines.append("--- Performance by Category ---")
            category_performance = df.groupby('category')['combined_quality_score'].agg(['mean', 'count']).round(2)
            for category, row in category_performance.iterrows():
                report_lines.append(f"{category}: {row['mean']:.2f}/10 ({row['count']} articles)")
            report_lines.append("")
        
        # Top and Bottom Performers
        report_lines.append("--- Top 3 Articles by Combined Quality Score ---")
        top_articles = df.nlargest(3, 'combined_quality_score')[['headline', 'combined_quality_score', 'llm_overall_score']]
        for idx, row in top_articles.iterrows():
            report_lines.append(f"• {row['headline'][:60]}... (Score: {row['combined_quality_score']:.2f})")
        
        report_lines.append("")
        report_lines.append("--- Bottom 3 Articles by Combined Quality Score ---")
        bottom_articles = df.nsmallest(3, 'combined_quality_score')[['headline', 'combined_quality_score', 'llm_overall_score']]
        for idx, row in bottom_articles.iterrows():
            report_lines.append(f"• {row['headline'][:60]}... (Score: {row['combined_quality_score']:.2f})")
        
        return "\n".join(report_lines)


def main():
    parser = argparse.ArgumentParser(description='Evaluate article quality using LLM and ML approaches')
    parser.add_argument('--date', required=True, help='Date in YYYY-MM-DD format (e.g., 2025-06-14)')
    
    args = parser.parse_args()
    
    # Validate date format
    try:
        datetime.strptime(args.date, '%Y-%m-%d')
    except ValueError:
        print("Error: Date must be in YYYY-MM-DD format")
        return
    
    # Run evaluation
    evaluator = ArticleEvaluator(args.date)
    evaluator.run_evaluation()


if __name__ == "__main__":
    main()
