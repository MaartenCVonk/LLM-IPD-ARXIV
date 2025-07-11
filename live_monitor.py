#!/usr/bin/env python3
"""
Live monitor that reads both progress.json and log files
Auto-refreshes every few seconds
"""

import json
import os
import re
import time
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

def parse_log_progress(log_file="full_experiment.log"):
    """Parse the log file for current match progress"""
    if not os.path.exists(log_file):
        return None, None
        
    try:
        # Read last 1000 bytes of file
        with open(log_file, 'rb') as f:
            f.seek(0, 2)  # Go to end
            file_size = f.tell()
            f.seek(max(0, file_size - 1000))
            tail = f.read().decode('utf-8', errors='ignore')
            
        # Find progress indicators
        matches = re.findall(r'Running matches:\s+\d+%.*?(\d+)/(\d+)', tail)
        if matches:
            current, total = matches[-1]
            return int(current), int(total)
            
    except Exception:
        pass
        
    return None, None

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

def clear_screen():
    """Clear the terminal screen"""
    os.system('clear' if os.name == 'posix' else 'cls')

def main():
    # Find progress file once
    progress_file = find_latest_progress_file()
    
    if not progress_file:
        print("No progress file found!")
        exit(1)
    
    print("IPD Experiment Monitor - Press Ctrl+C to exit")
    time.sleep(2)
    
    try:
        while True:
            clear_screen()
            
            try:
                with open(progress_file, 'r') as f:
                    progress = json.load(f)
                
                # Get tournament-level progress
                match_current = progress.get('completed_matches', 0)
                match_total = progress.get('total_matches', 0)
                
                # Get current match progress from log
                current_match, total_match = parse_log_progress()
                
                # Calculate elapsed time
                start_time = datetime.fromisoformat(progress['start_time'])
                elapsed = (datetime.now() - start_time).total_seconds()
                
                # Print header
                print("="*60)
                print("IPD EXPERIMENT LIVE MONITOR")
                print("="*60)
                
                # Print status
                print(f"\nExperiment: {progress.get('current_condition', 'N/A')}")
                print(f"Status: {progress.get('status', 'Running')}")
                print(f"Elapsed: {format_time(elapsed)}")
                
                # Show completed matches
                print(f"\nOVERALL PROGRESS:")
                print(f"Completed: {match_current}/{match_total} total matches ({match_current/match_total*100:.1f}%)")
                
                # Progress bar for overall
                if match_total > 0:
                    pct = match_current / match_total
                    bar_width = 50
                    filled = int(bar_width * pct)
                    bar = "█" * filled + "░" * (bar_width - filled)
                    print(f"[{bar}]")
                
                # Show current tournament progress
                if current_match is not None:
                    print(f"\nCURRENT TOURNAMENT:")
                    print(f"Progress: {current_match}/{total_match} matches ({current_match/total_match*100:.1f}%)")
                    
                    # Progress bar for current tournament
                    if total_match > 0:
                        pct = current_match / total_match
                        filled = int(bar_width * pct)
                        bar = "█" * filled + "░" * (bar_width - filled)
                        print(f"[{bar}]")
                    
                    # Estimate time remaining
                    print(f"\nTIME ESTIMATES:")
                    if current_match > 0:
                        # For current tournament
                        total_matches_so_far = match_current + current_match
                        if total_matches_so_far > 0:
                            avg_time_per_match = elapsed / total_matches_so_far
                            
                            remaining_in_tournament = (total_match - current_match) * avg_time_per_match
                            print(f"Current tournament ETA: {format_time(remaining_in_tournament)}")
                            
                            # For entire experiment
                            total_remaining = (match_total - match_current - current_match) * avg_time_per_match
                            print(f"Full experiment ETA: {format_time(total_remaining)}")
                            
                            # Show speed
                            print(f"\nSpeed: {1/avg_time_per_match:.2f} matches/min")
                
                # Show any errors
                if progress.get('errors'):
                    print(f"\nERRORS: {len(progress['errors'])}")
                    for error in progress['errors'][-3:]:
                        print(f"  - {error}")
                
                # Check if complete
                if progress.get('status') == 'complete':
                    print("\n✅ EXPERIMENT COMPLETE!")
                    break
                    
            except Exception as e:
                print(f"Error reading data: {e}")
            
            # Refresh every 5 seconds
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\n\nMonitor stopped. Experiment continues in background.")

if __name__ == "__main__":
    main()