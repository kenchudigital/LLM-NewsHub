import json
import os
import subprocess

# Install the fundus package before running the main code
def install_fundus():
    subprocess.check_call([os.sys.executable, "-m", "pip", "install", "fundus"])

# Constant for file path
FILE_PATH = os.path.expanduser("~/airflow/data/data_articles.json")

# Function to read existing articles from the JSON file
def read_existing_articles(file_path):
    """
    Reads the existing articles from a JSON file.
    If the file does not exist or is empty, returns an empty list.
    """
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            try:
                existing_articles = [json.loads(line) for line in f if line.strip()]
                return existing_articles
            except json.JSONDecodeError:
                return []  # If file is empty or has an error, return an empty list
    return []

# Scrape and append articles to the JSON file
def scrape_and_append_articles():
    """
    Scrapes articles from The New Yorker using Fundus library,
    appends new articles to the existing JSON file.
    """
    # Initialize the crawler for The New Yorker
    from fundus import PublisherCollection, Crawler  # Import inside the function after install

    crawler = Crawler(PublisherCollection.us.TheNewYorker)
    articles = []
    
    # Crawl 3 articles and append them as JSON
    for article in crawler.crawl(max_articles=3):
        # Convert article to JSON format with specific fields
        article_json = article.to_json("title", "plaintext", "body", "lang", 'publishing_date', 'topics', 'images', "free_access")
        
        # Add additional metadata
        article_json['source'] = 'TheNewYorker'  # Add source to each article
        article_json['scraper'] = 'fundus'  # Add scraper type to each article
        
        # Append the article JSON to the articles list
        articles.append(article_json)

    # Read the existing articles from the file (if any)
    existing_articles = read_existing_articles(FILE_PATH)

    # Combine the existing articles with the new ones
    LIMIT = 100
    unchanged_articles = existing_articles[:-LIMIT] if len(existing_articles) > LIMIT else []
    recent_articles = list({json.dumps(article, sort_keys=True): article for article in existing_articles[-LIMIT:] + articles}.values())
    combined_articles = unchanged_articles + recent_articles

    # Save the combined articles back to the JSON file
    with open(FILE_PATH, "w") as f:
        json.dump(combined_articles, f, indent=4)

    print(f"Articles successfully scraped and appended. Total articles: {len(combined_articles)}")

# Run the function to test the scraping
if __name__ == "__main__":
    try:
        install_fundus()  # Install fundus first
        scrape_and_append_articles()  # Run the main scraping function
    except Exception as e:
        print(f"Error occurred: {e}")