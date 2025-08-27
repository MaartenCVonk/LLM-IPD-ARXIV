#!/usr/bin/env python3
"""Analyze the NEW experiments with lower shadow values."""

import pandas as pd
import numpy as np
import json
from pathlib import Path

def analyze_experiment(csv_path, shadow):
    """Analyze a single experiment CSV."""
    df = pd.read_csv(csv_path)
    
    # Get unique matches
    unique_matches = df['match_id'].unique()
    
    # Calculate rounds per match
    rounds_per_match = df.groupby('match_id')['round'].max().values
    
    stats = {
        'shadow': shadow,
        'expected_rounds': 1 / (1 - shadow),
        'total_matches': len(unique_matches),
        'total_rounds': len(df),
        'avg_rounds': np.mean(rounds_per_match),
        'median_rounds': np.median(rounds_per_match),
        'max_rounds': np.max(rounds_per_match),
        'min_rounds': np.min(rounds_per_match),
        'std_rounds': np.std(rounds_per_match),
        'rounds_distribution': {
            '1 round': np.sum(rounds_per_match == 1),
            '2-5 rounds': np.sum((rounds_per_match >= 2) & (rounds_per_match <= 5)),
            '6-10 rounds': np.sum((rounds_per_match >= 6) & (rounds_per_match <= 10)),
            '11-20 rounds': np.sum((rounds_per_match >= 11) & (rounds_per_match <= 20)),
            '21+ rounds': np.sum(rounds_per_match > 20)
        }
    }
    
    # Check for LLM providers
    providers = set()
    for match_id in unique_matches[:100]:  # Sample first 100 matches
        if 'o3' in match_id or 'o3mini' in match_id:
            providers.add('OpenAI')
        if 'Claude' in match_id:
            providers.add('Anthropic')
        if 'Gemini' in match_id:
            providers.add('Google')
        if 'Ministral' in match_id or 'Mistral' in match_id:
            providers.add('Mistral')
    
    stats['providers_found'] = list(providers)
    
    return stats

def main():
    results_dir = Path('/mnt/c/Apps/LLM-IPD-ARXIV/results')
    
    experiments = [
        {
            'name': 'Shadow 0.75 (Original)',
            'path': results_dir / 'experiment_20250811_131553' / 'evolutionary_shadow75_phase1.csv',
            'shadow': 0.75
        },
        {
            'name': 'Shadow 0.25 (NEW)',
            'path': results_dir / 'experiment_20250812_192959' / 'evolutionary_shadow25_phase1.csv',
            'shadow': 0.25
        },
        {
            'name': 'Shadow 0.10 (NEW)',
            'path': results_dir / 'experiment_20250818_102320' / 'evolutionary_shadow10_phase1.csv',
            'shadow': 0.10
        }
    ]
    
    print("=" * 80)
    print("ANALYSIS OF NEW EXPERIMENTS WITH LOWER SHADOW VALUES")
    print("=" * 80)
    
    all_stats = []
    
    for exp in experiments:
        if exp['path'].exists():
            print(f"\n### {exp['name']} ###")
            stats = analyze_experiment(exp['path'], exp['shadow'])
            all_stats.append(stats)
            
            print(f"Shadow value: {stats['shadow']}")
            print(f"Expected rounds (1/(1-shadow)): {stats['expected_rounds']:.2f}")
            print(f"Actual average rounds: {stats['avg_rounds']:.2f}")
            print(f"Median rounds: {stats['median_rounds']:.0f}")
            print(f"Max rounds in any match: {stats['max_rounds']}")
            print(f"Total matches analyzed: {stats['total_matches']}")
            
            print("\nRounds Distribution:")
            total = stats['total_matches']
            for category, count in stats['rounds_distribution'].items():
                pct = (count / total) * 100
                print(f"  {category}: {count} matches ({pct:.1f}%)")
            
            print(f"\nProviders detected: {', '.join(stats['providers_found'])}")
            
            # Check if actual matches expected
            diff = abs(stats['avg_rounds'] - stats['expected_rounds'])
            if diff < 0.5:
                print("✅ Actual rounds match mathematical expectation!")
            else:
                print(f"⚠️ Discrepancy: {diff:.2f} rounds difference from expectation")
    
    # Comparative analysis
    print("\n" + "=" * 80)
    print("COMPARATIVE ANALYSIS: THE IMPACT OF SHADOW VALUE")
    print("=" * 80)
    
    print("\n| Shadow | Expected | Actual Avg | % Single Round | % 10+ Rounds |")
    print("|--------|----------|------------|----------------|--------------|")
    
    for stats in all_stats:
        single_round_pct = (stats['rounds_distribution']['1 round'] / stats['total_matches']) * 100
        ten_plus = stats['rounds_distribution'].get('11-20 rounds', 0) + stats['rounds_distribution'].get('21+ rounds', 0)
        ten_plus_pct = (ten_plus / stats['total_matches']) * 100
        
        print(f"| {stats['shadow']:.2f}   | {stats['expected_rounds']:8.2f} | {stats['avg_rounds']:10.2f} | {single_round_pct:14.1f} | {ten_plus_pct:12.1f} |")
    
    print("\n🎯 KEY FINDING:")
    if all_stats[-1]['avg_rounds'] > 5:
        print("Shadow 0.10 FINALLY provides meaningful iteration!")
        print(f"With {all_stats[-1]['avg_rounds']:.1f} average rounds, agents can:")
        print("- Establish patterns beyond opening moves")
        print("- Learn from opponent behavior")
        print("- Develop reciprocal strategies")
        print("- Experience the true IPD dynamics")
    else:
        print("Even shadow 0.10 may not be sufficient for deep strategic play")
    
    # Save results
    output_path = Path('/mnt/c/Apps/LLM-IPD-ARXIV/Stephan_checking/analysis_scripts/new_experiments_analysis.json')
    with open(output_path, 'w') as f:
        json.dump(all_stats, f, indent=2)
    print(f"\n📊 Full statistics saved to: {output_path}")

if __name__ == "__main__":
    main()