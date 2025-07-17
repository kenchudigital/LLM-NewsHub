# Article Quality Evaluation System

## Overview

This evaluation system provides comprehensive quality assessment for generated news articles using state-of-the-art NLP metrics, traditional readability measures, and AI-based evaluation techniques. The system compares generated articles against original source articles using multiple dimensions of quality assessment.

## Installation Requirements

```bash
pip install nltk rouge-score sentence-transformers transformers torch scikit-learn
pip install pandas numpy matplotlib seaborn textstat
```

## Usage

```bash
python evaluate/evaluate.py --date "2025-06-24"
python evaluate/evaluate.py --date "2025-06-24"
```

## Evaluation Metrics

| Metric Name                | Description                                                      | Source                        |
|---------------------------|------------------------------------------------------------------|-------------------------------|
| BLEU                      | Measures n-gram overlap between generated and reference text      | ML - nltk                     |
| ROUGE-1, ROUGE-2, ROUGE-L | Measures unigram, bigram, and longest common subsequence overlap | ML - rouge-score              |
| Semantic Similarity       | Sentence embedding cosine similarity between texts               | ML - sentence-transformers    |
| Coherence                 | Measures sentence/paragraph structure and logical flow            | ML - custom (NLP heuristics)  |
| Coverage                  | Measures how much reference content is covered in generation      | ML - custom (NLP heuristics)  |
| Readability (Flesch, FK, CLI) | Standard readability indices (Flesch, Flesch-Kincaid, Coleman-Liau) | ML - textstat                 |
| Text Metrics (length, vocab, etc.) | Basic statistics: length, vocabulary size, etc.           | ML - Python                   |
| Sentiment Consistency     | Checks if sentiment is consistent with reference                  | ML - nltk (VADER/heuristics)  |
| Fake News Probability     | Probability of fake news content                                  | ML - custom/model output      |
| LLM Evaluation            | LLM-based scoring of article quality and attributes               | LLM evaluate (OpenAI, etc.)   |
| Diversity                 | Measures diversity of content and sources                         | ML - custom (NLP heuristics)  |
| Content Similarity        | Compares generated content to original articles                   | ML - sentence-transformers    |

## Dependencies
- `nltk`: BLEU score calculation and tokenization
- `rouge-score`: ROUGE metric implementation
- `sentence-transformers`: Semantic similarity embeddings
- `transformers`: Advanced NLP models
- `textstat`: Readability metrics
- `scikit-learn`: Machine learning utilities

## Troubleshooting

### Common Issues
1. **NLTK data not found**: Run `nltk.download()` for required packages
2. **Out of memory**: Reduce batch size or use CPU-only mode
3. **Missing dependencies**: Install all required packages
4. **Empty results**: Check input data format and file paths