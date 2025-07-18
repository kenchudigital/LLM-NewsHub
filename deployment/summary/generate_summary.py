import os
import json
import argparse
from pathlib import Path
from datetime import datetime
import sys

# Add project root to path to import llm_client
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from llm_client import openai_client, perplexity_client, alibaba_client, gemini_client

def read_articles_from_directory(date):
    """Read all article JSON files from the specified date directory"""
    input_path = f'data/output/article/{date}'
    
    if not os.path.exists(input_path):
        print(f"Error: Directory {input_path} does not exist")
        return []
    
    articles = []
    article_files = [f for f in os.listdir(input_path) if f.endswith('.json')]
    
    print(f"Found {len(article_files)} article files in {input_path}")
    
    for filename in article_files:
        file_path = os.path.join(input_path, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                article_data = json.load(f)
                articles.append(article_data)
        except Exception as e:
            print(f"Error reading {filename}: {e}")
    
    return articles

def extract_article_content(article):
    """Extract key content from an article"""
    content_parts = []
    
    # Add headline and lead
    if article.get('headline'):
        content_parts.append(f"Headline: {article['headline']}")
    if article.get('lead'):
        content_parts.append(f"Lead: {article['lead']}")
    
    # Add body content
    if article.get('body'):
        for section in article['body']:
            if section.get('content'):
                content_parts.append(f"{section['section']}: {section['content']}")
    
    # Add conclusion
    if article.get('conclusion'):
        content_parts.append(f"Conclusion: {article['conclusion']}")
    
    return "\n\n".join(content_parts)

def generate_summary_prompt(articles):
    """Generate the prompt with all article content"""
    all_content = []
    
    for i, article in enumerate(articles, 1):
        article_content = extract_article_content(article)
        all_content.append(f"Article {i}:\n{article_content}")
    
    combined_content = "\n\n" + "="*50 + "\n\n".join(all_content)
    
    prompt = f"""
Please generate a summary of the following news articles. 

<example>
    Good evening, I'm your AI Reporter. Today's top story: The Middle East crisis has reached new heights. Israel launched its most intense attack yet on Tehran, targeting the notorious Evin prison, while the US dropped massive bunker-buster bombs on Iran's nuclear sites. President Trump called it a 'Bullseye' and openly discussed regime change, prompting Iran to threaten: 'Mr Trump, the gambler, you may start this war, but we will be the ones to end it.'
    In business news, Hugo Boss is making headlines for all the wrong reasons - they've demanded a small Liverpool pet shop called 'Boss Pets' take down their website over trademark infringement. The owner, Ben McDonald, says his 'whole world collapsed' when he received the letter.
    And in entertainment, Amazon has announced a radical reimagining of James Bond as 'Double-O-Prime' - complete with Kindle Fire endorsements and overnight toilet paper delivery. The iconic spy will now say 'The name is Bond, James Bond - and I love my Kindle Fire!'
    This is AI News Sense. Stay informed, stay safe. For more detailed coverage of these stories, you can find the full articles below.
</example>

<news_articles>
{combined_content}
</news_articles>

Please generate a comprehensive summary in the same style as the example above, covering the main stories from all articles provided. The length of the speech should be around 1 mintues.
"""
    
    return prompt

def save_summary(summary_text, date):
    """Save the summary to the output file"""
    output_path = 'deployment/summary/resource/summary.txt'
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(summary_text)
        print(f"Summary saved to {output_path}")
        return True
    except Exception as e:
        print(f"Error saving summary: {e}")
        return False

def generate_llm_summary(prompt, llm_provider='ALIBABA'):
    """Generate summary using LLM client"""
    try:
        # Select the appropriate LLM client
        if llm_provider.upper() == 'GEMINI':
            client = openai_client
            model = 'gemini-2.5-pro'
        elif llm_provider.upper() == 'ALIBABA':
            client = alibaba_client
            model = 'qwen-max'
        elif llm_provider.upper() == 'PERPLEXITY':
            client = perplexity_client
            model = 'llama-3.1-8b-instant' # change model here !
        else:
            print(f"Unknown LLM provider: {llm_provider}. Using OpenAI as default.")
            client = openai_client
            model = 'gpt-4o-mini'
        
        print(f"Generating summary using {llm_provider} with model: {model}")
        
        # Generate the summary
        system_prompt = "You are an AI news reporter. Generate a comprehensive, engaging summary of the provided news articles in a broadcast-style format. Focus on the most important stories and maintain a professional yet accessible tone."
        
        response = client.generate(
            prompt_content=prompt,
            system_content=system_prompt,
            temperature=0.3,
            model=model
        )
        
        # Extract the content from the response
        if hasattr(response, 'choices') and len(response.choices) > 0:
            summary = response.choices[0].message.content
        else:
            # Fallback for different response formats
            summary = str(response)
        
        return summary
        
    except Exception as e:
        print(f"Error generating LLM summary: {e}")
        # Return a fallback summary
        return f""" error ! """

def main():
    parser = argparse.ArgumentParser(description='Generate summary from articles')
    parser.add_argument('--date', type=str, required=True, help='Date in YYYY-MM-DD format')
    parser.add_argument('--llm-provider', type=str, default='ALIBABA', 
                       choices=['OPENAI', 'PERPLEXITY', 'ALIBABA', 'GEMINI'],
                       help='LLM provider to use for summary generation (default: ALIBABA)')
    
    args = parser.parse_args()
    date = args.date
    llm_provider = args.llm_provider
    
    print(f"Generating summary for date: {date} using {llm_provider}")
    
    # Read all articles
    articles = read_articles_from_directory(date)
    
    if not articles:
        print("No articles found. Exiting.")
        return
    
    print(f"Successfully loaded {len(articles)} articles")
    
    # Generate summary prompt
    prompt = generate_summary_prompt(articles)
    
    prompt_path = 'deployment/summary/resource/summary_prompt.txt'
    os.makedirs(os.path.dirname(prompt_path), exist_ok=True)
    
    with open(prompt_path, 'w', encoding='utf-8') as f:
        f.write(prompt)
    
    print(f"Prompt saved to {prompt_path}")
    print(f"Prompt length: {len(prompt)} characters")
    
    # Generate the actual summary using the LLM
    if not llm_provider:
        llm_provider = 'ALIBABA'
    llm_summary = generate_llm_summary(prompt, llm_provider)
    
    # Save the summary
    save_summary(llm_summary, date)
    
    print("Summary generation complete!")

if __name__ == "__main__":
    main()