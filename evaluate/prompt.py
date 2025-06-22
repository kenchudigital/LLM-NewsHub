# System prompt for LLM evaluation
SYSTEM_PROMPT = "You are an expert journalist and article quality evaluator. Provide objective, professional assessments."

# Evaluation criteria prompts
EVALUATION_PROMPTS = {
    'coherence': "Rate the coherence and logical flow of this article from 1-10. Consider if ideas connect smoothly and the narrative makes sense.",
    'factual_accuracy': "Rate the apparent factual accuracy and credibility of this article from 1-10. Look for unrealistic claims or inconsistencies.",
    'writing_quality': "Rate the writing quality of this article from 1-10. Consider grammar, style, clarity, and professional journalistic standards.",
    'completeness': "Rate how complete and comprehensive this article is from 1-10. Consider if it covers the topic thoroughly.",
    'bias_neutrality': "Rate how neutral and unbiased this article appears from 1-10. Look for partisan language or one-sided reporting."
}

def get_evaluation_prompt(criterion: str, content: str) -> str:
    """
    Generate a full evaluation prompt for a specific criterion.
    
    Args:
        criterion: The evaluation criterion (e.g., 'coherence', 'factual_accuracy')
        content: The article content to evaluate
        
    Returns:
        The complete prompt string
    """
    if criterion not in EVALUATION_PROMPTS:
        raise ValueError(f"Unknown evaluation criterion: {criterion}")
    
    prompt = EVALUATION_PROMPTS[criterion]
    
    full_prompt = f""" 

{prompt}

Article to evaluate:
{content[:3000]}  # Limit content length for API efficiency

Please respond with just a number from 1-10, where 10 is excellent and 1 is poor.
"""
    
    return full_prompt
