#!/usr/bin/env python3
"""
Complete analysis of ALL CSV files in the results directory.
This corrects the earlier error where not all CSVs were analyzed.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

# Set style for better visualizations
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

def load_all_csv_files(results_dir="/mnt/c/Apps/LLM-IPD-ARXIV/results"):
    """Load ALL CSV files from results directory"""
    csv_files = sorted(Path(results_dir).rglob("*.csv"))
    print(f"\n📊 Found {len(csv_files)} CSV files to analyze:")
    
    all_data = {}
    for csv_file in csv_files:
        print(f"  Loading: {csv_file.name}")
        df = pd.read_csv(csv_file)
        
        # Extract experiment info from path
        parts = str(csv_file).split('/')
        experiment = parts[-2] if len(parts) > 1 else "unknown"
        filename = csv_file.stem
        
        all_data[f"{experiment}/{filename}"] = df
        
    return all_data

def analyze_all_tournaments(all_data):
    """Comprehensive analysis of all tournament data"""
    results = {
        'experiments': {},
        'all_agents': set(),
        'all_llm_agents': set(),
        'all_providers': set(),
        'total_matches': 0,
        'total_rounds': 0,
        'phase_summaries': []
    }
    
    for key, df in all_data.items():
        print(f"\n📈 Analyzing: {key}")
        
        # Parse experiment/phase info
        if 'phase' in key:
            phase_num = int(key.split('phase')[-1].split('.')[0])
        else:
            phase_num = 1
            
        if 'shadow' in key:
            if 'shadow75' in key:
                shadow = 0.75
            elif 'shadow50' in key:
                shadow = 0.50
            else:
                shadow = 0.75
        else:
            shadow = 0.75
            
        experiment_key = key.split('/')[0]
        
        if experiment_key not in results['experiments']:
            results['experiments'][experiment_key] = {
                'phases': {},
                'shadow': shadow,
                'total_matches': 0,
                'total_rounds': 0
            }
        
        # Count matches and rounds
        n_matches = len(df)
        n_rounds = df['round'].max() if 'round' in df.columns else n_matches
        
        results['total_matches'] += n_matches
        results['total_rounds'] += n_rounds
        results['experiments'][experiment_key]['total_matches'] += n_matches
        results['experiments'][experiment_key]['total_rounds'] += n_rounds
        
        # Extract all unique agents
        if 'agent1' in df.columns and 'agent2' in df.columns:
            agents = set(df['agent1'].unique()) | set(df['agent2'].unique())
        elif 'player1' in df.columns and 'player2' in df.columns:
            agents = set(df['player1'].unique()) | set(df['player2'].unique())
        else:
            agents = set()
            
        results['all_agents'].update(agents)
        
        # Identify LLM agents and their providers
        llm_agents = set()
        providers = set()
        
        for agent in agents:
            agent_clean = agent.split('_')[0] if '_' in agent else agent
            
            # Check for all LLM types (including Ministral with 'i')
            if any(x in agent for x in ['GPT', 'gpt', 'o3', 'o1']):
                llm_agents.add(agent)
                providers.add('OpenAI')
            elif any(x in agent for x in ['Claude', 'claude']):
                llm_agents.add(agent)
                providers.add('Anthropic')
            elif any(x in agent for x in ['Mistral', 'Ministral', 'mistral', 'ministral']):
                llm_agents.add(agent)
                providers.add('Mistral')
                print(f"    ⚠️ Found Mistral agent: {agent}")  # Highlight Mistral findings
            elif any(x in agent for x in ['Gemini', 'gemini']):
                llm_agents.add(agent)
                providers.add('Google')
                
        results['all_llm_agents'].update(llm_agents)
        results['all_providers'].update(providers)
        
        # Analyze cooperation rates
        if 'move1' in df.columns and 'move2' in df.columns:
            coop_rate = ((df['move1'] == 'C').sum() + (df['move2'] == 'C').sum()) / (len(df) * 2)
        elif 'action1' in df.columns and 'action2' in df.columns:
            coop_rate = ((df['action1'] == 'C').sum() + (df['action2'] == 'C').sum()) / (len(df) * 2)
        else:
            coop_rate = 0
            
        # Store phase data
        phase_data = {
            'experiment': experiment_key,
            'phase': phase_num,
            'shadow': shadow,
            'n_agents': len(agents),
            'n_llm_agents': len(llm_agents),
            'n_matches': n_matches,
            'n_rounds': n_rounds,
            'avg_rounds_per_match': n_rounds / n_matches if n_matches > 0 else 0,
            'cooperation_rate': coop_rate,
            'providers': list(providers),
            'llm_agents': list(llm_agents)
        }
        
        results['experiments'][experiment_key]['phases'][phase_num] = phase_data
        results['phase_summaries'].append(phase_data)
        
        print(f"    Agents: {len(agents)} ({len(llm_agents)} LLMs)")
        print(f"    Providers: {providers if providers else 'None'}")
        print(f"    Matches: {n_matches}")
        print(f"    Cooperation: {coop_rate:.1%}")
    
    return results

def analyze_agent_performance(all_data):
    """Detailed performance analysis for each agent"""
    agent_stats = defaultdict(lambda: {
        'total_score': 0,
        'total_matches': 0,
        'total_rounds': 0,
        'cooperation_count': 0,
        'defection_count': 0,
        'phases_survived': set(),
        'provider': None,
        'temperature': None
    })
    
    for key, df in all_data.items():
        # Extract phase number
        if 'phase' in key:
            phase = int(key.split('phase')[-1].split('.')[0])
        else:
            phase = 1
            
        # Process each row
        for _, row in df.iterrows():
            # Get agent names and scores
            if 'agent1' in row and 'agent2' in row:
                agent1, agent2 = row['agent1'], row['agent2']
            elif 'player1' in row and 'player2' in row:
                agent1, agent2 = row['player1'], row['player2']
            else:
                continue
                
            if 'score1' in row and 'score2' in row:
                score1, score2 = row['score1'], row['score2']
            elif 'payoff1' in row and 'payoff2' in row:
                score1, score2 = row['payoff1'], row['payoff2']
            else:
                score1, score2 = 0, 0
                
            # Get moves
            if 'move1' in row and 'move2' in row:
                move1, move2 = row['move1'], row['move2']
            elif 'action1' in row and 'action2' in row:
                move1, move2 = row['action1'], row['action2']
            else:
                move1, move2 = None, None
                
            # Update agent1 stats
            agent_stats[agent1]['total_score'] += score1
            agent_stats[agent1]['total_matches'] += 1
            agent_stats[agent1]['total_rounds'] += 1
            agent_stats[agent1]['phases_survived'].add(phase)
            if move1 == 'C':
                agent_stats[agent1]['cooperation_count'] += 1
            elif move1 == 'D':
                agent_stats[agent1]['defection_count'] += 1
                
            # Update agent2 stats
            agent_stats[agent2]['total_score'] += score2
            agent_stats[agent2]['total_matches'] += 1
            agent_stats[agent2]['total_rounds'] += 1
            agent_stats[agent2]['phases_survived'].add(phase)
            if move2 == 'C':
                agent_stats[agent2]['cooperation_count'] += 1
            elif move2 == 'D':
                agent_stats[agent2]['defection_count'] += 1
                
    # Identify providers and calculate derived stats
    for agent, stats in agent_stats.items():
        # Identify provider
        if any(x in agent for x in ['GPT', 'gpt', 'o3', 'o1']):
            stats['provider'] = 'OpenAI'
        elif any(x in agent for x in ['Claude', 'claude']):
            stats['provider'] = 'Anthropic'
        elif any(x in agent for x in ['Mistral', 'Ministral', 'mistral', 'ministral']):
            stats['provider'] = 'Mistral'
        elif any(x in agent for x in ['Gemini', 'gemini']):
            stats['provider'] = 'Google'
        else:
            stats['provider'] = 'Classical'
            
        # Extract temperature if present
        if '_T' in agent:
            try:
                temp_str = agent.split('_T')[1].split('_')[0]
                stats['temperature'] = float(temp_str.replace('0', '0.'))
            except:
                pass
                
        # Calculate derived stats
        total_moves = stats['cooperation_count'] + stats['defection_count']
        if total_moves > 0:
            stats['cooperation_rate'] = stats['cooperation_count'] / total_moves
        else:
            stats['cooperation_rate'] = 0
            
        if stats['total_rounds'] > 0:
            stats['avg_score'] = stats['total_score'] / stats['total_rounds']
        else:
            stats['avg_score'] = 0
            
        stats['max_phase'] = max(stats['phases_survived']) if stats['phases_survived'] else 0
        
    return dict(agent_stats)

def analyze_provider_performance(agent_stats):
    """Aggregate performance by provider"""
    provider_stats = defaultdict(lambda: {
        'agents': [],
        'total_score': 0,
        'total_rounds': 0,
        'cooperation_count': 0,
        'defection_count': 0,
        'max_phase_survived': 0,
        'temperatures': set()
    })
    
    for agent, stats in agent_stats.items():
        provider = stats['provider']
        if provider and provider != 'Classical':
            provider_stats[provider]['agents'].append(agent)
            provider_stats[provider]['total_score'] += stats['total_score']
            provider_stats[provider]['total_rounds'] += stats['total_rounds']
            provider_stats[provider]['cooperation_count'] += stats['cooperation_count']
            provider_stats[provider]['defection_count'] += stats['defection_count']
            provider_stats[provider]['max_phase_survived'] = max(
                provider_stats[provider]['max_phase_survived'],
                stats['max_phase']
            )
            if stats['temperature']:
                provider_stats[provider]['temperatures'].add(stats['temperature'])
    
    # Calculate derived stats
    for provider, stats in provider_stats.items():
        total_moves = stats['cooperation_count'] + stats['defection_count']
        if total_moves > 0:
            stats['cooperation_rate'] = stats['cooperation_count'] / total_moves
        else:
            stats['cooperation_rate'] = 0
            
        if stats['total_rounds'] > 0:
            stats['avg_score'] = stats['total_score'] / stats['total_rounds']
        else:
            stats['avg_score'] = 0
            
        stats['n_agents'] = len(stats['agents'])
        stats['temperatures'] = sorted(list(stats['temperatures']))
        
    return dict(provider_stats)

def print_complete_analysis(results, agent_stats, provider_stats):
    """Print comprehensive analysis results"""
    print("\n" + "="*80)
    print("COMPLETE TOURNAMENT ANALYSIS - ALL CSV FILES")
    print("="*80)
    
    print("\n📊 OVERALL STATISTICS")
    print(f"Total CSV files analyzed: {len(results['phase_summaries'])}")
    print(f"Total matches: {results['total_matches']:,}")
    print(f"Total rounds: {results['total_rounds']:,}")
    print(f"Average rounds per match: {results['total_rounds']/results['total_matches']:.2f}")
    print(f"Total unique agents: {len(results['all_agents'])}")
    print(f"Total LLM agents: {len(results['all_llm_agents'])}")
    
    print("\n🏢 LLM PROVIDERS FOUND")
    for provider in sorted(results['all_providers']):
        print(f"  ✓ {provider}")
        
    if 'Mistral' in results['all_providers']:
        print("\n⚠️  MISTRAL CONFIRMED: Mistral agents were found in the tournament!")
        
    print("\n📈 PROVIDER PERFORMANCE SUMMARY")
    print("-" * 60)
    print(f"{'Provider':<12} {'Agents':<8} {'Avg Score':<10} {'Coop Rate':<10} {'Survival':<10}")
    print("-" * 60)
    
    for provider in sorted(provider_stats.keys()):
        stats = provider_stats[provider]
        print(f"{provider:<12} {stats['n_agents']:<8} {stats['avg_score']:<10.3f} {stats['cooperation_rate']:<10.1%} Phase {stats['max_phase_survived']}")
        
    print("\n🎮 TOP 10 AGENTS BY SCORE")
    print("-" * 70)
    print(f"{'Rank':<6} {'Agent':<30} {'Avg Score':<10} {'Coop Rate':<10} {'Survival':<10}")
    print("-" * 70)
    
    sorted_agents = sorted(agent_stats.items(), key=lambda x: x[1]['avg_score'], reverse=True)
    for i, (agent, stats) in enumerate(sorted_agents[:10], 1):
        agent_name = agent.split('_')[0] if '_p' in agent else agent
        print(f"{i:<6} {agent_name:<30} {stats['avg_score']:<10.3f} {stats['cooperation_rate']:<10.1%} Phase {stats['max_phase']}")
        
    print("\n🔍 MISTRAL AGENTS DETAIL")
    print("-" * 70)
    mistral_agents = [(a, s) for a, s in agent_stats.items() if 'istral' in a]
    if mistral_agents:
        for agent, stats in mistral_agents:
            print(f"{agent}: Score={stats['avg_score']:.3f}, Coop={stats['cooperation_rate']:.1%}, Survived to Phase {stats['max_phase']}")
    else:
        print("No Mistral agents found (this would be an error!)")
        
    print("\n📊 PHASE-BY-PHASE EVOLUTION")
    print("-" * 80)
    
    # Group by experiment
    for exp_name, exp_data in results['experiments'].items():
        print(f"\nExperiment: {exp_name} (Shadow={exp_data['shadow']*100}%)")
        
        for phase_num in sorted(exp_data['phases'].keys()):
            phase = exp_data['phases'][phase_num]
            print(f"  Phase {phase_num}: {phase['n_agents']} agents, {phase['cooperation_rate']:.1%} cooperation")
            if phase['providers']:
                print(f"    Providers: {', '.join(phase['providers'])}")

def main():
    print("🔍 Starting complete analysis of ALL CSV files...")
    
    # Load all CSV files
    all_data = load_all_csv_files()
    
    # Run comprehensive analysis
    results = analyze_all_tournaments(all_data)
    agent_stats = analyze_agent_performance(all_data)
    provider_stats = analyze_provider_performance(agent_stats)
    
    # Print results
    print_complete_analysis(results, agent_stats, provider_stats)
    
    # Save results to JSON
    output_file = "/mnt/c/Apps/LLM-IPD-ARXIV/Stephan_checking/complete_analysis_results.json"
    
    # Convert sets to lists for JSON serialization
    def convert_sets(obj):
        if isinstance(obj, set):
            return list(obj)
        elif isinstance(obj, dict):
            return {k: convert_sets(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_sets(item) for item in obj]
        return obj
    
    save_data = {
        'summary': results,
        'agent_stats': agent_stats,
        'provider_stats': provider_stats
    }
    save_data = convert_sets(save_data)
    
    with open(output_file, 'w') as f:
        json.dump(save_data, f, indent=2)
    print(f"\n✅ Results saved to: {output_file}")
    
    return results, agent_stats, provider_stats

if __name__ == "__main__":
    main()