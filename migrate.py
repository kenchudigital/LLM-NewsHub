#!/usr/bin/env python3
"""
Migration script to copy files from data/output to apps/static directories.

Usage:
    python migrate.py --date "2025-06-14"

This script will copy all files from:
- data/output/article/2025-06-14/ -> apps/static/articles/2025-06-14/
- data/output/audio/2025-06-14/ -> apps/static/audio/2025-06-14/
- data/output/video/2025-06-14/ -> apps/static/video/2025-06-14/
- data/output/image/2025-06-14/ -> apps/static/images/2025-06-14/
- data/output/resource/2025-06-14/ -> apps/static/resources/2025-06-14/
"""

import argparse
import os
import shutil
from pathlib import Path
import sys
from datetime import datetime


def validate_date(date_string):
    """Validate date format YYYY-MM-DD"""
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def create_directory_if_not_exists(path):
    """Create directory if it doesn't exist"""
    Path(path).mkdir(parents=True, exist_ok=True)
    print(f"Created directory: {path}")


def copy_files(source_dir, dest_dir, file_type):
    """Copy files from source to destination directory"""
    if not os.path.exists(source_dir):
        print(f"Source directory not found: {source_dir}")
        return 0
    
    if not os.listdir(source_dir):
        print(f"No files found in: {source_dir}")
        return 0
    
    # Create destination directory
    create_directory_if_not_exists(dest_dir)
    
    copied_count = 0
    for filename in os.listdir(source_dir):
        source_file = os.path.join(source_dir, filename)
        dest_file = os.path.join(dest_dir, filename)
        
        if os.path.isfile(source_file):
            try:
                shutil.copy2(source_file, dest_file)
                print(f"Copied {file_type}: {filename}")
                copied_count += 1
            except Exception as e:
                print(f"Error copying {filename}: {str(e)}")
        elif os.path.isdir(source_file):
            try:
                if os.path.exists(dest_file):
                    shutil.rmtree(dest_file)
                shutil.copytree(source_file, dest_file)
                print(f"✓ Copied {file_type} directory: {filename}")
                copied_count += 1
            except Exception as e:
                print(f"Error copying directory {filename}: {str(e)}")
    
    return copied_count


def copy_single_file(source_file, dest_file, file_type):
    """Copy a single file from source to destination"""
    if not os.path.exists(source_file):
        print(f"Source file not found: {source_file}")
        return 0
    
    # Create destination directory
    dest_dir = os.path.dirname(dest_file)
    create_directory_if_not_exists(dest_dir)
    
    try:
        shutil.copy2(source_file, dest_file)
        print(f"Copied {file_type}: {os.path.basename(source_file)}")
        return 1
    except Exception as e:
        print(f"Error copying {os.path.basename(source_file)}: {str(e)}")
        return 0


def main():
    parser = argparse.ArgumentParser(
        description="Migrate files from data/output to apps/static directories"
    )
    parser.add_argument(
        "--date", 
        required=True, 
        help="Date in YYYY-MM-DD format (e.g., 2025-06-14)"
    )
    parser.add_argument(
        "--dry-run", 
        action="store_true", 
        help="Show what would be copied without actually copying files"
    )
    
    args = parser.parse_args()
    
    # Validate date format
    if not validate_date(args.date):
        print("Error: Date must be in YYYY-MM-DD format")
        sys.exit(1)
    
    date = args.date
    print(f"Starting migration for date: {date}")
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - No files will be copied")
    
    # Define source and destination mappings
    migrations = [
        {
            'source': f'data/output/article/{date}',
            'dest': f'apps/static/articles/{date}',
            'type': 'articles'
        },
        {
            'source': f'data/output/audio/{date}',
            'dest': f'apps/static/audio/{date}',
            'type': 'audio files'
        },
        {
            'source': f'data/output/video/{date}',
            'dest': f'apps/static/video/{date}',
            'type': 'video files'
        },
        {
            'source': f'data/output/image/{date}',
            'dest': f'apps/static/images/{date}',
            'type': 'images'
        },
        {
            'source': f'data/output/resource/{date}',
            'dest': f'apps/static/resources/{date}',
            'type': 'resources'
        }
    ]

    # Add summary video migration
    summary_video_migration = {
        'source': 'deployment/summary/resource/summary.mp4',
        'dest': f'apps/static/summary-video/{date}/summary.mp4',
        'type': 'summary video'
    }
    migrations.append(summary_video_migration)
    
    total_copied = 0
    
    for migration in migrations:
        source_dir = migration['source']
        dest_dir = migration['dest']
        file_type = migration['type']
        
        print(f"\nProcessing {file_type}...")
        print(f"   From: {source_dir}")
        print(f"   To:   {dest_dir}")
        
        if args.dry_run:
            if os.path.exists(source_dir):
                file_count = len([f for f in os.listdir(source_dir) 
                                if os.path.isfile(os.path.join(source_dir, f))])
                dir_count = len([f for f in os.listdir(source_dir) 
                               if os.path.isdir(os.path.join(source_dir, f))])
                print(f"   Would copy: {file_count} files, {dir_count} directories")
            else:
                print(f"   Source directory not found")
        else:
            if file_type == 'summary video':
                copied = copy_single_file(
                    summary_video_migration['source'], 
                    summary_video_migration['dest'], 
                    summary_video_migration['type']
                )
            else:
                copied = copy_files(source_dir, dest_dir, file_type)
            total_copied += copied
    
    if args.dry_run:
        print(f"\nDRY RUN COMPLETE")
    else:
        print(f"\nMigration complete! Total items copied: {total_copied}")


if __name__ == "__main__":
    main()
