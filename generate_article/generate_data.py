import pandas as pd
import ast
from pathlib import Path
import sys
from datetime import datetime
import argparse

class DataGenerator:
    def __init__(self, date_str=None):
        self.project_root = Path(__file__).parent.parent
        if date_str is None:
            date_str = datetime.now().strftime('%Y-%m-%d')
        self.date = date_str
        self.output_dir = self.project_root / 'data' / 'group' / self.date
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Source data paths
        self.event_source = self.project_root / 'data' / 'card' / 'event_card' / f'{self.date}.csv'
        self.post_source = self.project_root / 'data' / 'card' / 'statement_card' / 'posts' / f'{self.date}.csv'
        self.comment_source = self.project_root / 'data' / 'card' / 'statement_card' / 'comments' / f'{self.date}.csv'
        self.fundus_dir = self.project_root / 'data' / 'raw' / 'fundus' / self.date

    def load_group_data(self):
        """Load the group data that contains event and post IDs."""
        group_file = self.output_dir / 'group_result.csv'
        if not group_file.exists():
            raise FileNotFoundError(f"Group data file not found: {group_file}")
        
        df = pd.read_csv(group_file)
        if df.empty:
            raise ValueError("Group data file is empty")
        
        # Get the first group's event and post IDs
        first_group = df.iloc[0]
        event_ids = ast.literal_eval(first_group['event_ids'])
        post_ids = ast.literal_eval(first_group['post_ids'])
        
        print(f"Found {len(event_ids)} event IDs and {len(post_ids)} post IDs in group data")
        return event_ids, post_ids

    def get_events(self, event_ids):
        """Get events from the source file."""
        if not self.event_source.exists():
            raise FileNotFoundError(f"Event source file not found: {self.event_source}")
        
        df = pd.read_csv(self.event_source)
        events = df[df['event_id'].isin(event_ids)]
        print(f"Found {len(events)} events out of {len(event_ids)} requested")
        return events

    def get_posts(self, post_ids):
        """Get posts from the source file."""
        if not self.post_source.exists():
            raise FileNotFoundError(f"Post source file not found: {self.post_source}")
        
        df = pd.read_csv(self.post_source)
        posts = df[df['post_id'].isin(post_ids)]
        print(f"Found {len(posts)} posts out of {len(post_ids)} requested")
        return posts

    def get_comments(self, post_ids):
        """Get comments from the source file."""
        if not self.comment_source.exists():
            raise FileNotFoundError(f"Comment source file not found: {self.comment_source}")
        
        df = pd.read_csv(self.comment_source)
        comments = df[df['post_id'].isin(post_ids)]
        print(f"Found {len(comments)} comments for the requested posts")
        return comments

    def get_articles(self, event_df):
        """Get articles from the fundus directory."""
        if not self.fundus_dir.exists():
            raise FileNotFoundError(f"Fundus directory not found: {self.fundus_dir}")
        
        # Get unique URLs from events
        urls = event_df['link'].unique()
        
        # Find and read all CSV files in the fundus directory
        dfs = []
        for file in self.fundus_dir.glob('*.csv'):
            try:
                df = pd.read_csv(file)
                dfs.append(df)
            except Exception as e:
                print(f"Error reading {file}: {e}")
                continue
        
        if not dfs:
            print("No article data found")
            return pd.DataFrame()
        
        # Combine all dataframes and filter by URLs
        combined_df = pd.concat(dfs, ignore_index=True)
        articles = combined_df[combined_df['link'].isin(urls)]
        print(f"Found {len(articles)} articles for the event URLs")
        return articles

    def generate_files(self):
        """Generate all required data files."""
        try:
            # Load group data to get event and post IDs
            event_ids, post_ids = self.load_group_data()
            
            # Get data from source files
            events_df = self.get_events(event_ids)
            posts_df = self.get_posts(post_ids)
            comments_df = self.get_comments(post_ids)
            articles_df = self.get_articles(events_df)
            
            # Save the data files
            events_df.to_csv(self.output_dir / 'events_df.csv', index=False)
            posts_df.to_csv(self.output_dir / 'posts_df.csv', index=False)
            comments_df.to_csv(self.output_dir / 'comments_df.csv', index=False)
            if not articles_df.empty:
                articles_df.to_csv(self.output_dir / 'articles_df.csv', index=False)
            
            print(f"\nGenerated files in {self.output_dir}:")
            print(f"- events_df.csv: {len(events_df)} events")
            print(f"- posts_df.csv: {len(posts_df)} posts")
            print(f"- comments_df.csv: {len(comments_df)} comments")
            if not articles_df.empty:
                print(f"- articles_df.csv: {len(articles_df)} articles")
            
        except Exception as e:
            print(f"Error generating data files: {e}", file=sys.stderr)
            raise

def main():
    parser = argparse.ArgumentParser(description='Generate data files for article generation')
    parser.add_argument('--date', type=str, help='Date in YYYY-MM-DD format')
    args = parser.parse_args()
    
    try:
        generator = DataGenerator(args.date)
        generator.generate_files()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main() 