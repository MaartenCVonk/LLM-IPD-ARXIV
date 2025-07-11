#!/usr/bin/env python3
"""
Quick one-line status check for IPD experiments
"""

import json
import os
import sys
from datetime import datetime

def find_latest_progress_file(results_dir="results"):
    """Find the most recent progress file"""
    latest_time = 0
    latest_file = None
    
    for root, dirs, files in os.walk(results_dir):
        for file in files:
            if file == "progress.json":
                filepath = os.path.join(root, file)
                mtime = os.path.getmtime(filepath)
                if mtime > latest_time:
                    latest_time = mtime
                    latest_file = filepath
    
    return latest_file

def format_time(seconds):
    """Format seconds into readable time"""
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        return f"{int(seconds/60)}m {int(seconds%60)}s"
    else:
        hours = int(seconds/3600)
        minutes = int((seconds%3600)/60)
        return f"{hours}h {minutes}m"

# Find progress file
progress_file = find_latest_progress_file()

if not progress_file:
    print("No progress file found!")
    sys.exit(1)

try:
    with open(progress_file, 'r') as f:
        progress = json.load(f)
    
    # Calculate progress
    match_current = progress.get('completed_matches', 0)
    match_total = progress.get('total_matches', 0)
    pct = (match_current / match_total * 100) if match_total > 0 else 0
    
    # Calculate elapsed time
    start_time = datetime.fromisoformat(progress['start_time'])
    elapsed = (datetime.now() - start_time).total_seconds()
    
    # Calculate ETA
    if match_current > 0:
        rate = match_current / elapsed
        remaining = (match_total - match_current) / rate if rate > 0 else 0
        eta_str = format_time(remaining)
    else:
        eta_str = "calculating..."
    
    # Print status
    print(f"Progress: {match_current}/{match_total} matches ({pct:.1f}%) | "
          f"Elapsed: {format_time(elapsed)} | ETA: {eta_str} | "
          f"Condition: {progress.get('current_condition', 'N/A')}")
    
except Exception as e:
    print(f"Error: {e}")