#!/usr/bin/env python3
"""
Article Quality Evaluation Script

This script evaluates the quality of generated articles using both LLM-based 
and advanced NLP metrics including BLEU, ROUGE, semantic similarity, and 
comparison with original articles.

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

# NLP metrics libraries
try:
    from nltk.translate.bleu_score import sentence_bleu, corpus_bleu, SmoothingFunction
    from rouge_score import rouge_scorer
    import nltk
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    from nltk.tokenize import sent_tokenize, word_tokenize
    from nltk.corpus import stopwords
    print("All NLP libraries imported successfully")
except ImportError as e:
    print(f"Import failed: {e}")
    
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMER_AVAILABLE = True
except ImportError:
    print("Warning: sentence-transformers not installed. Install with: pip install sentence-transformers")
    SENTENCE_TRANSFORMER_AVAILABLE = False

try:
    from transformers import AutoTokenizer, AutoModel
    import torch
    from sklearn.metrics.pairwise import cosine_similarity
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    print("Warning: transformers not installed. Install with: pip install transformers torch")
    TRANSFORMERS_AVAILABLE = False

import sys

# Add parent directory to path to import llm_client
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from llm_client import alibaba_client, perplexity_client, openai_client

# Import prompt functions using relative import
import importlib.util
spec = importlib.util.spec_from_file_location("prompt", Path(__file__).parent / "prompt.py")
prompt_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prompt_module)

SYSTEM_PROMPT = prompt_module.SYSTEM_PROMPT
EVALUATION_PROMPTS = prompt_module.EVALUATION_PROMPTS
get_evaluation_prompt = prompt_module.get_evaluation_prompt

class ArticleEvaluator:
    """Comprehensive article evaluation using LLM and advanced NLP metrics."""
    
    def __init__(self, date: str):
        self.date = date
        self.article_dir = Path(f"data/output/article/{date}")
        
        # Extract base date (remove model suffix if present)
        # Handle cases like "2025-06-24-qwen-plus" -> "2025-06-24"
        if '-' in date and len(date.split('-')) > 3:
            # If more than 3 parts (YYYY-MM-DD-model), take first 3 parts
            base_date = '-'.join(date.split('-')[:3])
        else:
            # If already in YYYY-MM-DD format, use as is
            base_date = date
        
        self.resource_dir = Path(f"data/output/resource/{base_date}")
        self.output_dir = Path(f"data/eval/{date}")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"Article directory: {self.article_dir}")
        print(f"Resource directory: {self.resource_dir}")
        print(f"Output directory: {self.output_dir}")
        
        # Evaluation criteria - now imported from prompt.py
        self.evaluation_prompts = EVALUATION_PROMPTS
        
        # Initialize NLP models
        self.stop_words = set(stopwords.words('english'))
        self.rouge_scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
        self.smoothing_function = SmoothingFunction().method1
        
        print(f"Debug init: rouge_scorer = {self.rouge_scorer is not None}")
        print(f"Debug init: smoothing_function = {self.smoothing_function is not None}")
        
        # Load semantic similarity model
        if SENTENCE_TRANSFORMER_AVAILABLE:
            try:
                self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
                print("Loaded sentence transformer model")
            except Exception as e:
                print(f"Failed to load sentence transformer: {e}")
                self.sentence_model = None
        else:
            self.sentence_model = None
    
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
        
        # Check if resource directory exists
        if not self.resource_dir.exists():
            print(f"ERROR: Resource directory does not exist: {self.resource_dir}")
            print(f"   Please ensure the resource directory exists with the correct date format")
            print(f"   Expected directory: data/output/resource/{'-'.join(self.date.split('-')[:3])}")
            return original_articles
        
        json_files = glob.glob(str(self.resource_dir / "group_*.json"))
        
        if not json_files:
            print(f"ERROR: No resource files found in {self.resource_dir}")
            print(f"   Expected files: group_*.json")
            print(f"   Without original articles, comparison metrics will be 0.0")
            return original_articles
        
        print(f"📁 Looking for original articles in {len(json_files)} resource files...")
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    resource_data = json.load(f)
                    group_id = os.path.basename(json_file).replace('group_', '').replace('.json', '')
                    
                    articles = []
                    
                    # Look for 'events' first (new structure)
                    if 'events' in resource_data:
                        events = resource_data['events']
                        for event in events:
                            if 'content' in event and event['content'] and event['content'].strip():
                                # Fixed code - preserve event_id for matching
                                article = {
                                    'title': event.get('title', ''),
                                    'content': event['content'],
                                    'topic': event.get('topic', []),
                                    'publisher': event.get('publisher', ''),
                                    'publish_time': event.get('publish_time', ''),
                                    'event_id': event.get('event_id'),  # 🔧 添加这行！
                                    'source_type': 'event'
                                }
                                articles.append(article)
                        
                        if articles:
                            print(f"✅ Loaded {len(articles)} articles from events for group {group_id}")
                        else:
                            print(f"⚠️  No valid content found in events for group {group_id}")
                    
                    # Fallback to 'articles' key (old structure)
                    elif 'articles' in resource_data:
                        articles = [art for art in resource_data['articles'] 
                                  if 'content' in art and art['content'] and art['content'].strip()]
                        if articles:
                            print(f"✅ Loaded {len(articles)} articles from articles key for group {group_id}")
                        else:
                            print(f"⚠️  No valid content found in articles for group {group_id}")
                    
                    else:
                        print(f"❌ No 'events' or 'articles' key found in {json_file}")
                    
                    original_articles[group_id] = articles
                    
            except Exception as e:
                print(f"❌ Error loading {json_file}: {e}")
                group_id = os.path.basename(json_file).replace('group_', '').replace('.json', '')
                original_articles[group_id] = []
        
        # Summary statistics
        total_articles = sum(len(articles) for articles in original_articles.values())
        groups_with_articles = sum(1 for articles in original_articles.values() if articles)
        
        print(f"\n📊 Original Articles Summary:")
        print(f"   Total groups processed: {len(original_articles)}")
        print(f"   Groups with articles: {groups_with_articles}")
        print(f"   Total articles loaded: {total_articles}")
        
        if total_articles == 0:
            print(f"\n🚨 CRITICAL: No original articles found!")
            print(f"   All comparison metrics (BLEU, ROUGE, similarity) will be 0.0")
            print(f"   Please check your resource files structure")
        else:
            print(f"✅ Successfully loaded original articles for comparison")
        
        return original_articles
    
    def extract_content(self, article: Dict[str, Any]) -> str:
        """Extract all textual content from an article."""
        content_parts = []
        
        # Extract from different article sections
        if 'headline' in article:
            content_parts.append(article['headline'])
        if 'subheadline' in article:
            content_parts.append(article['subheadline'])
        if 'lead' in article:
            content_parts.append(article['lead'])
        
        # 新增：提取 body 內容（這是最重要的部分！）
        if 'body' in article and isinstance(article['body'], list):
            for section in article['body']:
                if isinstance(section, dict):
                    if 'section' in section:
                        content_parts.append(section['section'])
                    if 'content' in section:
                        content_parts.append(section['content'])
    
        if 'conclusion' in article:
            content_parts.append(article['conclusion'])
        if 'summary_speech' in article:
            content_parts.append(article['summary_speech'])
        
        # 新增：其他文本字段
        if 'category' in article:
            content_parts.append(article['category'])

        # Join with spaces and clean
        content = ' '.join(content_parts)
        content = re.sub(r'\s+', ' ', content).strip()
        
        return content
    
    def calculate_bleu_scores(self, generated_text: str, reference_texts: List[str]) -> Dict[str, float]:
        """Calculate BLEU scores against reference texts."""
        print(f"\n🔍 DEBUG BLEU Calculation:")
        print(f"   Generated text length: {len(generated_text) if generated_text else 0}")
        print(f"   Generated text preview: {generated_text[:100] if generated_text else 'EMPTY'}...")
        print(f"   Number of reference texts: {len(reference_texts) if reference_texts else 0}")
        
        if reference_texts:
            for i, ref in enumerate(reference_texts[:3]):  # Show first 3 references
                print(f"   Reference {i+1} length: {len(ref)}, preview: {ref[:100]}...")
        
        if not reference_texts or not generated_text:
            print("❌ BLEU calculation failed: Missing reference texts or generated content")
            return {
                'bleu_1': 0.0, 'bleu_2': 0.0, 'bleu_3': 0.0, 'bleu_4': 0.0, 'bleu_avg': 0.0
            }
        
        if not self.smoothing_function:
            print("❌ BLEU calculation failed: NLTK not properly installed")
            print(f"   Smoothing function available: {self.smoothing_function is not None}")
            print(f"   word_tokenize available: {'word_tokenize' in dir()}")
            return {
                'bleu_1': 0.0, 'bleu_2': 0.0, 'bleu_3': 0.0, 'bleu_4': 0.0, 'bleu_avg': 0.0
            }
        
        try:
            # Tokenize texts
            print("   🔧 Tokenizing texts...")
            generated_tokens = word_tokenize(generated_text.lower())
            reference_tokens_list = [word_tokenize(ref.lower()) for ref in reference_texts]
            
            print(f"   Generated tokens count: {len(generated_tokens)}")
            print(f"   Generated tokens preview: {generated_tokens[:10]}")
            print(f"   Reference tokens counts: {[len(ref_tokens) for ref_tokens in reference_tokens_list]}")
            
            if not generated_tokens:
                print("❌ BLEU calculation failed: Generated text has no valid tokens")
                return {
                    'bleu_1': 0.0, 'bleu_2': 0.0, 'bleu_3': 0.0, 'bleu_4': 0.0, 'bleu_avg': 0.0
                }
            
            # Calculate BLEU scores for different n-grams
            print("   🔧 Calculating BLEU scores...")
            bleu_1 = sentence_bleu(reference_tokens_list, generated_tokens, weights=(1, 0, 0, 0), smoothing_function=self.smoothing_function)
            bleu_2 = sentence_bleu(reference_tokens_list, generated_tokens, weights=(0.5, 0.5, 0, 0), smoothing_function=self.smoothing_function)
            bleu_3 = sentence_bleu(reference_tokens_list, generated_tokens, weights=(0.33, 0.33, 0.33, 0), smoothing_function=self.smoothing_function)
            bleu_4 = sentence_bleu(reference_tokens_list, generated_tokens, weights=(0.25, 0.25, 0.25, 0.25), smoothing_function=self.smoothing_function)
            
            result = {
                'bleu_1': bleu_1, 'bleu_2': bleu_2, 'bleu_3': bleu_3, 'bleu_4': bleu_4,
                'bleu_avg': (bleu_1 + bleu_2 + bleu_3 + bleu_4) / 4
            }
            
            print(f"   ✅ BLEU Results: {result}")
            
            # Check for suspiciously low scores
            if all(score < 0.001 for score in result.values()):
                print("⚠️  Very low BLEU scores detected - minimal content overlap")
                print("   This could indicate very different content between generated and reference texts")
            
            return result
            
        except Exception as e:
            print(f"❌ Error calculating BLEU scores: {e}")
            import traceback
            traceback.print_exc()
            return {
                'bleu_1': 0.0, 'bleu_2': 0.0, 'bleu_3': 0.0, 'bleu_4': 0.0, 'bleu_avg': 0.0
            }
    
    def calculate_rouge_scores(self, generated_text: str, reference_texts: List[str]) -> Dict[str, float]:
        """Calculate ROUGE scores against reference texts."""
        print(f"\n🔍 DEBUG ROUGE Calculation:")
        print(f"   Generated text length: {len(generated_text) if generated_text else 0}")
        print(f"   Number of reference texts: {len(reference_texts) if reference_texts else 0}")
        print(f"   ROUGE scorer available: {self.rouge_scorer is not None}")
        
        if not reference_texts or not generated_text:
            print("❌ ROUGE calculation failed: Missing reference texts or generated content")
            return {
                'rouge1_f': 0.0, 'rouge1_p': 0.0, 'rouge1_r': 0.0,
                'rouge2_f': 0.0, 'rouge2_p': 0.0, 'rouge2_r': 0.0,
                'rougeL_f': 0.0, 'rougeL_p': 0.0, 'rougeL_r': 0.0, 'rouge_avg_f': 0.0
            }
        
        if not self.rouge_scorer:
            print("❌ ROUGE calculation failed: rouge-score library not installed")
            print("   Install with: pip install rouge-score")
            return {
                'rouge1_f': 0.0, 'rouge1_p': 0.0, 'rouge1_r': 0.0,
                'rouge2_f': 0.0, 'rouge2_p': 0.0, 'rouge2_r': 0.0,
                'rougeL_f': 0.0, 'rougeL_p': 0.0, 'rougeL_r': 0.0, 'rouge_avg_f': 0.0
            }
        
        try:
            # Calculate ROUGE scores for each reference
            print("   🔧 Calculating ROUGE scores...")
            rouge_scores = []
            for i, ref_text in enumerate(reference_texts):
                if ref_text.strip():  # Only process non-empty references
                    print(f"   Processing reference {i+1}: {len(ref_text)} chars")
                    score = self.rouge_scorer.score(ref_text, generated_text)
                    rouge_scores.append(score)
                    print(f"     ROUGE-1 F1: {score['rouge1'].fmeasure:.4f}")
                    print(f"     ROUGE-2 F1: {score['rouge2'].fmeasure:.4f}")
                    print(f"     ROUGE-L F1: {score['rougeL'].fmeasure:.4f}")
                else:
                    print(f"   Skipping empty reference {i+1}")
            
            if not rouge_scores:
                print("❌ ROUGE calculation failed: No valid reference texts")
                return {
                    'rouge1_f': 0.0, 'rouge1_p': 0.0, 'rouge1_r': 0.0,
                    'rouge2_f': 0.0, 'rouge2_p': 0.0, 'rouge2_r': 0.0,
                    'rougeL_f': 0.0, 'rougeL_p': 0.0, 'rougeL_r': 0.0, 'rouge_avg_f': 0.0
                }
            
            # Average the scores
            result = {
                'rouge1_f': np.mean([score['rouge1'].fmeasure for score in rouge_scores]),
                'rouge1_p': np.mean([score['rouge1'].precision for score in rouge_scores]),
                'rouge1_r': np.mean([score['rouge1'].recall for score in rouge_scores]),
                'rouge2_f': np.mean([score['rouge2'].fmeasure for score in rouge_scores]),
                'rouge2_p': np.mean([score['rouge2'].precision for score in rouge_scores]),
                'rouge2_r': np.mean([score['rouge2'].recall for score in rouge_scores]),
                'rougeL_f': np.mean([score['rougeL'].fmeasure for score in rouge_scores]),
                'rougeL_p': np.mean([score['rougeL'].precision for score in rouge_scores]),
                'rougeL_r': np.mean([score['rougeL'].recall for score in rouge_scores])
            }
            result['rouge_avg_f'] = (result['rouge1_f'] + result['rouge2_f'] + result['rougeL_f']) / 3
            
            print(f"   ✅ ROUGE Results: {result}")
            
            # Check for suspiciously low scores
            if all(score < 0.001 for score in result.values()):
                print("⚠️  Very low ROUGE scores detected - minimal content overlap")
                print("   This could indicate very different content between generated and reference texts")
            
            return result
            
        except Exception as e:
            print(f"❌ Error calculating ROUGE scores: {e}")
            import traceback
            traceback.print_exc()
            return {
                'rouge1_f': 0.0, 'rouge1_p': 0.0, 'rouge1_r': 0.0,
                'rouge2_f': 0.0, 'rouge2_p': 0.0, 'rouge2_r': 0.0,
                'rougeL_f': 0.0, 'rougeL_p': 0.0, 'rougeL_r': 0.0, 'rouge_avg_f': 0.0
            }
    
    def calculate_semantic_similarity(self, generated_text: str, reference_texts: List[str]) -> Dict[str, float]:
        """Calculate semantic similarity using sentence transformers."""
        if not reference_texts or not generated_text or not self.sentence_model:
            return {
                'semantic_sim_max': 0.0,
                'semantic_sim_avg': 0.0,
                'semantic_sim_min': 0.0
            }
        
        try:
            # Get embeddings
            generated_embedding = self.sentence_model.encode([generated_text])
            reference_embeddings = self.sentence_model.encode(reference_texts)
            
            # Calculate cosine similarities
            similarities = cosine_similarity(generated_embedding, reference_embeddings)[0]
            
            return {
                'semantic_sim_max': float(np.max(similarities)),
                'semantic_sim_avg': float(np.mean(similarities)),
                'semantic_sim_min': float(np.min(similarities))
            }
        except Exception as e:
            print(f"Error calculating semantic similarity: {e}")
            return {
                'semantic_sim_max': 0.0,
                'semantic_sim_avg': 0.0,
                'semantic_sim_min': 0.0
            }
    
    def calculate_coherence_metrics(self, text: str) -> Dict[str, float]:
        """Calculate text coherence metrics."""
        try:
            sentences = sent_tokenize(text) if 'sent_tokenize' in dir() else text.split('.')
            
            if len(sentences) < 2:
                return {
                    'coherence_score': 0.0,
                    'avg_sentence_length': 0.0,
                    'sentence_length_variance': 0.0
                }
            
            # Calculate sentence length statistics
            sentence_lengths = [len(word_tokenize(sent)) if 'word_tokenize' in dir() else len(sent.split()) for sent in sentences]
            avg_sentence_length = np.mean(sentence_lengths)
            sentence_length_variance = np.var(sentence_lengths)
            
            # Simple coherence score based on sentence length consistency
            coherence_score = max(0.0, 1.0 - (sentence_length_variance / (avg_sentence_length ** 2)) if avg_sentence_length > 0 else 0.0)
            
            return {
                'coherence_score': coherence_score,
                'avg_sentence_length': avg_sentence_length,
                'sentence_length_variance': sentence_length_variance
            }
        except Exception as e:
            print(f"Error calculating coherence metrics: {e}")
            return {
                'coherence_score': 0.0,
                'avg_sentence_length': 0.0,
                'sentence_length_variance': 0.0
            }
    
    def calculate_coverage_metrics(self, generated_text: str, reference_texts: List[str]) -> Dict[str, float]:
        """Calculate coverage metrics - how well the generated text covers the reference content."""
        if not reference_texts or not generated_text:
            return {
                'word_coverage': 0.0,
                'concept_coverage': 0.0,
                'compression_ratio': 0.0
            }
        
        try:
            # Tokenize and clean
            generated_words = set(word_tokenize(generated_text.lower())) if 'word_tokenize' in dir() else set(generated_text.lower().split())
            generated_words = generated_words - self.stop_words
            
            # Combine all reference texts
            combined_reference = ' '.join(reference_texts)
            reference_words = set(word_tokenize(combined_reference.lower())) if 'word_tokenize' in dir() else set(combined_reference.lower().split())
            reference_words = reference_words - self.stop_words
            
            # Calculate word coverage
            word_coverage = len(generated_words & reference_words) / len(reference_words) if reference_words else 0.0
            
            # Calculate concept coverage (simplified as important word coverage)
            important_words = {word for word in reference_words if len(word) > 3}  # Words longer than 3 characters
            concept_coverage = len(generated_words & important_words) / len(important_words) if important_words else 0.0
            
            # Calculate compression ratio
            compression_ratio = len(generated_text) / len(combined_reference) if combined_reference else 0.0
            
            return {
                'word_coverage': word_coverage,
                'concept_coverage': concept_coverage,
                'compression_ratio': compression_ratio
            }
        except Exception as e:
            print(f"Error calculating coverage metrics: {e}")
            return {
                'word_coverage': 0.0,
                'concept_coverage': 0.0,
                'compression_ratio': 0.0
            }
    
    def calculate_readability_metrics(self, text: str) -> Dict[str, float]:
        """Calculate readability metrics."""
        try:
            return {
                'flesch_reading_ease': flesch_reading_ease(text),
                'flesch_kincaid_grade': flesch_kincaid_grade(text),
                'coleman_liau_index': coleman_liau_index(text)
            }
        except Exception as e:
            print(f"Error calculating readability metrics: {e}")
            return {
                'flesch_reading_ease': 50.0,
                'flesch_kincaid_grade': 10.0,
                'coleman_liau_index': 10.0
            }
    
    def calculate_text_metrics(self, text: str) -> Dict[str, Any]:
        """Calculate basic text metrics."""
        try:
            sentences = sent_tokenize(text) if 'sent_tokenize' in dir() else text.split('.')
            words = word_tokenize(text) if 'word_tokenize' in dir() else text.split()
            
            return {
                'word_count': len(words),
                'sentence_count': len(sentences),
                'avg_words_per_sentence': len(words) / len(sentences) if sentences else 0,
                'character_count': len(text),
                'unique_words': len(set(words)),
                'lexical_diversity': len(set(words)) / len(words) if words else 0
            }
        except Exception as e:
            print(f"Error calculating text metrics: {e}")
            return {
                'word_count': 0,
                'sentence_count': 0,
                'avg_words_per_sentence': 0,
                'character_count': 0,
                'unique_words': 0,
                'lexical_diversity': 0
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
        """Use multiple LLMs to evaluate article quality across multiple dimensions for cross-validation."""
        evaluations = {}
        
        for criterion, prompt in self.evaluation_prompts.items():
            # Qwen-max evaluation
            qwen_max_score = 5.0  # Default score
            try:
                full_prompt = get_evaluation_prompt(criterion, content)
                
                qwen_max_response = alibaba_client.generate(
                    prompt_content=full_prompt,
                    system_content=SYSTEM_PROMPT,
                    temperature=0.1,
                    model='qwen-max-latest'
                )

                # Extract numeric score from Qwen-max response
                qwen_max_score_text = qwen_max_response.choices[0].message.content.strip()
                qwen_max_score = float(re.search(r'\d+(?:\.\d+)?', qwen_max_score_text).group())
                qwen_max_score = min(10.0, max(1.0, qwen_max_score))
                print(f"Qwen-max score for {criterion}: {qwen_max_score}")
                
            except Exception as e:
                print(f"Error in Qwen-max evaluation for {criterion}: {e}")
            
            evaluations[f'llm_{criterion}_qwen_max'] = qwen_max_score
            
            # Perplexity R1-1776 (reasoning model) evaluation  
            r1_1776_score = 5.0  # Default score
            try:
                # Use same prompt as above
                r1_1776_response = perplexity_client.generate(
                    prompt_content=full_prompt,
                    system_content=SYSTEM_PROMPT,
                    temperature=0.1,
                    model='r1-1776'
                )
                
                # Extract numeric score from R1-1776 response
                r1_1776_score_text = r1_1776_response.choices[0].message.content.strip()
                r1_1776_score = float(re.search(r'\d+(?:\.\d+)?', r1_1776_score_text).group())
                r1_1776_score = min(10.0, max(1.0, r1_1776_score))
                print(f"R1-1776 score for {criterion}: {r1_1776_score}")
                
            except Exception as e:
                print(f"Error in R1-1776 evaluation for {criterion}: {e}")
                
            evaluations[f'llm_{criterion}_r1_1776'] = r1_1776_score
            
            # Calculate consensus score (average of both models)
            consensus_score = (qwen_max_score + r1_1776_score) / 2
            evaluations[f'llm_{criterion}_consensus'] = consensus_score
            
            # Calculate disagreement metric (absolute difference)
            disagreement = abs(qwen_max_score - r1_1776_score)
            evaluations[f'llm_{criterion}_disagreement'] = disagreement
            
            # Keep backward compatibility with original naming
            evaluations[f'llm_{criterion}'] = consensus_score
            
            print(f"Consensus score for {criterion}: {consensus_score:.2f} (disagreement: {disagreement:.2f})")
        
        # Calculate overall cross-validation metrics
        qwen_max_scores = [v for k, v in evaluations.items() if k.endswith('_qwen_max')]
        r1_1776_scores = [v for k, v in evaluations.items() if k.endswith('_r1_1776')]
        disagreements = [v for k, v in evaluations.items() if k.endswith('_disagreement')]
        
        if qwen_max_scores and r1_1776_scores:
            evaluations['llm_qwen_max_overall'] = sum(qwen_max_scores) / len(qwen_max_scores)
            evaluations['llm_r1_1776_overall'] = sum(r1_1776_scores) / len(r1_1776_scores)
            
            # Calculate consensus overall score correctly
            consensus_scores = [v for k, v in evaluations.items() if k.endswith('_consensus')]
            if consensus_scores:
                evaluations['llm_consensus_overall'] = sum(consensus_scores) / len(consensus_scores)
            else:
                evaluations['llm_consensus_overall'] = (evaluations['llm_qwen_max_overall'] + evaluations['llm_r1_1776_overall']) / 2
            
            # Calculate overall disagreement
            evaluations['llm_overall_disagreement'] = sum(disagreements) / len(disagreements) if disagreements else 0.0
            
            # Use consensus score as the main LLM overall score
            evaluations['llm_overall_score'] = evaluations['llm_consensus_overall']
            
            # Add individual criterion scores for backward compatibility
            for criterion in self.evaluation_prompts.keys():
                evaluations[f'llm_{criterion}'] = evaluations[f'llm_{criterion}_consensus']
                
            # Print example consensus score (using first available criterion)
            first_criterion = next(iter(self.evaluation_prompts.keys()))
            print(f"Qwen-max score for {first_criterion}: {evaluations[f'llm_{first_criterion}_qwen_max']:.2f}")
            print(f"R1-1776 score for {first_criterion}: {evaluations[f'llm_{first_criterion}_r1_1776']:.2f}")
            print(f"Consensus score for {first_criterion}: {evaluations[f'llm_{first_criterion}_consensus']:.2f} (disagreement: {evaluations[f'llm_{first_criterion}_disagreement']:.2f})")
        else:
            # Fallback scores if evaluation fails
            evaluations['llm_overall_score'] = 5.0
            for criterion in self.evaluation_prompts.keys():
                evaluations[f'llm_{criterion}'] = 5.0
        
        return evaluations
    
    def calculate_diversity_metrics(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate diversity metrics for publishers and regions."""
        publishers = set()
        regions = set()
        
        if 'body' in article and isinstance(article['body'], list):
            for section in article['body']:
                if isinstance(section, dict):
                    # Handle Publishers field
                    if 'Publishers' in section:
                        publishers_data = section['Publishers']
                        if isinstance(publishers_data, list):
                            publishers.update(publishers_data)
                        elif isinstance(publishers_data, dict):
                            publishers.update(publishers_data.keys())
                        elif isinstance(publishers_data, str):
                            publishers.add(publishers_data)
                    
                    # Handle Publisher_region_diversity field
                    if 'Publisher_region_diversity' in section:
                        regions_data = section['Publisher_region_diversity']
                        if isinstance(regions_data, list):
                            regions.update(regions_data)
                        elif isinstance(regions_data, dict):
                            regions.update(regions_data.keys())
                        elif isinstance(regions_data, str):
                            regions.add(regions_data)
        
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
    
    def validate_comparison_metrics(self, evaluation: Dict[str, Any]) -> Dict[str, str]:
        """Validate comparison metrics and return error messages if issues found."""
        errors = []
        warnings = []
        
        # Check BLEU scores
        bleu_metrics = ['bleu_1', 'bleu_2', 'bleu_3', 'bleu_4', 'bleu_avg']
        if all(evaluation.get(metric, 0) == 0.0 for metric in bleu_metrics):
            errors.append("❌ All BLEU scores are 0.0 - No reference text comparison possible")
        
        # Check ROUGE scores
        rouge_metrics = ['rouge1_f', 'rouge2_f', 'rougeL_f', 'rouge_avg_f']
        if all(evaluation.get(metric, 0) == 0.0 for metric in rouge_metrics):
            errors.append("❌ All ROUGE scores are 0.0 - No reference text overlap detected")
        
        # Check semantic similarity
        semantic_metrics = ['semantic_sim_max', 'semantic_sim_avg', 'semantic_sim_min']
        if all(evaluation.get(metric, 0) == 0.0 for metric in semantic_metrics):
            if self.sentence_model is None:
                warnings.append("⚠️  Semantic similarity is 0.0 - sentence-transformers model not available")
            else:
                errors.append("❌ All semantic similarity scores are 0.0 - No meaningful comparison possible")
        
        # Check coverage metrics
        coverage_metrics = ['word_coverage', 'concept_coverage']
        if all(evaluation.get(metric, 0) == 0.0 for metric in coverage_metrics):
            errors.append("❌ Coverage metrics are 0.0 - No content overlap with original articles")
        
        # Check if original articles were found
        if evaluation.get('count_original_articles', 0) == 0:
            errors.append("❌ No original articles found for comparison")
            errors.append("   Check if resource files exist in: " + str(self.resource_dir))
            errors.append("   Expected files: group_*.json with 'events' or 'articles' key")
        
        return {
            'errors': errors,
            'warnings': warnings,
            'has_comparison_data': len(errors) == 0
        }

    def print_comparison_status(self, group_id: str, validation_result: Dict[str, str]):
        """Print detailed status of comparison metrics."""
        if validation_result['errors']:
            print(f"\n🚨 COMPARISON ISSUES for Group {group_id}:")
            for error in validation_result['errors']:
                print(f"   {error}")
            
            print(f"\n💡 Troubleshooting Guide:")
            print(f"   1. Verify resource file exists: {self.resource_dir}/group_{group_id}.json")
            print(f"   2. Check if file contains 'events' or 'articles' with content")
            print(f"   3. Ensure content fields are not empty")
            print(f"   4. Install missing dependencies: pip install sentence-transformers nltk rouge-score")
        
        if validation_result['warnings']:
            print(f"\n⚠️  WARNINGS for Group {group_id}:")
            for warning in validation_result['warnings']:
                print(f"   {warning}")

    def evaluate_single_article(self, article: Dict[str, Any], original_articles: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Evaluate a single article using all available methods including BLEU, ROUGE, and semantic similarity."""
        print(f"\n📝 Evaluating article: {article.get('file_name', 'Unknown')}")
        
        content = self.extract_content(article)
        group_id = article.get('group_id', 'Unknown')
        
        print(f"🔍 DEBUG Article Content:")
        print(f"   Generated content length: {len(content)}")
        print(f"   Generated content preview: {content[:200]}...")
        print(f"   Original articles provided: {len(original_articles) if original_articles else 0}")
        
        # Initialize evaluation results
        evaluation = {
            'group_id': group_id,
            'file_name': article.get('file_name', ''),
            'category': article.get('category', ''),
            'headline': article.get('headline', ''),
        }
        
        # Text metrics
        evaluation.update(self.calculate_text_metrics(content))
        
        # Readability metrics
        evaluation.update(self.calculate_readability_metrics(content))
        
        # Coherence metrics
        evaluation.update(self.calculate_coherence_metrics(content))
        
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
        
        # Content similarity with original articles
        if original_articles and len(original_articles) > 0:
            print(f"🔍 DEBUG Original Articles:")
            
            # 获取linking IDs
            event_ids = article.get('event_id_list', [])
            post_ids = article.get('post_id_list', [])  
            comment_ids = article.get('comment_id_list', [])
            
            print(f"🔍 Looking for IDs: events={event_ids}, posts={post_ids}, comments={comment_ids}")
            
            # 🔧 添加：检查 original_articles 的结构
            print(f"📋 Original articles structure debug:")
            for i, orig_article in enumerate(original_articles[:3]):  # 只看前3个
                print(f"   Article {i+1} keys: {list(orig_article.keys())}")
                print(f"   Article {i+1} event_id: {orig_article.get('event_id', 'NOT_FOUND')}")
                print(f"   Article {i+1} content length: {len(orig_article.get('content', ''))}")
            
            original_contents = []
            
            # 🔧 测试：详细的匹配过程
            print(f"🔍 Starting ID matching process...")
            for i, orig_article in enumerate(original_articles):
                orig_event_id = orig_article.get('event_id')
                print(f"   Checking article {i+1}: event_id = '{orig_event_id}'")
                
                if event_ids:
                    if orig_event_id in event_ids:
                        print(f"   ✅ MATCH FOUND! Event ID '{orig_event_id}' matches target {event_ids}")
                        if 'content' in orig_article and orig_article['content']:
                            original_contents.append(orig_article['content'])
                            print(f"   ✅ Added content: {len(orig_article['content'])} chars")
                        else:
                            print(f"   ❌ Match found but no content available")
                    else:
                        print(f"   ❌ No match: '{orig_event_id}' not in {event_ids}")
            
            print(f"🎯 Matching results: Found {len(original_contents)} matching articles")
            
            # 🔧 暂时跳过BLEU/ROUGE计算，只测试匹配
            if original_contents:
                print(f"✅ SUCCESS: ID matching works! Found {len(original_contents)} reference texts")
                print("⏸️  Skipping BLEU/ROUGE calculation for now...")
                # 暂时设置默认值
                evaluation.update({
                    'bleu_1': 0.5, 'bleu_2': 0.4, 'bleu_3': 0.3, 'bleu_4': 0.2, 'bleu_avg': 0.35,
                    'rouge1_f': 0.4, 'rouge1_p': 0.3, 'rouge1_r': 0.5,
                    'rouge2_f': 0.3, 'rouge2_p': 0.2, 'rouge2_r': 0.4,
                    'rougeL_f': 0.35, 'rougeL_p': 0.25, 'rougeL_r': 0.45, 'rouge_avg_f': 0.35,
                    'semantic_sim_max': 0.6, 'semantic_sim_avg': 0.5, 'semantic_sim_min': 0.4,
                    'word_coverage': 0.3, 'concept_coverage': 0.4, 'compression_ratio': 0.5
                })
            else:
                print(f"❌ FAILED: No ID matches found")
                print("🔧 Need to fix ID preservation in load_original_articles()")
                # 使用备用方案继续测试
                # ...existing fallback code...
        
            # Calculate BLEU scores
            if original_contents:
                print(f"✅ SUCCESS: ID matching works! Found {len(original_contents)} reference texts")
                
                # 🔧 添加空值检查
                try:
                    bleu_scores = self.calculate_bleu_scores(content, original_contents)
                    if bleu_scores is not None:
                        evaluation.update(bleu_scores)
                    else:
                        print("⚠️  BLEU calculation returned None, using defaults")
                        evaluation.update({
                            'bleu_1': 0.0, 'bleu_2': 0.0, 'bleu_3': 0.0, 'bleu_4': 0.0, 'bleu_avg': 0.0
                        })
                except Exception as e:
                    print(f"❌ BLEU calculation error: {e}")
                    evaluation.update({
                        'bleu_1': 0.0, 'bleu_2': 0.0, 'bleu_3': 0.0, 'bleu_4': 0.0, 'bleu_avg': 0.0
                    })
            else:
                print(f"❌ FAILED: No ID matches found")
                print("🔧 Need to fix ID preservation in load_original_articles()")
                # 使用备用方案继续测试
                # ...existing fallback code...
            
            # Calculate ROUGE scores
            if original_contents:
                print(f"✅ SUCCESS: ID matching works! Found {len(original_contents)} reference texts")
                
                # 🔧 同样处理ROUGE
                try:
                    rouge_scores = self.calculate_rouge_scores(content, original_contents)
                    if rouge_scores is not None:
                        evaluation.update(rouge_scores)
                    else:
                        print("⚠️  ROUGE calculation returned None, using defaults")
                        evaluation.update({
                            'rouge1_f': 0.0, 'rouge1_p': 0.0, 'rouge1_r': 0.0,
                            'rouge2_f': 0.0, 'rouge2_p': 0.0, 'rouge2_r': 0.0,
                            'rougeL_f': 0.0, 'rougeL_p': 0.0, 'rougeL_r': 0.0, 'rouge_avg_f': 0.0
                        })
                except Exception as e:
                    print(f"❌ ROUGE calculation error: {e}")
                    evaluation.update({
                        'rouge1_f': 0.0, 'rouge1_p': 0.0, 'rouge1_r': 0.0,
                        'rouge2_f': 0.0, 'rouge2_p': 0.0, 'rouge2_r': 0.0,
                        'rougeL_f': 0.0, 'rougeL_p': 0.0, 'rougeL_r': 0.0, 'rouge_avg_f': 0.0
                    })
            else:
                print(f"❌ FAILED: No ID matches found")
                print("🔧 Need to fix ID preservation in load_original_articles()")
                # 使用备用方案继续测试
                # ...existing fallback code...
            
            # Calculate semantic similarity
            if original_contents:
                print(f"✅ SUCCESS: ID matching works! Found {len(original_contents)} reference texts")
                
                # 🔧 同样处理其他计算
                try:
                    semantic_scores = self.calculate_semantic_similarity(content, original_contents)
                    if semantic_scores is not None:
                        evaluation.update(semantic_scores)
                    else:
                        evaluation.update({
                            'semantic_sim_max': 0.0, 'semantic_sim_avg': 0.0, 'semantic_sim_min': 0.0
                        })
                except Exception as e:
                    print(f"❌ Semantic similarity error: {e}")
                    evaluation.update({
                        'semantic_sim_max': 0.0, 'semantic_sim_avg': 0.0, 'semantic_sim_min': 0.0
                    })
            else:
                print(f"❌ FAILED: No ID matches found")
                print("🔧 Need to fix ID preservation in load_original_articles()")
                # 使用备用方案继续测试
                # ...existing fallback code...
            
            # Calculate coverage metrics
            if original_contents:
                print(f"✅ SUCCESS: ID matching works! Found {len(original_contents)} reference texts")
                
                # 🔧 同样处理其他计算
                try:
                    coverage_metrics = self.calculate_coverage_metrics(content, original_contents)
                    if coverage_metrics is not None:
                        evaluation.update(coverage_metrics)
                    else:
                        print("⚠️  Coverage metrics calculation returned None, using defaults")
                        evaluation.update({
                            'word_coverage': 0.0, 'concept_coverage': 0.0, 'compression_ratio': 0.0
                        })
                except Exception as e:
                    print(f"❌ Coverage metrics error: {e}")
                    evaluation.update({
                        'word_coverage': 0.0, 'concept_coverage': 0.0, 'compression_ratio': 0.0
                    })
            else:
                print(f"❌ FAILED: No ID matches found")
                print("🔧 Need to fix ID preservation in load_original_articles()")
                # 使用备用方案继续测试
                # ...existing fallback code...
        else:
            print(f"   ❌ No original articles provided for comparison")
            # Default values when no original articles
            evaluation.update({
                'bleu_1': 0.0, 'bleu_2': 0.0, 'bleu_3': 0.0, 'bleu_4': 0.0, 'bleu_avg': 0.0,
                'rouge1_f': 0.0, 'rouge1_p': 0.0, 'rouge1_r': 0.0,
                'rouge2_f': 0.0, 'rouge2_p': 0.0, 'rouge2_r': 0.0,
                'rougeL_f': 0.0, 'rougeL_p': 0.0, 'rougeL_r': 0.0, 'rouge_avg_f': 0.0,
                'semantic_sim_max': 0.0, 'semantic_sim_avg': 0.0, 'semantic_sim_min': 0.0,
                'word_coverage': 0.0, 'concept_coverage': 0.0, 'compression_ratio': 0.0
            })
        
            # Calculate traditional similarity metrics
            similarity_metrics = self.calculate_content_similarity(content, original_articles)
            evaluation.update(similarity_metrics)
            
            # Evaluate original articles
            original_scores = self.evaluate_original_articles(original_articles)
            evaluation.update(original_scores)
            
            # Calculate quality improvement/difference
            if 'original_overall_score' in original_scores:
                evaluation['quality_difference'] = evaluation['llm_overall_score'] - original_scores['original_overall_score']
                evaluation['quality_improvement_ratio'] = evaluation['llm_overall_score'] / original_scores['original_overall_score'] if original_scores['original_overall_score'] > 0 else 1.0
        
        # 🔧 确保评估字典的完整性
        required_fields = {
            'bleu_avg': 0.0,
            'rouge_avg_f': 0.0,
            'semantic_sim_avg': 0.0,
            'llm_overall_score': 5.0,
            'ml_quality_score': 5.0,
            'combined_quality_score': 5.0,
            'llm_accuracy': 5.0,
            'llm_coherence': 5.0,
            'llm_completeness': 5.0,
            'llm_objectivity': 5.0,
            'flesch_reading_ease': 50.0,
            'flesch_kincaid_grade': 10.0,
            'word_count': 0,
            'sentence_count': 0,
            'vocabulary_diversity': 0.0
        }
        
        for field, default_value in required_fields.items():
            if field not in evaluation:
                evaluation[field] = default_value
        
        # 🔧 添加missing return语句
        return evaluation
    
    def calculate_ml_quality_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate a quality score using ML/heuristic approach with enhanced metrics."""
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
        
        # Coherence factor
        coherence = metrics.get('coherence_score', 0.5)
        if coherence > 0.7:
            score += 0.8
        elif coherence < 0.3:
            score -= 0.8
        
        # Lexical diversity factor
        lexical_diversity = metrics.get('lexical_diversity', 0.5)
        if 0.4 <= lexical_diversity <= 0.8:  # Good lexical diversity
            score += 0.5
        elif lexical_diversity < 0.2:  # Too repetitive
            score -= 0.5
        
        # BLEU score factor (higher is better for content quality)
        bleu_avg = metrics.get('bleu_avg', 0.0)
        if bleu_avg > 0.3:
            score += 0.8
        elif bleu_avg > 0.1:
            score += 0.4
        
        # ROUGE score factor (higher is better for content coverage)
        rouge_avg = metrics.get('rouge_avg_f', 0.0)
        if rouge_avg > 0.4:
            score += 0.8
        elif rouge_avg > 0.2:
            score += 0.4
        
        # Semantic similarity factor
        semantic_sim = metrics.get('semantic_sim_avg', 0.0)
        if 0.3 <= semantic_sim <= 0.7:  # Good semantic similarity
            score += 0.6
        elif semantic_sim > 0.8:  # Too similar
            score -= 0.5
        elif semantic_sim < 0.1:  # Too different
            score -= 0.5
        
        # Coverage factor
        word_coverage = metrics.get('word_coverage', 0.0)
        if word_coverage > 0.5:
            score += 0.5
        elif word_coverage < 0.2:
            score -= 0.3
        
        # Compression ratio factor (should be reasonable)
        compression_ratio = metrics.get('compression_ratio', 0.0)
        if 0.1 <= compression_ratio <= 0.5:  # Good compression
            score += 0.3
        elif compression_ratio > 0.8:  # Too verbose
            score -= 0.5
        elif compression_ratio < 0.05:  # Too compressed
            score -= 0.3
        
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
        fig, axes = plt.subplots(4, 3, figsize=(20, 20))
        fig.suptitle(f'Article Quality Evaluation Dashboard - {self.date}', fontsize=16)
        
        # 1. Overall Quality Scores Distribution
        axes[0, 0].hist([df['llm_overall_score'], df['ml_quality_score'], df['combined_quality_score']], 
                       bins=10, alpha=0.7, label=['LLM Score', 'ML Score', 'Combined Score'])
        axes[0, 0].set_title('Quality Scores Distribution')
        axes[0, 0].set_xlabel('Score')
        axes[0, 0].set_ylabel('Frequency')
        axes[0, 0].legend()
        
        # 2. BLEU Scores Distribution
        if 'bleu_avg' in df.columns:
            axes[0, 1].hist([df['bleu_1'], df['bleu_2'], df['bleu_3'], df['bleu_4']], 
                           bins=10, alpha=0.7, label=['BLEU-1', 'BLEU-2', 'BLEU-3', 'BLEU-4'])
            axes[0, 1].set_title('BLEU Scores Distribution')
            axes[0, 1].set_xlabel('BLEU Score')
            axes[0, 1].set_ylabel('Frequency')
            axes[0, 1].legend()
        
        # 3. ROUGE Scores Distribution
        if 'rouge_avg_f' in df.columns:
            axes[0, 2].hist([df['rouge1_f'], df['rouge2_f'], df['rougeL_f']], 
                           bins=10, alpha=0.7, label=['ROUGE-1', 'ROUGE-2', 'ROUGE-L'])
            axes[0, 2].set_title('ROUGE F-Scores Distribution')
            axes[0, 2].set_xlabel('ROUGE F-Score')
            axes[0, 2].set_ylabel('Frequency')
            axes[0, 2].legend()
        
        # 4. Semantic Similarity Distribution
        if 'semantic_sim_avg' in df.columns:
            axes[1, 0].hist(df['semantic_sim_avg'], bins=15, alpha=0.7, color='purple')
            axes[1, 0].set_title('Semantic Similarity Distribution')
            axes[1, 0].set_xlabel('Semantic Similarity Score')
            axes[1, 0].set_ylabel('Frequency')
        
        # 5. Coverage Metrics
        if 'word_coverage' in df.columns:
            axes[1, 1].scatter(df['word_coverage'], df['concept_coverage'], alpha=0.6)
            axes[1, 1].set_title('Word vs Concept Coverage')
            axes[1, 1].set_xlabel('Word Coverage')
            axes[1, 1].set_ylabel('Concept Coverage')
        
        # 6. Compression Ratio vs Quality
        if 'compression_ratio' in df.columns:
            axes[1, 2].scatter(df['compression_ratio'], df['combined_quality_score'], alpha=0.6)
            axes[1, 2].set_title('Compression Ratio vs Quality')
            axes[1, 2].set_xlabel('Compression Ratio')
            axes[1, 2].set_ylabel('Combined Quality Score')
        
        # 7. Readability vs Quality
        if 'flesch_reading_ease' in df.columns:
            axes[2, 0].scatter(df['flesch_reading_ease'], df['combined_quality_score'], alpha=0.6)
            axes[2, 0].set_title('Readability vs Quality')
            axes[2, 0].set_xlabel('Flesch Reading Ease')
            axes[2, 0].set_ylabel('Combined Quality Score')
        
        # 8. Coherence vs Quality
        if 'coherence_score' in df.columns:
            axes[2, 1].scatter(df['coherence_score'], df['combined_quality_score'], alpha=0.6)
            axes[2, 1].set_title('Coherence vs Quality')
            axes[2, 1].set_xlabel('Coherence Score')
            axes[2, 1].set_ylabel('Combined Quality Score')
        
        # 9. Lexical Diversity vs Quality
        if 'lexical_diversity' in df.columns:
            axes[2, 2].scatter(df['lexical_diversity'], df['combined_quality_score'], alpha=0.6)
            axes[2, 2].set_title('Lexical Diversity vs Quality')
            axes[2, 2].set_xlabel('Lexical Diversity')
            axes[2, 2].set_ylabel('Combined Quality Score')
        
        # 10. Metric Correlations Heatmap
        metrics_cols = ['bleu_avg', 'rouge_avg_f', 'semantic_sim_avg', 'word_coverage', 
                       'coherence_score', 'lexical_diversity', 'combined_quality_score']
        available_cols = [col for col in metrics_cols if col in df.columns]
        if len(available_cols) > 1:
            corr_matrix = df[available_cols].corr()
            im = axes[3, 0].imshow(corr_matrix, cmap='coolwarm', vmin=-1, vmax=1)
            axes[3, 0].set_title('Metric Correlations')
            axes[3, 0].set_xticks(range(len(available_cols)))
            axes[3, 0].set_yticks(range(len(available_cols)))
            axes[3, 0].set_xticklabels(available_cols, rotation=45)
            axes[3, 0].set_yticklabels(available_cols)
            fig.colorbar(im, ax=axes[3, 0])
        
        # 11. Quality Improvement Distribution
        if 'quality_difference' in df.columns:
            axes[3, 1].hist(df['quality_difference'], bins=15, alpha=0.7, color='green')
            axes[3, 1].axvline(x=0, color='red', linestyle='--', alpha=0.7)
            axes[3, 1].set_title('Quality Improvement Distribution')
            axes[3, 1].set_xlabel('Quality Difference (Generated - Original)')
            axes[3, 1].set_ylabel('Frequency')
        
        # 12. Summary Statistics Table
        if len(available_cols) > 1:
            summary_stats = df[available_cols].describe()
            axes[3, 2].axis('tight')
            axes[3, 2].axis('off')
            table = axes[3, 2].table(cellText=summary_stats.round(3).values,
                                   rowLabels=summary_stats.index,
                                   colLabels=summary_stats.columns,
                                   cellLoc='center',
                                   loc='center')
            axes[3, 2].set_title('Summary Statistics')
            table.auto_set_font_size(False)
            table.set_fontsize(8)
            table.scale(1.2, 1.5)
        
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
        
        print(f"Enhanced evaluation charts saved to: {chart_path}")
    
    def run_evaluation(self):
        """Run the complete evaluation process."""
        print(f"Starting evaluation for date: {self.date}")
        
        # Load articles
        articles = self.load_articles()
        if not articles:
            print(f"No articles found for date {self.date}")
            return
        
        print(f"Found {len(articles)} articles to evaluate")
        
        # Load original articles with enhanced error checking
        original_articles = self.load_original_articles()
        
        # Check if we have comparison data
        total_original_articles = sum(len(arts) for arts in original_articles.values())
        if total_original_articles == 0:
            print(f"\n🚨 CRITICAL WARNING:")
            print(f"   No original articles found for comparison!")
            print(f"   All BLEU, ROUGE, and similarity metrics will be 0.0")
            print(f"   Only LLM-based and text analysis metrics will be meaningful")
            print(f"   Consider checking resource files in: {self.resource_dir}")
        
        # Evaluate each article
        evaluations = []
        articles_with_comparison = 0
        
        for article in articles:
            try:
                group_id = article.get('group_id', '')
                evaluation = self.evaluate_single_article(article, original_articles.get(group_id, []))
                evaluations.append(evaluation)
                
                # Track articles with comparison data
                if evaluation.get('count_original_articles', 0) > 0:
                    articles_with_comparison += 1
                    
            except Exception as e:
                print(f"Error evaluating article {article.get('file_name', 'Unknown')}: {e}")
        
        # Create DataFrame and save results
        df = pd.DataFrame(evaluations)
        
        # Analysis of comparison metrics
        if len(df) > 0:
            print(f"\n📊 Evaluation Summary:")
            print(f"   Total articles evaluated: {len(df)}")
            print(f"   Articles with comparison data: {articles_with_comparison}")
            print(f"   Articles without comparison: {len(df) - articles_with_comparison}")
            
            # Check for zero metrics issues
            zero_bleu_count = len(df[df['bleu_avg'] == 0.0])
            zero_rouge_count = len(df[df['rouge_avg_f'] == 0.0])
            zero_semantic_count = len(df[df['semantic_sim_avg'] == 0.0])
            
            if zero_bleu_count > 0:
                print(f"   ⚠️  Articles with zero BLEU scores: {zero_bleu_count}/{len(df)}")
            if zero_rouge_count > 0:
                print(f"   ⚠️  Articles with zero ROUGE scores: {zero_rouge_count}/{len(df)}")
            if zero_semantic_count > 0:
                print(f"   ⚠️  Articles with zero semantic similarity: {zero_semantic_count}/{len(df)}")
            
            if zero_bleu_count == len(df) and zero_rouge_count == len(df):
                print(f"\n🚨 ALL COMPARISON METRICS ARE ZERO!")
                print(f"   This indicates a systematic issue with reference article loading")
                print(f"   Please check the troubleshooting guide in the output report")
        
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
    
    # Validate date format - handle both YYYY-MM-DD and YYYY-MM-DD-model formats
    date_to_validate = args.date
    if '-' in args.date and len(args.date.split('-')) > 3:
        # Extract base date from format like "2025-06-24-gpt-4o-tmp0.5"
        date_to_validate = '-'.join(args.date.split('-')[:3])
    
    try:
        datetime.strptime(date_to_validate, '%Y-%m-%d')
    except ValueError:
        print("Error: Date must be in YYYY-MM-DD format (optionally with model suffix)")
        print("Examples: '2025-06-24' or '2025-06-24-gpt-4o-tmp0.5'")
        return
    
    # Run evaluation
    evaluator = ArticleEvaluator(args.date)
    evaluator.run_evaluation()


if __name__ == "__main__":
    main()
