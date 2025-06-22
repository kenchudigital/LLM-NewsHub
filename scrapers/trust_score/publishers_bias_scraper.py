"""
Usage: python  scrapers/trust_score/publishers_bias_scraper.py

Input: None

Output: data/raw/trust_score/publishers_bias.csv
"""
import sys
sys.path.append('../..')

import pandas as pd
import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv

def load_environment():
    load_dotenv()
    rapid_api_key = os.getenv("RAPID_API_KEY")
    return rapid_api_key

def fetch_bias_data(api_key):
    url = "https://media-bias-fact-check-ratings-api2.p.rapidapi.com/fetch-data"
    
    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "media-bias-fact-check-ratings-api2.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers)    
    if response.status_code != 200:
        raise Exception(f"API request failed with status code: {response.status_code}")
    
    text = response.text
    if text.startswith('\ufeff'):
        text = text.encode('utf-8').decode('utf-8-sig')
    
    data = json.loads(text)
    return data


def process_bias_data(data):
    df = pd.DataFrame(data)
    df['data_extracted_at'] = datetime.now().isoformat()
    if 'Unnamed: 9' in df.columns:
        df = df.drop('Unnamed: 9', axis=1)
    if 'Credibility' in df.columns:
        df['Credibility'] = df['Credibility'].str.title()
    return df

def save_data(df, filename='data/raw/trust_score/publishers_bias.csv'):
    """Save DataFrame to CSV file"""
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")

def test_news_url(url: str, df='data/raw/trust_score/publishers_bias.csv'):
    df = ''
    matches = df[df['Source URL'] == url]
    if not matches.empty:
        match = matches.iloc[0]
        return {
            'found': True,
            'source': match['Source'],
            'bias': match['Bias'],
            'factual_reporting': match['Factual Reporting'],
            'credibility': match['Credibility'],
            'country': match['Country']
        }
    else:
        return {'found': False, 'url': url}

def main():
    """Main function to run the bias data scraper"""
    api_key = load_environment()
    raw_data = fetch_bias_data(api_key)   
    df = process_bias_data(raw_data)
    save_data(df)

if __name__ == "__main__":
    main()