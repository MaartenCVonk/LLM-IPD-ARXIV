#!/usr/bin/env python3
"""
Auto-run version of experiments (no user input required)
"""

import os
import sys

# Set up to auto-confirm
os.environ['AUTO_CONFIRM'] = 'yes'

# Import and run the main experiment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from run_experiments import run_main_experiments

if __name__ == "__main__":
    # Run with default settings
    run_main_experiments(
        shadow_conditions=[0.1, 0.25, 0.75],
        temperature_settings=[0.2, 0.7, 1.2],
        n_tournaments=2,
        output_dir="results"
    )