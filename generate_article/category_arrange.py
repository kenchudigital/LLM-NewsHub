import os
import sys
import json
import glob
from pathlib import Path
from collections import Counter, defaultdict
import re
import argparse

# Add project root to Python path
project_root = Path.cwd()
sys.path.append(str(project_root))

from classifier.category.predict import predict_single_text

def extract_text_from_group(group_data):
    """Extract meaningful text content from a group JSON structure"""
    text_parts = []
    
    # Add headline and subheadline
    if 'headline' in group_data and group_data['headline']:
        text_parts.append(group_data['headline'])
    
    if 'subheadline' in group_data and group_data['subheadline']:
        text_parts.append(group_data['subheadline'])
    
    # Add lead paragraph
    if 'lead' in group_data and group_data['lead']:
        text_parts.append(group_data['lead'])
    
    # Add body content (first few sections to avoid too much text)
    if 'body' in group_data and isinstance(group_data['body'], list):
        for i, section in enumerate(group_data['body'][:3]):  # Limit to first 3 sections
            if isinstance(section, dict) and 'content' in section:
                # Clean the content (remove Reddit references and other noise)
                content = section['content']
                # Remove references like (Reddit: {{fake_news_probability}})
                content = re.sub(r'\(Reddit: \{\{[^}]+\}\}\)', '', content)
                text_parts.append(content)
    
    # Add conclusion if available
    if 'conclusion' in group_data and group_data['conclusion']:
        text_parts.append(group_data['conclusion'])
    
    # Join all parts with spaces
    combined_text = ' '.join(text_parts)
    
    # Clean up extra whitespace
    combined_text = re.sub(r'\s+', ' ', combined_text).strip()
    
    return combined_text

def map_classifier_category_to_target(classifier_category, probabilities):
    """Map classifier categories to target categories: social, tech, entertainment"""
    # Direct mappings
    if classifier_category == 'tech':
        return 'tech'
    elif classifier_category == 'entertainment':
        return 'entertainment'
    elif classifier_category == 'business' or classifier_category == 'politics':
        return 'social'
    elif classifier_category == 'sport':
        return 'sport'
    else:
        print('type: ', classifier_category)
        return 'unknown'

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate news articles from grouped data')
    parser.add_argument('--date', type=str, required=True, help='Date in YYYY-MM-DD format')
    args = parser.parse_args()
    date_str = args.date
    
    groups_dir = Path(f"data/output/article/{date_str}")

    print("Starting group categorization...")
    print(f"Looking for group files in: {groups_dir}")

    # Find all group JSON files
    group_files = list(groups_dir.glob("group_*.json"))

    if not group_files:
        print(f"No group_*.json files found in {groups_dir}")
    else:
        print(f"Found {len(group_files)} group files to categorize...")

    # Store results
    group_categories = {}
    category_counts = Counter()
    detailed_results = {}

    # Process each group file
    for group_file in sorted(group_files):
        group_id = group_file.stem  # e.g., 'group_1'
        
        print(f"Processing {group_id}...")
        
        try:
            # Load group data
            with open(group_file, 'r', encoding='utf-8') as f:
                group_data = json.load(f)
            
            # Extract text content
            text_content = extract_text_from_group(group_data)
            
            if not text_content.strip():
                print(f"Warning: No text content found for {group_id}")
                continue
            
            # Get prediction from classifier
            print(f"Classifying text ({len(text_content)} chars)...")
            probabilities = predict_single_text(text_content[:5000])  # Limit text length
            
            if probabilities is None:
                print(f"Failed to classify {group_id}")
                continue
            
            # Find the category with highest probability
            best_category = max(probabilities, key=probabilities.get)
            best_probability = probabilities[best_category]
            
            # Map to target categories
            mapped_category = map_classifier_category_to_target(best_category, probabilities)
            
            # Store results
            group_categories[group_id] = mapped_category
            category_counts[mapped_category] += 1
            
            # Store detailed results
            detailed_results[group_id] = {
                'predicted_category': best_category,
                'mapped_category': mapped_category,
                'probability': best_probability,
                'all_probabilities': probabilities,
                'text_length': len(text_content),
                'original_category': group_data.get('category', 'unknown')
            }
            
        except Exception as e:
            print(f"Error processing {group_id}: {str(e)}")
            continue

    if group_categories:
        # Display final results
        print(f"\nCategorization complete!")
        print(f"Final distribution:")
        for category, count in category_counts.items():
            print(f"   {category}: {count}")
        
        # Save the mapping to JSON
        output_file = f"data/output/article/{date_str}/group_categories.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(group_categories, f, indent=2, ensure_ascii=False)
        
        print(f"\nResults saved to {output_file}")
        
        # Display the mapping
        print(f"\nFinal mapping:")
        for group_id, category in sorted(group_categories.items()):
            print(f'"{group_id}": "{category}"')
        
        # Also save in the exact format you requested
        print(f"\nFinal JSON mapping:")
        print(json.dumps(group_categories, indent=2))

    else:
        print("No groups were successfully categorized")