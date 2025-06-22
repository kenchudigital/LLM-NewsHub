# Group size configuration settings

# Maximum group size for clustering process
# Groups larger than this will be split into smaller subgroups
MAX_GROUP_SIZE_CLUSTERING = 50

# Maximum group size for article generation
# Groups larger than this will be skipped during article generation
MAX_GROUP_SIZE_GENERATION = 50

# Grouping algorithm parameters
CLUSTERING_PARAMS = {
    'max_features': 1000,
    'ngram_range': (1, 2),
    'random_state': 42,
    'n_init': 10
}

# Size thresholds for different scenarios
SIZE_THRESHOLDS = {
    'small': 10,    # Groups with ≤10 items
    'medium': 30,   # Groups with 11-30 items  
    'large': 50,    # Groups with 31-50 items
    'xlarge': 100   # Groups with 51-100 items (to be split)
}

# How to determine optimal group size:
# 1. Consider LLM token limits (typically 4K-8K tokens)
# 2. Average content length per item
# 3. Processing time constraints
# 4. Article quality requirements

def get_max_group_size(context='generation'):
    """Get the appropriate max group size for different contexts"""
    if context == 'clustering':
        return MAX_GROUP_SIZE_CLUSTERING
    elif context == 'generation':
        return MAX_GROUP_SIZE_GENERATION
    else:
        return 50  # Default

def suggest_optimal_size(avg_content_length, token_limit=4000):
    """Suggest optimal group size based on content characteristics"""
    # Rough estimate: each item might use avg_content_length * 1.3 tokens
    # (including metadata and formatting)
    estimated_tokens_per_item = avg_content_length * 1.3
    
    # Reserve 1000 tokens for prompt template and output
    available_tokens = token_limit - 1000
    
    # Calculate max items that fit within token limit
    max_items = int(available_tokens / estimated_tokens_per_item)
    
    # Apply safety margin and reasonable bounds
    suggested_size = max(5, min(max_items * 0.8, 50))
    
    return int(suggested_size) 