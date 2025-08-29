#!/usr/bin/env python3
"""Comprehensive analysis of ALL strategies across shadow values."""

import pandas as pd
import numpy as np
from pathlib import Path
import json

def analyze_strategies_detailed(base_path, shadow, phase=1):
    """Analyze all strategies in detail for a given shadow value."""
    
    csv_path = base_path / f"evolutionary_shadow{int(shadow*100)}_phase{phase}.csv"
    if not csv_path.exists():
        # Try alternative naming
        csv_path = base_path / f"evolutionary_shadow{int(shadow*100)}_phase1.csv"
    
    if not csv_path.exists():
        return None
        
    df = pd.read_csv(csv_path)
    
    # Extract agent types
    def get_agent_type(agent_name):
        """Categorize agents by type."""
        if any(x in agent_name for x in ['o3', 'O3']):
            return 'OpenAI'
        elif any(x in agent_name for x in ['Claude', 'claude']):
            return 'Anthropic'
        elif any(x in agent_name for x in ['Gemini', 'gemini']):
            return 'Google'
        elif any(x in agent_name for x in ['Mistral', 'Ministral']):
            return 'Mistral'
        elif any(x in agent_name for x in ['QLearning', 'QLearn']):
            return 'Learning-Q'
        elif any(x in agent_name for x in ['Thompson', 'Sampling']):
            return 'Learning-Thompson'
        elif any(x in agent_name for x in ['Gradient', 'Meta']):
            return 'Learning-Gradient'
        elif any(x in agent_name for x in ['Detective']):
            return 'Behavioral-Detective'
        elif any(x in agent_name for x in ['SoftGrudger', 'Soft']):
            return 'Behavioral-SoftGrudger'
        elif any(x in agent_name for x in ['ForgivingGrim', 'Forgiving']):
            return 'Behavioral-Forgiving'
        elif any(x in agent_name for x in ['TitForTat', 'Tit']):
            return 'Classical-TitForTat'
        elif any(x in agent_name for x in ['AlwaysCooperate']):
            return 'Classical-AlwaysCoop'
        elif any(x in agent_name for x in ['AlwaysDefect']):
            return 'Classical-AlwaysDefect'
        elif any(x in agent_name for x in ['Random']):
            return 'Classical-Random'
        elif any(x in agent_name for x in ['GrimTrigger', 'Grim']):
            return 'Classical-GrimTrigger'
        elif any(x in agent_name for x in ['Pavlov']):
            return 'Classical-Pavlov'
        elif any(x in agent_name for x in ['SuspiciousTit']):
            return 'Behavioral-Suspicious'
        else:
            return 'Other'
    
    results = {}
    
    # Get unique matches
    unique_matches = df['match_id'].unique()
    
    for match_id in unique_matches:
        match_data = df[df['match_id'] == match_id]
        
        # Extract agents
        parts = match_id.split('_vs_')
        if len(parts) != 2:
            continue
            
        agent1, agent2 = parts
        agent1_type = get_agent_type(agent1)
        agent2_type = get_agent_type(agent2)
        
        # Calculate metrics
        rounds = match_data['round'].max()
        
        # Get moves and scores
        agent1_moves = match_data['agent1_move'].values
        agent2_moves = match_data['agent2_move'].values
        agent1_scores = match_data['agent1_score'].values
        agent2_scores = match_data['agent2_score'].values
        
        # Calculate cooperation rates
        agent1_coop = np.mean(agent1_moves == 'C') if len(agent1_moves) > 0 else 0
        agent2_coop = np.mean(agent2_moves == 'C') if len(agent2_moves) > 0 else 0
        
        # Total scores
        agent1_total = np.sum(agent1_scores)
        agent2_total = np.sum(agent2_scores)
        
        # Store results
        for agent, agent_type, coop_rate, total_score in [
            (agent1, agent1_type, agent1_coop, agent1_total),
            (agent2, agent2_type, agent2_coop, agent2_total)
        ]:
            if agent_type not in results:
                results[agent_type] = {
                    'matches': 0,
                    'total_rounds': 0,
                    'total_score': 0,
                    'cooperation_count': 0,
                    'move_count': 0,
                    'rounds_list': []
                }
            
            results[agent_type]['matches'] += 1
            results[agent_type]['total_rounds'] += rounds
            results[agent_type]['total_score'] += total_score
            results[agent_type]['cooperation_count'] += coop_rate * rounds
            results[agent_type]['move_count'] += rounds
            results[agent_type]['rounds_list'].append(rounds)
    
    # Calculate final metrics
    final_results = {}
    for agent_type, data in results.items():
        if data['matches'] > 0:
            final_results[agent_type] = {
                'avg_rounds': data['total_rounds'] / data['matches'],
                'avg_score_per_match': data['total_score'] / data['matches'],
                'avg_score_per_round': data['total_score'] / data['total_rounds'] if data['total_rounds'] > 0 else 0,
                'cooperation_rate': data['cooperation_count'] / data['move_count'] if data['move_count'] > 0 else 0,
                'total_matches': data['matches'],
                'median_rounds': np.median(data['rounds_list']),
                'max_rounds': max(data['rounds_list']) if data['rounds_list'] else 0
            }
    
    return final_results

def main():
    results_dir = Path('/mnt/c/Apps/LLM-IPD-ARXIV/results')
    
    # Define experiments
    experiments = [
        ('experiment_20250811_131553', 0.75),
        ('experiment_20250812_192959', 0.25),
        ('experiment_20250818_102320', 0.10)
    ]
    
    print("=" * 100)
    print("COMPREHENSIVE STRATEGY ANALYSIS ACROSS SHADOW VALUES")
    print("=" * 100)
    
    all_results = {}
    
    for exp_dir, shadow in experiments:
        base_path = results_dir / exp_dir
        results = analyze_strategies_detailed(base_path, shadow)
        
        if results:
            all_results[shadow] = results
            
    # Now compare across shadow values
    print("\n### LEARNING ALGORITHMS PERFORMANCE ###")
    print("-" * 80)
    
    learning_agents = ['Learning-Q', 'Learning-Thompson', 'Learning-Gradient']
    
    print("\n| Strategy | Metric | Shadow 0.75 | Shadow 0.25 | Shadow 0.10 | % Change |")
    print("|----------|--------|-------------|-------------|-------------|----------|")
    
    for agent in learning_agents:
        if all([agent in all_results.get(shadow, {}) for shadow in [0.75, 0.10]]):
            s75 = all_results[0.75][agent]
            s10 = all_results[0.10][agent]
            
            score_change = ((s10['avg_score_per_round'] - s75['avg_score_per_round']) / s75['avg_score_per_round']) * 100
            
            print(f"| {agent.split('-')[1]:12} | Score/Round | {s75['avg_score_per_round']:.3f} | "
                  f"{all_results.get(0.25, {}).get(agent, {}).get('avg_score_per_round', 0):.3f} | "
                  f"{s10['avg_score_per_round']:.3f} | {score_change:+.1f}% |")
            print(f"| {'':12} | Cooperation | {s75['cooperation_rate']:.1%} | "
                  f"{all_results.get(0.25, {}).get(agent, {}).get('cooperation_rate', 0):.1%} | "
                  f"{s10['cooperation_rate']:.1%} | - |")
            print(f"| {'':12} | Avg Rounds | {s75['avg_rounds']:.1f} | "
                  f"{all_results.get(0.25, {}).get(agent, {}).get('avg_rounds', 0):.1f} | "
                  f"{s10['avg_rounds']:.1f} | - |")
    
    print("\n### BEHAVIORAL STRATEGIES (NEW RULES) ###")
    print("-" * 80)
    
    behavioral = ['Behavioral-Detective', 'Behavioral-SoftGrudger', 'Behavioral-Forgiving', 'Behavioral-Suspicious']
    
    print("\n| Strategy | Shadow 0.75 | Shadow 0.10 | Performance Change |")
    print("|----------|-------------|-------------|-------------------|")
    
    for agent in behavioral:
        if agent in all_results.get(0.75, {}) and agent in all_results.get(0.10, {}):
            s75 = all_results[0.75][agent]
            s10 = all_results[0.10][agent]
            
            score_change = ((s10['avg_score_per_round'] - s75['avg_score_per_round']) / s75['avg_score_per_round']) * 100
            
            print(f"| {agent.split('-')[1]:15} | {s75['avg_score_per_round']:.3f} ({s75['cooperation_rate']:.0%} coop) | "
                  f"{s10['avg_score_per_round']:.3f} ({s10['cooperation_rate']:.0%} coop) | "
                  f"{score_change:+.1f}% |")
    
    print("\n### CLASSICAL STRATEGIES ###")
    print("-" * 80)
    
    classical = ['Classical-TitForTat', 'Classical-Pavlov', 'Classical-GrimTrigger', 
                 'Classical-AlwaysDefect', 'Classical-AlwaysCoop', 'Classical-Random']
    
    print("\n| Strategy | Shadow 0.75 Score | Shadow 0.10 Score | Viability Change |")
    print("|----------|-------------------|-------------------|------------------|")
    
    for agent in classical:
        if agent in all_results.get(0.75, {}) and agent in all_results.get(0.10, {}):
            s75 = all_results[0.75][agent]
            s10 = all_results[0.10][agent]
            
            score_change = ((s10['avg_score_per_round'] - s75['avg_score_per_round']) / s75['avg_score_per_round']) * 100
            
            viability = "📈 MORE VIABLE" if score_change > 10 else "📉 LESS VIABLE" if score_change < -10 else "➡️ UNCHANGED"
            
            print(f"| {agent.split('-')[1]:12} | {s75['avg_score_per_round']:.3f} | "
                  f"{s10['avg_score_per_round']:.3f} | {viability} ({score_change:+.1f}%) |")
    
    print("\n### KEY INSIGHTS ###")
    print("-" * 80)
    
    # Calculate some key insights
    if 0.75 in all_results and 0.10 in all_results:
        # Who benefits most from iteration?
        winners = []
        losers = []
        
        for agent in all_results[0.75]:
            if agent in all_results[0.10]:
                s75 = all_results[0.75][agent]
                s10 = all_results[0.10][agent]
                change = ((s10['avg_score_per_round'] - s75['avg_score_per_round']) / s75['avg_score_per_round']) * 100
                
                if change > 15:
                    winners.append((agent, change))
                elif change < -15:
                    losers.append((agent, change))
        
        print("\n🏆 BIGGEST WINNERS WITH ITERATION:")
        for agent, change in sorted(winners, key=lambda x: x[1], reverse=True)[:5]:
            print(f"  - {agent}: {change:+.1f}% improvement")
        
        print("\n💀 BIGGEST LOSERS WITH ITERATION:")
        for agent, change in sorted(losers, key=lambda x: x[1])[:5]:
            print(f"  - {agent}: {change:.1f}% decline")
    
    # Save detailed results
    output_path = Path('/mnt/c/Apps/LLM-IPD-ARXIV/Stephan_checking/analysis_scripts/comprehensive_strategy_results.json')
    
    # Convert numpy types for JSON serialization
    def convert_numpy(obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return obj
    
    clean_results = {}
    for shadow, strategies in all_results.items():
        clean_results[str(shadow)] = {}
        for strategy, metrics in strategies.items():
            clean_results[str(shadow)][strategy] = {k: convert_numpy(v) for k, v in metrics.items() if k != 'rounds_list'}
    
    with open(output_path, 'w') as f:
        json.dump(clean_results, f, indent=2)
    
    print(f"\n📊 Detailed results saved to: {output_path}")

if __name__ == "__main__":
    main()