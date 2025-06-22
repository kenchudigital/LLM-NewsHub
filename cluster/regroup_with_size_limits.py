#!/usr/bin/env python3
"""
Script to re-process existing grouped data with size constraints.
This will split large groups and create a new group_result.csv file.
"""

import pandas as pd
import sys
import os
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from cluster.group_content import ContentGrouper

def regroup_existing_data(date_str, max_group_size=50):
    """Re-process existing grouped data with size constraints"""
    
    # Check if existing group data exists
    existing_group_file = f'data/group/{date_str}/group_result.csv'
    if not os.path.exists(existing_group_file):
        return False
    
    # Load existing group data
    existing_groups = pd.read_csv(existing_group_file)
    # Check if re-grouping is needed
    large_groups = existing_groups[existing_groups['size'] > max_group_size]
    if len(large_groups) == 0:
        return True
    # Initialize the grouper and load original data
    grouper = ContentGrouper(date_str)
    grouper.load_data()
    
    # Check if we have the raw data needed for re-clustering
    if grouper.events_df.empty and grouper.posts_df.empty:
        return False
    
    # Prepare content and create vectors
    grouper.prepare_content_for_grouping()
    grouper.create_content_vectors()
    
    # Perform initial clustering
    grouper.perform_clustering()
    
    # Create backup of existing results
    backup_file = f'data/group/{date_str}/group_result_backup.csv'
    existing_groups.to_csv(backup_file, index=False)
    
    # Save new results with size constraints
    new_summary = grouper.save_grouped_content(max_group_size)
    return True

def main():
    """Main execution"""
    parser = argparse.ArgumentParser(description='Re-process existing grouped data with size constraints')
    parser.add_argument('--date', type=str, required=True,
                       help='Date in YYYY-MM-DD format')
    parser.add_argument('--max-size', type=int, default=50,
                       help='Maximum group size (default: 50)')
    
    args = parser.parse_args()
    
    # Validate date format
    try:
        from datetime import datetime
        datetime.strptime(args.date, '%Y-%m-%d')
    except ValueError:
        sys.exit(1)
    
    try:
        success = regroup_existing_data(args.date, args.max_size)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 