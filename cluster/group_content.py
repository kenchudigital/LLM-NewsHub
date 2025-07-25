import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from datetime import datetime
import os
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns

class ContentGrouper:
    def __init__(self, date):
        self.date = date
        self.content_df = None
        self.tfidf_matrix = None
        self.tfidf_vectorizer = None
        self.cluster_analysis = {}
        self.optimal_clusters = None
        self.performance_results = {}
        
    def load_data(self):
        """Load data from card directories for the specified date"""
        print(f"Loading data for date: {self.date}")
        
        # Load event cards
        event_path = f'data/card/event_card/{self.date}.csv'
        if os.path.exists(event_path):
            self.events_df = pd.read_csv(event_path)
            print(f"Loaded {len(self.events_df)} events")
        else:
            print(f"No event data found for {self.date}")
            self.events_df = pd.DataFrame()
            
        # Load statement cards (posts only)
        posts_path = f'data/card/statement_card/posts/{self.date}.csv'
        
        if os.path.exists(posts_path):
            self.posts_df = pd.read_csv(posts_path)
            print(f"Loaded {len(self.posts_df)} posts")
        else:
            print(f"No post data found for {self.date}")
            self.posts_df = pd.DataFrame()
    
    def prepare_content_for_grouping(self):
        """Prepare and combine content from events and posts only"""
        print("Preparing content for grouping...")
        
        content_data = []
        
        # Process events
        if not self.events_df.empty:
            for idx, row in self.events_df.iterrows():
                try:
                    event_id = row.get('event_id', f'event_{idx}')
                    description = str(row.get('event_description', ''))
                    statement = str(row.get('statement_or_comment', ''))
                    combined_text = f"{description} {statement}".strip()
                    
                    if not combined_text:
                        continue
                        
                    content_data.append({
                        'content_id': event_id,
                        'type': 'event',
                        'content': combined_text,
                        'source': 'event_card'
                    })
                except Exception as e:
                    print(f"Warning: Error processing event {idx}: {e}")
                    continue
        
        # Process posts
        if not self.posts_df.empty:
            for idx, row in self.posts_df.iterrows():
                try:
                    post_id = row.get('post_id', f'post_{idx}')
                    title = str(row.get('title', ''))
                    content = str(row.get('content', ''))
                    combined_text = f"{title} {content}".strip()
                    
                    if not combined_text:
                        continue
                        
                    content_data.append({
                        'content_id': post_id,
                        'type': 'post',
                        'content': combined_text,
                        'source': 'statement_card'
                    })
                except Exception as e:
                    print(f"Warning: Error processing post {idx}: {e}")
                    continue
        
        self.content_df = pd.DataFrame(content_data)
        return self.content_df
    
    def create_content_vectors(self):
        """Create TF-IDF vectors for content"""
        print("Creating content vectors...")
        
        if self.content_df is None or len(self.content_df) == 0:
            print("No content to vectorize!")
            return None
            
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(self.content_df['content'])
        return self.tfidf_matrix
    
    def evaluate_clustering_performance(self, kmeans_model, tfidf_matrix, n_clusters):
        """Evaluate clustering performance using multiple metrics"""
        try:
            cluster_labels = kmeans_model.labels_

            silhouette_avg = silhouette_score(tfidf_matrix, cluster_labels)
            
            inertia = kmeans_model.inertia_
            
            inertia_per_sample = inertia / tfidf_matrix.shape[0]
            
            unique_labels, counts = np.unique(cluster_labels, return_counts=True)
            size_variance = np.var(counts)  # Lower variance means more balanced clusters
            
            # Calculate a combined score (higher is better)
            # We want high silhouette, low inertia, and balanced cluster sizes - TODO: use better way !
            combined_score = silhouette_avg - (inertia_per_sample / 1000) - (size_variance / 1000)
            
            return {
                'silhouette_score': silhouette_avg,
                'inertia': inertia,
                'inertia_per_sample': inertia_per_sample,
                'size_variance': size_variance,
                'combined_score': combined_score,
                'cluster_sizes': counts.tolist()
            }
        except Exception as e:
            print(f"Error evaluating clustering for n_clusters={n_clusters}: {e}")
            return None
    
    def plot_clustering_performance(self, performance_results):
        """Plot clustering performance metrics"""
        if not performance_results:
            print("No performance results to plot")
            return
            
        n_clusters_list = list(performance_results.keys())
        
        # Create subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle(f'Clustering Performance Analysis for {self.date}', fontsize=16)
        
        # Plot 1: Silhouette Score
        silhouette_scores = [performance_results[n]['silhouette_score'] for n in n_clusters_list]
        axes[0, 0].plot(n_clusters_list, silhouette_scores, 'bo-', linewidth=2, markersize=8)
        axes[0, 0].set_xlabel('Number of Clusters')
        axes[0, 0].set_ylabel('Silhouette Score')
        axes[0, 0].set_title('Silhouette Score vs Number of Clusters')
        axes[0, 0].grid(True, alpha=0.3)
        
        # Plot 2: Inertia
        inertias = [performance_results[n]['inertia'] for n in n_clusters_list]
        axes[0, 1].plot(n_clusters_list, inertias, 'ro-', linewidth=2, markersize=8)
        axes[0, 1].set_xlabel('Number of Clusters')
        axes[0, 1].set_ylabel('Inertia')
        axes[0, 1].set_title('Inertia vs Number of Clusters')
        axes[0, 1].grid(True, alpha=0.3)
        
        # Plot 3: Combined Score
        combined_scores = [performance_results[n]['combined_score'] for n in n_clusters_list]
        axes[1, 0].plot(n_clusters_list, combined_scores, 'go-', linewidth=2, markersize=8)
        axes[1, 0].set_xlabel('Number of Clusters')
        axes[1, 0].set_ylabel('Combined Score')
        axes[1, 0].set_title('Combined Score vs Number of Clusters')
        axes[1, 0].grid(True, alpha=0.3)
        
        # Plot 4: Cluster Size Variance
        size_variances = [performance_results[n]['size_variance'] for n in n_clusters_list]
        axes[1, 1].plot(n_clusters_list, size_variances, 'mo-', linewidth=2, markersize=8)
        axes[1, 1].set_xlabel('Number of Clusters')
        axes[1, 1].set_ylabel('Cluster Size Variance')
        axes[1, 1].set_title('Cluster Size Variance vs Number of Clusters')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save the plot
        output_dir = Path(f'data/group/{self.date}')
        output_dir.mkdir(parents=True, exist_ok=True)
        plot_path = output_dir / 'clustering_performance_analysis.png'
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        print(f"Performance analysis plot saved to {plot_path}")
        
        # Show the plot
        plt.show()
    
    def perform_clustering(self, n_clusters=None, test_range=None):
        """Perform clustering on content with performance evaluation"""
        print("Performing clustering with performance evaluation...")
        
        if len(self.content_df) < 2:
            print("Not enough content for clustering!")
            self.content_df['group_id'] = 0
            return self.content_df['group_id']
        
        # Determine the range of n_clusters to test
        if test_range is None:
            # Get minimum clusters based on publisher diversity
            try:
                fundus_file = f'data/raw/fundus/{self.date}/{self.date}.csv'
                fundus_df = pd.read_csv(fundus_file)
                unique_publishers = len(fundus_df['publisher'].unique())
                min_clusters = max(5, unique_publishers)
            except Exception as e:
                print(f"Warning: Could not read fundus data: {e}")
                min_clusters = 5  # Default fallback
            
            # Set range for testing
            max_clusters = min(65, len(fundus_df)//3)  # Don't exceed half the data size
            test_range = range(min_clusters, max_clusters + 1)
        
        print(f"Testing n_clusters range: {list(test_range)}")
        
        # Test different numbers of clusters
        performance_results = {}
        
        for n_clusters in test_range:
            print(f"Testing n_clusters = {n_clusters}")
            
            try:
                # Perform clustering
                kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
                clusters = kmeans.fit_predict(self.tfidf_matrix)
                
                # Evaluate performance
                performance = self.evaluate_clustering_performance(kmeans, self.tfidf_matrix, n_clusters)
                
                if performance:
                    performance_results[n_clusters] = performance
                    print(f"  Silhouette: {performance['silhouette_score']:.4f}, "
                          f"Inertia: {performance['inertia']:.2f}, "
                          f"Combined Score: {performance['combined_score']:.4f}")
                else:
                    print(f"  Failed to evaluate performance for n_clusters={n_clusters}")
                    
            except Exception as e:
                print(f"  Error with n_clusters={n_clusters}: {e}")
                continue
        
        # After collecting performance_results for all n_clusters
        silhouette_scores = [performance_results[n]['silhouette_score'] for n in sorted(performance_results)]
        n_clusters_list = sorted(performance_results)

        # Calculate slopes (differences)
        slopes = [silhouette_scores[i+1] - silhouette_scores[i] for i in range(len(silhouette_scores)-1)]

        # Set a threshold for minimal improvement
        threshold = 0.00006 # You can adjust this

        # Find the first n where the slope is less than the threshold
        optimal_n = n_clusters_list[-1]  # Default to last if no plateau found
        for i, slope in enumerate(slopes):
            if abs(slope) < threshold:
                print(f'slope: {slope}')
                optimal_n = n_clusters_list[i]
                print(f"Plateau detected at n_clusters={optimal_n} (slope={slope:.4f})")
                break

        print(f"Selected n_clusters based on silhouette plateau: {optimal_n}")

        # Find optimal number of clusters
        if performance_results:
            # Use combined score to find the best n_clusters
            # best_n_clusters = max(performance_results.keys(), 
            #                     key=lambda x: performance_results[x]['combined_score'])
            
            best_n_clusters = optimal_n
            # print(f"\nOptimal n_clusters found: {best_n_clusters}")
            # print(f"Best combined score: {performance_results[best_n_clusters]['combined_score']:.4f}")
            
            # Plot performance analysis
            self.plot_clustering_performance(performance_results)
            
            # Save performance results
            self.performance_results = performance_results
            self.optimal_clusters = best_n_clusters
            
            # Perform final clustering with optimal n_clusters
            self.kmeans = KMeans(n_clusters=best_n_clusters, random_state=42, n_init=10)
            final_clusters = self.kmeans.fit_predict(self.tfidf_matrix)
            
            # Assign group IDs (starting from 1)
            self.content_df['group_id'] = final_clusters + 1
            
            return self.content_df['group_id']
        else:
            print("No valid clustering results found!")
            return None
    
    def split_large_groups(self, max_group_size=20):
        """Split groups that are too large into smaller subgroups"""
        print(f"Checking for groups larger than {max_group_size}...")
        
        new_groups = []
        max_group_id = self.content_df['group_id'].max()
        next_group_id = max_group_id + 1
        
        for group_id in sorted(self.content_df['group_id'].unique()):
            group_data = self.content_df[self.content_df['group_id'] == group_id]
            
            if len(group_data) <= max_group_size:
                # Keep normal-sized groups as is
                new_groups.append(group_data)
            else:
                # Split large group into smaller subgroups
                print(f"Splitting large group {group_id} (size: {len(group_data)}) into smaller groups")
                
                # Calculate number of subgroups needed
                n_subgroups = (len(group_data) + max_group_size - 1) // max_group_size
                
                # Use additional clustering for the large group
                if len(group_data) > 1:
                    # Get the content for this group
                    group_indices = group_data.index
                    group_tfidf = self.tfidf_matrix[group_indices]
                    
                    # Perform sub-clustering
                    subgroup_kmeans = KMeans(n_clusters=n_subgroups, random_state=42, n_init=10)
                    sub_clusters = subgroup_kmeans.fit_predict(group_tfidf)
                    
                    # Assign new group IDs to subgroups
                    for sub_cluster_id in range(n_subgroups):
                        sub_mask = sub_clusters == sub_cluster_id
                        sub_indices = group_indices[sub_mask]
                        
                        if len(sub_indices) > 0:
                            subgroup_data = group_data.loc[sub_indices].copy()
                            subgroup_data['group_id'] = next_group_id
                            new_groups.append(subgroup_data)
                            print(f"  → Created subgroup {next_group_id} with size {len(subgroup_data)}")
                            next_group_id += 1
        
        # Combine all groups back together
        if new_groups:
            self.content_df = pd.concat(new_groups, ignore_index=True)
            print(f"Group splitting complete. New total groups: {len(self.content_df['group_id'].unique())}")
        
        return self.content_df

    def save_grouped_content(self, max_group_size=50):
        """Save grouped content to output directory with size constraints"""
        
        # Split large groups first
        self.split_large_groups(max_group_size)
        
        output_dir = Path(f'data/group/{self.date}')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create a summary of groups
        group_summary = []
        rejected_groups = 0
        large_groups_split = 0
        
        for group_id in sorted(self.content_df['group_id'].unique()):
            group_data = self.content_df[self.content_df['group_id'] == group_id]
            
            # Get content IDs by type (only events and posts)
            events = group_data[group_data['type'] == 'event']['content_id'].tolist()
            posts = group_data[group_data['type'] == 'post']['content_id'].tolist()
            
            # Reject groups with no event_ids
            if not events:  # If events list is empty
                print(f"Rejecting group {group_id}: No event_ids found")
                rejected_groups += 1
                continue
            
            # Double-check group size (should be handled by split_large_groups)
            if len(group_data) > max_group_size:
                print(f"Warning: Group {group_id} still too large (size: {len(group_data)})")
            
            group_summary.append({
                'group_id': group_id,
                'size': len(group_data),
                'event_ids': events,
                'post_ids': posts
            })
        
        # Save group results
        summary_df = pd.DataFrame(group_summary)
        result_file = output_dir / 'group_result.csv'
        summary_df.to_csv(result_file, index=False)
        print(f"Saved group results to {result_file}")
        
        # Save performance results
        if self.performance_results:
            performance_file = output_dir / 'clustering_performance.json'
            import json
            # Convert numpy types to native Python types for JSON serialization
            performance_data = {}
            for n_clusters, metrics in self.performance_results.items():
                performance_data[n_clusters] = {
                    'silhouette_score': float(metrics['silhouette_score']),
                    'inertia': float(metrics['inertia']),
                    'inertia_per_sample': float(metrics['inertia_per_sample']),
                    'size_variance': float(metrics['size_variance']),
                    'combined_score': float(metrics['combined_score']),
                    'cluster_sizes': [int(x) for x in metrics['cluster_sizes']]
                }
            
            with open(performance_file, 'w') as f:
                json.dump(performance_data, f, indent=2)
            print(f"Saved performance results to {performance_file}")
        
        return summary_df

def main(date_str, max_group_size=None, test_range=None):
    """Main execution function"""
    
    # Use centralized configuration if not specified
    if max_group_size is None:
        max_group_size = 50
    
    print(f"Content Grouping System for {date_str}")
    print(f"Max group size: {max_group_size}")
    if test_range:
        print(f"Testing n_clusters range: {list(test_range)}")
    print("="*60)
    
    # Initialize the grouper
    grouper = ContentGrouper(date_str)
    
    # Load and process data
    grouper.load_data()
    grouper.prepare_content_for_grouping()
    
    # Create vectors and perform clustering with performance evaluation
    grouper.create_content_vectors()
    grouper.perform_clustering(test_range=test_range)
    
    # Save results with size constraints
    summary = grouper.save_grouped_content(max_group_size)
    
    print("\nGrouping complete!")
    print(f"Results saved to data/group/{date_str}/")
    print(f"Created {len(summary)} groups")
    if grouper.optimal_clusters:
        print(f"Optimal number of clusters: {grouper.optimal_clusters}")
    
    return summary

if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description='Group content by date with size constraints')
    parser.add_argument('--date', help='Date in YYYY-MM-DD format')
    parser.add_argument('--max-size', type=int, default=50, 
                       help='Maximum group size (default: 50)')
    parser.add_argument('--min-clusters', type=int, default=None,
                       help='Minimum number of clusters to test')
    parser.add_argument('--max-clusters', type=int, default=None,
                       help='Maximum number of clusters to test')
    
    args = parser.parse_args()
    
    try:
        # Validate date format
        datetime.strptime(args.date, '%Y-%m-%d')
        
        # Set test range if specified
        test_range = None
        if args.min_clusters is not None and args.max_clusters is not None:
            test_range = range(args.min_clusters, args.max_clusters + 1)
        
        main(args.date, args.max_size, test_range)
    except ValueError:
        print("Error: Date must be in YYYY-MM-DD format")
        sys.exit(1)

# printing to see something !
# df = pd.read_csv('data/raw/fundus/2025-06-21/2025-06-21.csv')
# unique_publishers = df['publisher'].nunique()
# print(f"Unique publishers: {unique_publishers}")
# publishers = df['publisher'].unique()
# print(f"Publisher list: {list(publishers)}")
# publisher_counts = df['publisher'].value_counts()
# print(f"Publisher counts:\n{publisher_counts}")