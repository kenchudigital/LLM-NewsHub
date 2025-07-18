import pandas as pd
import json
import os
from datetime import datetime
from pathlib import Path
import sys
from typing import Dict, List, Optional, Union
import ast
import time
from config.group_settings import get_max_group_size

# Add tiktoken for token counting
try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    print("Warning: tiktoken not available. Install with: pip install tiktoken")
    TIKTOKEN_AVAILABLE = False

project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Use relative import
from llm_client import LLMClient
from generate_article.prompt import get_prompt_templates, format_prompt
import argparse

def count_tokens(text: str, model: str = "gpt-4") -> int:
    """Count tokens in text using tiktoken for accurate token counting."""
    if not TIKTOKEN_AVAILABLE:
        # Fallback: rough estimation (1 token ≈ 4 characters for English)
        return len(text) // 4
    
    try:
        # Get the appropriate encoding for the model
        if model.startswith("gpt-4"):
            encoding = tiktoken.encoding_for_model("gpt-4")
        elif model.startswith("gpt-3.5"):
            encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        else:
            # Default to cl100k_base for most modern models
            encoding = tiktoken.get_encoding("cl100k_base")
        
        return len(encoding.encode(text))
    except Exception as e:
        print(f"Error counting tokens: {e}")
        # Fallback estimation
        return len(text) // 4

def log_token_usage_unified(date_str: str, group_id: int, model: str, publisher: str, 
                          prompt: str, system_prompt: str, response_content: str = None, 
                          response_tokens: Optional[int] = None, error: str = None, status: str = "success"):
    """Log token usage to a unified JSON file for all groups, including errors."""
    # Count input tokens (always available)
    input_tokens = count_tokens(prompt, model) + count_tokens(system_prompt, model)
    
    # Count output tokens only if response available
    output_tokens = 0
    if response_content:
        output_tokens = response_tokens or count_tokens(response_content, model)
    
    # Create log entry
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "date": date_str,
        "group_id": group_id,
        "model": model,
        "publisher": publisher,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "status": status,  # "success", "error", "timeout", etc.
        "error": error if error else None
    }
    
    # Ensure log directory exists
    log_dir = Path(f"data/eval_token_log/{date_str}")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Unified log file for all groups
    unified_log_file = log_dir / "unified_token_log.json"
    
    # Read existing logs or create empty list
    logs = []
    if unified_log_file.exists():
        try:
            with open(unified_log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        except (json.JSONDecodeError, Exception) as e:
            print(f"Warning: Could not read existing log file: {e}")
            logs = []
    
    # Append new log entry
    logs.append(log_entry)
    
    # Write back to file
    with open(unified_log_file, 'w', encoding='utf-8') as f:
        json.dump(logs, f, indent=2, ensure_ascii=False)
    
    # Also keep individual log file for backward compatibility
    log_file = log_dir / f"token_log_group_{group_id}.json"
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(log_entry, f, indent=2, ensure_ascii=False)
    return log_entry

def log_token_usage(date_str: str, group_id: int, model: str, publisher: str, 
                   prompt: str, system_prompt: str, response_content: str, 
                   response_tokens: Optional[int] = None):
    """Log simplified token usage as JSON for evaluation."""
    # Use the new unified logging function for backward compatibility
    return log_token_usage_unified(
        date_str=date_str,
        group_id=group_id,
        model=model,
        publisher=publisher,
        prompt=prompt,
        system_prompt=system_prompt,
        response_content=response_content,
        response_tokens=response_tokens,
        status="success"
    )

def format_token_info(prompt: str, system_prompt: str, model: str = "gpt-4") -> str:
    """Format detailed token information for debugging."""
    prompt_tokens = count_tokens(prompt, model)
    system_tokens = count_tokens(system_prompt, model)
    total_tokens = prompt_tokens + system_tokens
    
    return f""" Token Analysis:
            • System Prompt: {system_tokens:,} tokens
            • User Prompt: {prompt_tokens:,} tokens
            • Total Input: {total_tokens:,} tokens
            • Prompt Length: {len(prompt):,} characters
            • System Length: {len(system_prompt):,} characters
            """     

def generate_article(date_str: str, model: str):
    """Generate article for a given date"""
    group_df = pd.read_csv(f'data/group/{date_str}/group_result.csv')

    group_id_list = list(group_df['group_id'])

    for group_id in group_id_list:
        # RESUME: Skip groups before 45 (uncomment this line when resume not needed)

        # -------------------- RESUME HERE --------------------

        # if group_id in [1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 12, 13, 14,15,17, 18, 19, 21, 23] : continue # 22 

        # -------------------- RESUME HERE --------------------
        
        # Check group size and skip if too large
        group_row = group_df[group_df['group_id'] == group_id]
        group_size = group_row.iloc[0]['size']
        
        # Import configuration
        MAX_GROUP_SIZE = 60  # Fallback default
            
        if group_size > MAX_GROUP_SIZE:
            print(f"Skipping Group {group_id} - too large (size: {group_size}, max: {MAX_GROUP_SIZE})")
            continue

        output_file_path = Path(f"data/output/article/group_{group_id}.json")
        if output_file_path.exists():
            print(f"Skipping Group {group_id} - output file already exists: {output_file_path}")
            continue

        small_group_df = group_df[group_df['group_id'] == group_id]

        event_id_list = ast.literal_eval(small_group_df.iloc[0]['event_ids'])
        post_id_list = ast.literal_eval(small_group_df.iloc[0]['post_ids'])

        def get_event_by_id(event_id_list, date):
            df = pd.read_csv(f'data/card/event_card/{date}.csv')
            return df[df['event_id'].isin(event_id_list)]

        def get_post_by_id(post_id_list, date):
            df = pd.read_csv(f'data/card/statement_card/posts/{date}.csv')
            return df[df['post_id'].isin(post_id_list)]
    
        def get_article_by_url(url_list, date):
            # Find all CSV files with the date in any subfolder
            fundus_dir = Path('data/raw/fundus')
            csv_files = list(fundus_dir.rglob(f'{date}.csv'))
            if not csv_files:
                print(f"No CSV file found for date {date}")
                return pd.DataFrame()
        
            # Read and combine all matching CSV files
            dfs = []
            for file in csv_files:
                try:
                    df = pd.read_csv(file)
                    dfs.append(df)
                except Exception as e:
                    print(f"Error reading {file}: {e}")
                    continue
            
            if not dfs:
                return pd.DataFrame()
            
            # Combine all dataframes
            combined_df = pd.concat(dfs, ignore_index=True)
            
            # Filter by url_list
            return combined_df[combined_df['link'].isin(url_list)]
    
        def get_comment_by_id(post_id_list, date):
            df = pd.read_csv(f'data/card/statement_card/comments/{date}.csv')
            return df[df['post_id'].isin(post_id_list)]
        
        event_df = get_event_by_id(event_id_list, date_str)
        url_list = list(set(event_df['link']))
        post_df = get_post_by_id(post_id_list, date_str)
        comment_df = get_comment_by_id(post_id_list, date_str)
        article_df = get_article_by_url(url_list, date_str)

        # Convert DataFrames to JSON format suitable for LLM prompt
        events_json = json.dumps(event_df.to_dict('records'), indent=2, default=str)
        posts_json = json.dumps(post_df.to_dict('records'), indent=2, default=str) 
        comments_json = json.dumps(comment_df.to_dict('records'), indent=2, default=str)

        system_prompt = get_prompt_templates()[0]
        prompt = format_prompt(
            events=events_json,
            posts=posts_json,
            comments=comments_json
        )

        model = 'qwen-plus'
        # model = 'qwen-max-latest'
        # model = 'qwen-vl-max'
        publisher = 'ALIBABA'

        # model = 'gpt-4o'     
        # publisher = 'OPENAI'

        # model = 'sonar-pro' # reasoning model
        # model = 'r1-1776'
        # publisher = 'PERPLEXITY'

        # model = 'gemini-2.0-flash'
        # model = 'gemini-2.5-pro'
        # publisher = 'GEMINI'

        client = LLMClient(publisher=publisher)

        # Display token information before sending request
        token_info = format_token_info(prompt, system_prompt, model)
        print(f"\nGroup {group_id} Token Analysis:{token_info}")
        
        # Check if tokens exceed common limits
        total_tokens = count_tokens(prompt, model) + count_tokens(system_prompt, model)
        if total_tokens > 8000:
            print(f"Warning: {total_tokens:,} tokens exceeds GPT-4 limit (8K)")
        elif total_tokens > 4000:
            print(f"Warning: {total_tokens:,} tokens may exceed some model limits")
        
        print("\nSending request to LLM...")
        
        # Retry logic for 503 errors
        max_retries = 3
        retry_delay = 60  # 60 seconds
        response = None
        llm_error = None
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    print(f"Retry attempt {attempt + 1}/{max_retries} for Group {group_id}")
                response = client.generate(
                    prompt_content=prompt,
                    system_content=system_prompt,
                    model=model,
                    timeout=1000
                )
                if model == 'gemini-2.0-flash':
                    time.sleep(6)
                elif model == 'gemini-2.5-pro':
                    time.sleep(12)
                print("\nReceived response from LLM")
                llm_error = None
                break
            except Exception as e:
                error_str = str(e)
                is_503_error = ("503" in error_str or "overloaded" in error_str.lower() or "unavailable" in error_str.lower())
                llm_error = e
                if is_503_error and attempt < max_retries - 1:
                    print(f"503 Service Unavailable for Group {group_id} (attempt {attempt + 1}/{max_retries}): {e}")
                    print(f"Waiting {retry_delay} seconds before retry...")
                    log_token_usage_unified(
                        date_str=date_str,
                        group_id=group_id,
                        model=model,
                        publisher=publisher,
                        prompt=prompt,
                        system_prompt=system_prompt,
                        error=f"503 retry attempt {attempt + 1}: {str(e)}",
                        status="503_retry"
                    )
                    time.sleep(retry_delay)
                    continue
                else:
                    # Log and break out of retry loop
                    print(f"Error for Group {group_id} after LLM call: {e}")
                    log_token_usage_unified(
                        date_str=date_str,
                        group_id=group_id,
                        model=model,
                        publisher=publisher,
                        prompt=prompt,
                        system_prompt=system_prompt,
                        error=str(e),
                        status="llm_error"
                    )
                    response = None
                    break

        if response is None:
            print(f"Skipping Group {group_id} due to LLM error.")
            continue
        # Now process the response
        try:
            response_content = response.choices[0].message.content
            response_tokens = None
            try:
                if hasattr(response, 'usage') and response.usage:
                    if hasattr(response.usage, 'completion_tokens'):
                        response_tokens = response.usage.completion_tokens
                    elif hasattr(response.usage, 'output_tokens'):
                        response_tokens = response.usage.output_tokens
            except Exception as e:
                print(f"Could not extract response tokens: {e}")

            # Log token usage for successful response
            log_token_usage_unified(
                date_str=date_str,
                group_id=group_id,
                model=model,
                publisher=publisher,
                prompt=prompt,
                system_prompt=system_prompt,
                response_content=response_content,
                response_tokens=response_tokens,
                status="success"
            )

            # Try to parse JSON
            try:
                article = json.loads(response_content)
                print(f"Successfully parsed JSON for Group {group_id}")
            except (json.JSONDecodeError, TypeError) as e:
                print(f"First JSON parse failed for Group {group_id}: {e}")
                # Try markdown code block
                try:
                    cleaned_content = response_content.strip()
                    if cleaned_content.startswith('```json'):
                        json_start = cleaned_content.find('{')
                        if cleaned_content.endswith('```'):
                            cleaned_content = cleaned_content[:-3].strip()
                        json_end = cleaned_content.rfind('}')
                        if json_start != -1 and json_end != -1 and json_end > json_start:
                            cleaned_content = cleaned_content[json_start:json_end + 1]
                            article = json.loads(cleaned_content)
                            print(f"Successfully parsed markdown-wrapped JSON for Group {group_id}")
                        else:
                            raise json.JSONDecodeError("No valid JSON found in markdown block", cleaned_content, 0)
                    else:
                        raise json.JSONDecodeError("Not a markdown block", cleaned_content, 0)
                except (json.JSONDecodeError, TypeError) as e2:
                    print(f"Second JSON parse (markdown) failed for Group {group_id}: {e2}")
                    try:
                        if not response_content:
                            print(f"Error for Group {group_id}: Empty response")
                            log_token_usage_unified(
                                date_str=date_str,
                                group_id=group_id,
                                model=model,
                                publisher=publisher,
                                prompt=prompt,
                                system_prompt=system_prompt,
                                response_content=response_content,
                                error="Empty response from LLM",
                                status="empty_response"
                            )
                            
                            # Save empty response info as txt file for reference
                            try:
                                output_dir = Path(f"data/output/article/{date_str}")
                                output_dir.mkdir(parents=True, exist_ok=True)
                                txt_file = output_dir / f"group_{group_id}_empty_response.txt"
                                with open(txt_file, 'w', encoding='utf-8') as f:
                                    f.write(f"Group {group_id} - Empty LLM Response\n")
                                    f.write(f"Model: {model}\n")
                                    f.write(f"Publisher: {publisher}\n")
                                    f.write(f"Date: {date_str}\n")
                                    f.write(f"Error: Empty response from LLM\n")
                                    f.write("="*80 + "\n\n")
                                    f.write("(No response content)")
                                print(f"Empty response info saved to: {txt_file}")
                            except Exception as save_error:
                                print(f"Warning: Could not save empty response info: {save_error}")
                            
                            print("Continuing to next group...")
                            continue
                        json_start = response_content.find('{')
                        json_end = response_content.rfind('}')
                        if json_start == -1 or json_end == -1 or json_end <= json_start:
                            print(f"Error for Group {group_id}: No valid JSON brackets found")
                            print(f"Response content: {response_content[:200]}...")
                            log_token_usage_unified(
                                date_str=date_str,
                                group_id=group_id,
                                model=model,
                                publisher=publisher,
                                prompt=prompt,
                                system_prompt=system_prompt,
                                response_content=response_content,
                                error="No valid JSON brackets found in response",
                                status="invalid_json_format"
                            )
                            
                            # Save raw response as txt file for reference
                            try:
                                output_dir = Path(f"data/output/article/{date_str}")
                                output_dir.mkdir(parents=True, exist_ok=True)
                                txt_file = output_dir / f"group_{group_id}_invalid_json_format.txt"
                                with open(txt_file, 'w', encoding='utf-8') as f:
                                    f.write(f"Group {group_id} - Invalid JSON Format\n")
                                    f.write(f"Model: {model}\n")
                                    f.write(f"Publisher: {publisher}\n")
                                    f.write(f"Date: {date_str}\n")
                                    f.write(f"Error: No valid JSON brackets found in response\n")
                                    f.write("="*80 + "\n\n")
                                    f.write(response_content)
                                print(f"Invalid format response saved to: {txt_file}")
                            except Exception as save_error:
                                print(f"Warning: Could not save invalid format response: {save_error}")
                            
                            print("Continuing to next group...")
                            continue
                        json_content = response_content[json_start:json_end + 1]
                        article = json.loads(json_content)
                        print(f"Successfully parsed extracted JSON for Group {group_id}")
                    except (json.JSONDecodeError, TypeError) as e3:
                        print(f"Error for Group {group_id}: Even extracted JSON failed to parse")
                        print(f"JSON error: {e3}")
                        print(f"Extracted content: {json_content[:200] if 'json_content' in locals() else 'N/A'}...")
                        log_token_usage_unified(
                            date_str=date_str,
                            group_id=group_id,
                            model=model,
                            publisher=publisher,
                            prompt=prompt,
                            system_prompt=system_prompt,
                            response_content=response_content,
                            error=f"JSON parsing failed: {str(e3)}",
                            status="json_parse_failed"
                        )
                        
                        # Save raw response as txt file for reference
                        try:
                            output_dir = Path(f"data/output/article/{date_str}")
                            output_dir.mkdir(parents=True, exist_ok=True)
                            txt_file = output_dir / f"group_{group_id}_raw_response.txt"
                            with open(txt_file, 'w', encoding='utf-8') as f:
                                f.write(f"Group {group_id} - Raw LLM Response (JSON Parse Failed)\n")
                                f.write(f"Model: {model}\n")
                                f.write(f"Publisher: {publisher}\n")
                                f.write(f"Date: {date_str}\n")
                                f.write(f"Error: {str(e3)}\n")
                                f.write("="*80 + "\n\n")
                                f.write(response_content)
                            print(f"Raw response saved to: {txt_file}")
                        except Exception as save_error:
                            print(f"Warning: Could not save raw response to txt file: {save_error}")
                        
                        print("Continuing to next group...")
                        continue
                    except Exception as e4:
                        print(f"Error for Group {group_id}: Unexpected error during JSON extraction")
                        print(f"Error: {e4}")
                        log_token_usage_unified(
                            date_str=date_str,
                            group_id=group_id,
                            model=model,
                            publisher=publisher,
                            prompt=prompt,
                            system_prompt=system_prompt,
                            response_content=response_content,
                            error=f"Unexpected error during JSON extraction: {str(e4)}",
                            status="json_extraction_error"
                        )
                        
                        # Save raw response as txt file for reference
                        try:
                            output_dir = Path(f"data/output/article/{date_str}")
                            output_dir.mkdir(parents=True, exist_ok=True)
                            txt_file = output_dir / f"group_{group_id}_extraction_error.txt"
                            with open(txt_file, 'w', encoding='utf-8') as f:
                                f.write(f"Group {group_id} - JSON Extraction Error\n")
                                f.write(f"Model: {model}\n")
                                f.write(f"Publisher: {publisher}\n")
                                f.write(f"Date: {date_str}\n")
                                f.write(f"Error: {str(e4)}\n")
                                f.write("="*80 + "\n\n")
                                f.write(response_content)
                            print(f"Extraction error response saved to: {txt_file}")
                        except Exception as save_error:
                            print(f"Warning: Could not save extraction error response: {save_error}")
                        
                        print("Continuing to next group...")
                        continue
            # If we get here, JSON parsing succeeded (first, second, or third attempt)
            print('saving...')
        except Exception as e:
            print(f"Error processing response for Group {group_id}: {e}")
            log_token_usage_unified(
                date_str=date_str,
                group_id=group_id,
                model=model,
                publisher=publisher,
                prompt=prompt,
                system_prompt=system_prompt,
                error=f"Error processing response: {str(e)}",
                status="response_processing_error"
            )
            
            # Save raw response as txt file for reference if response exists
            try:
                if 'response_content' in locals() and response_content:
                    output_dir = Path(f"data/output/article/{date_str}")
                    output_dir.mkdir(parents=True, exist_ok=True)
                    txt_file = output_dir / f"group_{group_id}_processing_error.txt"
                    with open(txt_file, 'w', encoding='utf-8') as f:
                        f.write(f"Group {group_id} - Response Processing Error\n")
                        f.write(f"Model: {model}\n")
                        f.write(f"Publisher: {publisher}\n")
                        f.write(f"Date: {date_str}\n")
                        f.write(f"Error: {str(e)}\n")
                        f.write("="*80 + "\n\n")
                        f.write(response_content)
                    print(f"Processing error response saved to: {txt_file}")
            except Exception as save_error:
                print(f"Warning: Could not save processing error response: {save_error}")
            
            print("Continuing to next group...")
            continue

        # Ensure output directory exists
        output_dir = Path(f"data/output/article/{date_str}")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / f"group_{group_id}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(article, f, indent=2, ensure_ascii=False)
        print(f"Article saved to: {output_file}")

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='Generate news articles from grouped data')
    parser.add_argument('--date', type=str, required=True, help='Date in YYYY-MM-DD format')
    parser.add_argument('--model', type=str, required=False, help='model name', default='qwen-plus')
    args = parser.parse_args()
    
    try:
        generate_article(args.date, args.model)
        print("Article generation completed!")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()