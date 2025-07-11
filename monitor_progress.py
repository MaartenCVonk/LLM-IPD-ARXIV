#!/usr/bin/env python3
"""
Visual progress monitor for IPD experiments
Run this in a separate terminal to monitor experiment progress in real-time
"""

import json
import time
import os
import sys
from datetime import datetime
from blessed import Terminal
import asciichartpy
from collections import deque
import argparse


class ExperimentMonitor:
    def __init__(self, progress_file: str, refresh_rate: float = 1.0):
        self.progress_file = progress_file
        self.refresh_rate = refresh_rate
        self.term = Terminal()
        
        # Data tracking
        self.completion_history = deque(maxlen=50)
        self.time_history = deque(maxlen=50)
        self.start_time = None
        
    def read_progress(self):
        """Read current progress from file"""
        try:
            with open(self.progress_file, 'r') as f:
                return json.load(f)
        except:
            return None
            
    def format_time(self, seconds):
        """Format seconds into readable time"""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            return f"{int(seconds/60)}m {int(seconds%60)}s"
        else:
            hours = int(seconds/3600)
            minutes = int((seconds%3600)/60)
            return f"{hours}h {minutes}m"
    
    def draw_progress_bar(self, current, total, width=50):
        """Create ASCII progress bar"""
        if total == 0:
            return "[" + " " * width + "]"
            
        filled = int(width * current / total)
        bar = "█" * filled + "░" * (width - filled)
        percentage = (current / total) * 100
        return f"[{bar}] {percentage:.1f}%"
    
    def draw_chart(self, data, height=10, width=60):
        """Create ASCII line chart"""
        if len(data) < 2:
            return "Waiting for data..."
            
        # Normalize data to fit height
        chart_data = list(data)
        
        try:
            chart = asciichartpy.plot(
                chart_data,
                {"height": height, "width": width}
            )
            return chart
        except:
            return "Chart error"
    
    def run(self):
        """Main monitor loop"""
        print(self.term.clear())
        
        while True:
            progress = self.read_progress()
            
            if progress is None:
                print(self.term.home + self.term.clear)
                print(self.term.bold("IPD EXPERIMENT MONITOR"))
                print("\nWaiting for experiment to start...")
                print(f"\nMonitoring: {self.progress_file}")
                time.sleep(self.refresh_rate)
                continue
            
            # Calculate metrics
            if self.start_time is None and 'start_time' in progress:
                self.start_time = datetime.fromisoformat(progress['start_time'])
            
            elapsed_time = 0
            if self.start_time:
                elapsed_time = (datetime.now() - self.start_time).total_seconds()
            
            # Track completion rate
            if progress.get('total_matches', 0) > 0:
                completion_pct = (progress.get('completed_matches', 0) / 
                                progress['total_matches']) * 100
                self.completion_history.append(completion_pct)
                self.time_history.append(elapsed_time / 60)  # Convert to minutes
            
            # Clear screen and draw interface
            print(self.term.home + self.term.clear)
            
            # Header
            print(self.term.bold("IPD EXPERIMENT MONITOR"))
            print("=" * 70)
            
            # Status
            status = progress.get('status', 'running')
            status_color = self.term.green if status == 'complete' else self.term.yellow
            print(f"Status: {status_color(status.upper())}")
            print(f"Started: {progress.get('start_time', 'Unknown')}")
            print(f"Elapsed: {self.format_time(elapsed_time)}")
            
            # Current condition
            print(f"\nCurrent Condition: {self.term.cyan(progress.get('current_condition', 'None'))}")
            
            # Progress bars
            print("\n" + self.term.bold("PROGRESS"))
            
            # Conditions progress
            cond_current = progress.get('completed_conditions', 0)
            cond_total = progress.get('total_conditions', 0)
            print(f"Conditions: {cond_current}/{cond_total}")
            print(self.draw_progress_bar(cond_current, cond_total))
            
            # Matches progress
            match_current = progress.get('completed_matches', 0)
            match_total = progress.get('total_matches', 0)
            print(f"\nMatches: {match_current}/{match_total}")
            print(self.draw_progress_bar(match_current, match_total))
            
            # Time estimate
            if progress.get('estimated_time_remaining'):
                print(f"\nEstimated time remaining: {self.term.magenta(progress['estimated_time_remaining'])}")
            
            # Completion chart
            if len(self.completion_history) > 1:
                print("\n" + self.term.bold("COMPLETION RATE (%)"))
                print(self.draw_chart(self.completion_history, height=8, width=60))
            
            # Errors
            if progress.get('errors'):
                print("\n" + self.term.bold_red("ERRORS"))
                for error in progress['errors'][-5:]:  # Show last 5 errors
                    print(f"- {error}")
            
            # Instructions
            print("\n" + "-" * 70)
            print("Press Ctrl+C to exit monitor (experiment will continue)")
            
            # Completion message
            if status == 'complete':
                print("\n" + self.term.bold_green("🎉 EXPERIMENT COMPLETE! 🎉"))
                break
            
            time.sleep(self.refresh_rate)
    
    def run_compact(self):
        """Compact monitoring mode"""
        while True:
            progress = self.read_progress()
            
            if progress is None:
                print("\rWaiting for experiment...", end='', flush=True)
                time.sleep(self.refresh_rate)
                continue
            
            # Calculate metrics
            match_current = progress.get('completed_matches', 0)
            match_total = progress.get('total_matches', 0)
            
            if match_total > 0:
                pct = (match_current / match_total) * 100
                bar = self.draw_progress_bar(match_current, match_total, width=30)
                
                status_line = f"\rProgress: {bar} | " \
                            f"Matches: {match_current}/{match_total} | " \
                            f"Condition: {progress.get('current_condition', 'N/A')} | " \
                            f"ETA: {progress.get('estimated_time_remaining', 'N/A')}"
                
                print(status_line, end='', flush=True)
                
                if progress.get('status') == 'complete':
                    print("\n✓ Complete!")
                    break
            
            time.sleep(self.refresh_rate)


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


def main():
    parser = argparse.ArgumentParser(description="Monitor IPD experiment progress")
    parser.add_argument("--file", type=str, help="Path to progress.json file")
    parser.add_argument("--compact", action="store_true", 
                       help="Use compact single-line display")
    parser.add_argument("--refresh", type=float, default=1.0,
                       help="Refresh rate in seconds")
    
    args = parser.parse_args()
    
    # Find progress file
    if args.file:
        progress_file = args.file
    else:
        progress_file = find_latest_progress_file()
        
    if not progress_file or not os.path.exists(progress_file):
        print("Error: No progress file found!")
        print("Either specify with --file or run an experiment first.")
        sys.exit(1)
    
    print(f"Monitoring: {progress_file}")
    
    # Create and run monitor
    monitor = ExperimentMonitor(progress_file, args.refresh)
    
    try:
        if args.compact:
            monitor.run_compact()
        else:
            monitor.run()
    except KeyboardInterrupt:
        print("\nMonitor stopped. Experiment continues in background.")


if __name__ == "__main__":
    main()