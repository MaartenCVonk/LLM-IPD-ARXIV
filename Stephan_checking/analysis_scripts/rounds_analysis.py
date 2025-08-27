#!/usr/bin/env python3
"""Detailed analysis of rounds per match and per phase in the tournament"""

import pandas as pd
import numpy as np
from pathlib import Path

def analyze_rounds_structure():
    """Analyze the number of rounds per match and per phase"""
    
    print("\n" + "="*80)
    print("TOURNAMENT STRUCTURE: ROUNDS ANALYSIS")
    print("="*80)
    
    # Load all phases
    data = {}
    exp_path = Path('results/experiment_20250811_131553')
    
    for phase in range(1, 6):
        file = exp_path / f'evolutionary_shadow75_phase{phase}.csv'
        if file.exists():
            data[phase] = pd.read_csv(file)
            print(f"Loaded Phase {phase}: {len(data[phase])} total rows")
    
    print("\n" + "="*80)
    print("DETAILED ROUNDS BREAKDOWN")
    print("="*80)
    
    all_round_lengths = []
    
    for phase_num, df in data.items():
        print(f"\n📊 PHASE {phase_num} ANALYSIS:")
        print("-"*40)
        
        # Get unique matches
        unique_matches = df['match_id'].unique()
        num_matches = len(unique_matches)
        
        # Count rounds per match
        rounds_per_match = df.groupby('match_id')['round'].max()
        
        # Statistics
        total_rounds = len(df)
        min_rounds = rounds_per_match.min()
        max_rounds = rounds_per_match.max()
        avg_rounds = rounds_per_match.mean()
        std_rounds = rounds_per_match.std()
        median_rounds = rounds_per_match.median()
        
        # Store for overall analysis
        all_round_lengths.extend(rounds_per_match.tolist())
        
        print(f"Total Matches: {num_matches}")
        print(f"Total Rounds Played: {total_rounds}")
        print(f"\nRounds per Match Statistics:")
        print(f"  • Average: {avg_rounds:.2f} rounds")
        print(f"  • Median: {median_rounds:.0f} rounds")
        print(f"  • Std Dev: {std_rounds:.2f} rounds")
        print(f"  • Min: {min_rounds} rounds")
        print(f"  • Max: {max_rounds} rounds")
        
        # Distribution of round lengths
        round_dist = rounds_per_match.value_counts().sort_index()
        print(f"\nRound Length Distribution:")
        for length, count in round_dist.items():
            percentage = (count / num_matches) * 100
            print(f"  {length} round(s): {count} matches ({percentage:.1f}%)")
        
        # Theoretical expectation with shadow = 0.75
        shadow = 0.75
        expected_rounds = 1 / shadow
        print(f"\nTheoretical Expectation (shadow={shadow}):")
        print(f"  Expected rounds: {expected_rounds:.2f}")
        print(f"  Actual average: {avg_rounds:.2f}")
        print(f"  Difference: {avg_rounds - expected_rounds:.2f} ({((avg_rounds/expected_rounds - 1)*100):.1f}% from expected)")
        
        # Sample some specific matches
        print(f"\nSample Matches:")
        sample_matches = unique_matches[:5]
        for match_id in sample_matches:
            match_data = df[df['match_id'] == match_id]
            agents = match_id.split('_vs_')
            rounds = match_data['round'].max()
            print(f"  • {agents[0][:20]} vs {agents[1][:20]}: {rounds} rounds")
    
    # Overall tournament statistics
    print("\n" + "="*80)
    print("OVERALL TOURNAMENT STATISTICS (ALL PHASES)")
    print("="*80)
    
    print(f"\nTotal Phases: 5")
    print(f"Matches per Phase: 378 (28 agents × 27 opponents / 2)")
    print(f"Total Matches in Tournament: {5 * 378} = 1,890 matches")
    
    total_rounds_all_phases = sum(len(df) for df in data.values())
    print(f"\nTotal Rounds Played (All Phases): {total_rounds_all_phases}")
    
    overall_avg = np.mean(all_round_lengths)
    overall_std = np.std(all_round_lengths)
    overall_median = np.median(all_round_lengths)
    
    print(f"\nOverall Round Statistics (Across All Matches):")
    print(f"  • Average: {overall_avg:.2f} rounds per match")
    print(f"  • Median: {overall_median:.0f} rounds per match")
    print(f"  • Std Dev: {overall_std:.2f} rounds")
    print(f"  • Total Matches Analyzed: {len(all_round_lengths)}")
    
    # Calculate probability that a match ends at round N
    print("\n" + "="*80)
    print("PROBABILITY DISTRIBUTION OF MATCH LENGTHS")
    print("="*80)
    
    # Theoretical vs Actual
    print(f"\nWith shadow probability = 0.75 (75% chance to end each round):")
    print(f"Theoretical probabilities:")
    for r in range(1, 6):
        theoretical_prob = 0.75 * (0.25 ** (r-1))
        actual_count = sum(1 for length in all_round_lengths if length == r)
        actual_prob = actual_count / len(all_round_lengths)
        print(f"  Round {r}: Theory={theoretical_prob:.3f}, Actual={actual_prob:.3f}")
    
    # Matches that went long
    long_matches = [l for l in all_round_lengths if l > 5]
    print(f"\nMatches lasting >5 rounds: {len(long_matches)} ({len(long_matches)/len(all_round_lengths)*100:.1f}%)")
    
    # Expected vs reality check
    print("\n" + "="*80)
    print("SHADOW OF THE FUTURE VERIFICATION")
    print("="*80)
    
    print(f"\nShadow = 0.75 means:")
    print(f"  • 75% chance to end after each round")
    print(f"  • 25% chance to continue to next round")
    print(f"  • Expected length = 1/(1-p) where p=0.25")
    print(f"  • Expected length = 1/0.75 = {1/0.75:.2f} rounds")
    
    print(f"\nActual Results:")
    print(f"  • Average match length: {overall_avg:.2f} rounds")
    print(f"  • This is {overall_avg / (1/0.75) * 100:.1f}% of theoretical expectation")
    
    # The paper's claim vs reality
    print("\n⚠️  IMPORTANT DISCREPANCY:")
    print("-"*40)
    print("The PDF claims shadow 0.75 gives ~4.0 rounds per match")
    print(f"Actual data shows: {overall_avg:.2f} rounds per match")
    print(f"Mathematical expectation: {1/0.75:.2f} rounds per match")
    print("\nThe PDF appears to have an error in its expected round calculations!")

if __name__ == "__main__":
    analyze_rounds_structure()