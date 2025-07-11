#!/usr/bin/env python3
"""
Simple progress monitor for IPD experiments
Works without special terminal libraries
"""

import json
import time
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

def draw_progress_bar(current, total, width=50):
    """Create ASCII progress bar"""
    if total == 0:
        return "[" + " " * width + "] 0.0%"
        
    filled = int(width * current / total)
    bar = "█" * filled + "░" * (width - filled)
    percentage = (current / total) * 100
    return f"[{bar}] {percentage:.1f}%"

def main():
    # Find progress file
    if len(sys.argv) > 1:
        progress_file = sys.argv[1]
    else:
        progress_file = find_latest_progress_file()
        
    if not progress_file or not os.path.exists(progress_file):
        print("Error: No progress file found!")
        print("Usage: python simple_monitor.py [path/to/progress.json]")
        sys.exit(1)
    
    print(f"Monitoring: {progress_file}")
    print("Press Ctrl+C to stop monitoring\n")
    
    start_time = None
    
    try:
        while True:
            try:
                with open(progress_file, 'r') as f:
                    progress = json.load(f)
                    
                # Clear screen (works on most terminals)
                print("\033[2J\033[H", end='')
                
                print("=" * 70)
                print("IPD EXPERIMENT PROGRESS MONITOR")
                print("=" * 70)
                
                # Calculate elapsed time
                if start_time is None and 'start_time' in progress:
                    start_time = datetime.fromisoformat(progress['start_time'])
                
                elapsed_time = 0
                if start_time:
                    elapsed_time = (datetime.now() - start_time).total_seconds()
                
                print(f"\nStarted: {progress.get('start_time', 'Unknown')}")
                print(f"Elapsed: {format_time(elapsed_time)}")
                print(f"Status: {progress.get('status', 'Running').upper()}")
                
                # Current condition
                print(f"\nCurrent Condition: {progress.get('current_condition', 'None')}")
                
                # Shadow conditions progress
                print("\nSHADOW CONDITIONS:")
                cond_current = progress.get('completed_conditions', 0)
                cond_total = progress.get('total_conditions', 0)
                print(f"{cond_current}/{cond_total} completed")
                print(draw_progress_bar(cond_current, cond_total))
                
                # Matches progress
                print("\nMATCHES:")
                match_current = progress.get('completed_matches', 0)
                match_total = progress.get('total_matches', 0)
                print(f"{match_current}/{match_total} completed")
                print(draw_progress_bar(match_current, match_total))
                
                # Speed and ETA
                if match_current > 0 and elapsed_time > 0:
                    speed = match_current / elapsed_time
                    remaining = match_total - match_current
                    eta = remaining / speed if speed > 0 else 0
                    print(f"\nSpeed: {speed:.2f} matches/second")
                    print(f"ETA: {format_time(eta)}")
                
                # Show estimated time from file if available
                if progress.get('estimated_time_remaining'):
                    print(f"File ETA: {progress['estimated_time_remaining']}")
                
                # Errors
                if progress.get('errors'):
                    print("\nERRORS:")
                    for error in progress['errors'][-3:]:
                        print(f"- {error}")
                
                # Check if complete
                if progress.get('status') == 'complete':
                    print("\n✅ EXPERIMENT COMPLETE!")
                    break
                    
            except Exception as e:
                print(f"Error reading progress: {e}")
            
            time.sleep(2)  # Update every 2 seconds
            
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped. Experiment continues in background.")

if __name__ == "__main__":
    main()