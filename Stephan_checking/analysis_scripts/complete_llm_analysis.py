#!/usr/bin/env python3
"""Complete LLM analysis including Mistral agents"""

import pandas as pd
import numpy as np
from pathlib import Path

def comprehensive_llm_analysis():
    """Complete analysis including all LLM agents"""
    
    print("\n" + "="*80)
    print("COMPLETE LLM ANALYSIS - INCLUDING MISTRAL")
    print("="*80)
    
    # Load all phases
    data = {}
    exp_path = Path('results/experiment_20250811_131553')
    for phase in range(1, 6):
        file = exp_path / f'evolutionary_shadow75_phase{phase}.csv'
        if file.exists():
            data[phase] = pd.read_csv(file)
    
    # Search for ALL LLMs including Mistral
    all_llm_stats = {}
    
    for phase_num, df in data.items():
        print(f"\n📊 PHASE {phase_num} LLM AGENTS:")
        print("-"*40)
        
        # Get all unique agents
        all_agents = set(df['agent1'].unique()) | set(df['agent2'].unique())
        
        # Find LLM agents
        llm_agents = []
        for agent in all_agents:
            agent_lower = agent.lower()
            if any(x in agent_lower for x in ['ministral', 'mistral', 'claude', 'gpt', 'gemini', 'o3']):
                llm_agents.append(agent)
                
                # Clean agent name
                clean_name = agent.split('_p')[0]
                
                # Categorize
                if 'ministral' in agent_lower or 'mistral' in agent_lower:
                    provider = 'Mistral'
                elif 'claude' in agent_lower:
                    provider = 'Anthropic'
                elif 'gemini' in agent_lower:
                    provider = 'Google'
                elif any(x in agent_lower for x in ['gpt', 'o3']):
                    provider = 'OpenAI'
                else:
                    provider = 'Unknown'
                
                # Get temperature
                temp = None
                if 't02' in agent_lower or 't_02' in agent_lower:
                    temp = 0.2
                elif 't05' in agent_lower or 't_05' in agent_lower:
                    temp = 0.5
                elif 't07' in agent_lower or 't_07' in agent_lower:
                    temp = 0.7
                elif 't08' in agent_lower or 't_08' in agent_lower:
                    temp = 0.8
                elif 't1' in agent_lower or 't_1' in agent_lower:
                    temp = 1.0
                elif 't10' in agent_lower:
                    temp = 1.0
                elif 't12' in agent_lower or 't_12' in agent_lower:
                    temp = 1.2
                
                # Calculate stats
                agent_data = df[(df['agent1'] == agent) | (df['agent2'] == agent)]
                
                scores = []
                moves = []
                
                for _, row in agent_data.iterrows():
                    if row['agent1'] == agent:
                        move = row['agent1_move']
                        opp_move = row['agent2_move']
                    else:
                        move = row['agent2_move']
                        opp_move = row['agent1_move']
                    
                    moves.append(move)
                    
                    # Calculate score
                    if (move, opp_move) == ('C', 'C'):
                        scores.append(3)
                    elif (move, opp_move) == ('C', 'D'):
                        scores.append(0)
                    elif (move, opp_move) == ('D', 'C'):
                        scores.append(5)
                    else:
                        scores.append(1)
                
                if scores:
                    key = f"{clean_name}_{temp}"
                    if key not in all_llm_stats:
                        all_llm_stats[key] = {
                            'provider': provider,
                            'clean_name': clean_name,
                            'temperature': temp,
                            'phases': {}
                        }
                    
                    all_llm_stats[key]['phases'][phase_num] = {
                        'avg_score': np.mean(scores),
                        'coop_rate': moves.count('C') / len(moves) if moves else 0,
                        'rounds': len(scores),
                        'coop_count': moves.count('C'),
                        'defect_count': moves.count('D')
                    }
        
        # Print phase summary
        providers = {}
        for agent in llm_agents:
            if 'ministral' in agent.lower() or 'mistral' in agent.lower():
                provider = 'Mistral'
            elif 'claude' in agent.lower():
                provider = 'Anthropic'
            elif 'gemini' in agent.lower():
                provider = 'Google'
            elif any(x in agent.lower() for x in ['gpt', 'o3']):
                provider = 'OpenAI'
            else:
                continue
            
            if provider not in providers:
                providers[provider] = []
            providers[provider].append(agent)
        
        for provider, agents in providers.items():
            print(f"{provider}: {len(agents)} agents")
            for agent in agents[:3]:  # Show first 3
                print(f"  - {agent}")
            if len(agents) > 3:
                print(f"  ... and {len(agents)-3} more")
    
    # Complete Provider Analysis
    print("\n\n" + "="*60)
    print("COMPLETE PROVIDER COMPARISON - ALL 4 PROVIDERS")
    print("="*60)
    
    provider_stats = {}
    for key, stats in all_llm_stats.items():
        provider = stats['provider']
        if provider not in provider_stats:
            provider_stats[provider] = {
                'scores': [],
                'coop_rates': [],
                'phases_present': set(),
                'models': set()
            }
        
        for phase, phase_data in stats['phases'].items():
            provider_stats[provider]['scores'].append(phase_data['avg_score'])
            provider_stats[provider]['coop_rates'].append(phase_data['coop_rate'])
            provider_stats[provider]['phases_present'].add(phase)
        
        provider_stats[provider]['models'].add(stats['clean_name'])
    
    print(f"\n{'Provider':<12} | {'Avg Score':<10} | {'Coop Rate':<10} | {'Survival':<12} | {'Models'}")
    print("-"*70)
    
    for provider in ['Google', 'OpenAI', 'Mistral', 'Anthropic']:
        if provider in provider_stats:
            stats = provider_stats[provider]
            avg_score = np.mean(stats['scores'])
            avg_coop = np.mean(stats['coop_rates'])
            phases = sorted(stats['phases_present'])
            survival = f"P{min(phases)}-P{max(phases)}"
            models = len(stats['models'])
            
            print(f"{provider:<12} | {avg_score:<10.3f} | {avg_coop:<10.1%} | {survival:<12} | {models} models")
    
    # Mistral Specific Analysis
    print("\n\n" + "="*60)
    print("MISTRAL DETAILED ANALYSIS")
    print("="*60)
    
    mistral_models = [k for k, v in all_llm_stats.items() if v['provider'] == 'Mistral']
    
    if mistral_models:
        print(f"\nMistral Models Found: {len(mistral_models)}")
        
        for model_key in sorted(mistral_models):
            stats = all_llm_stats[model_key]
            print(f"\n{stats['clean_name']} (T={stats['temperature']}):")
            print(f"{'Phase':<8} | {'Avg Score':<10} | {'Coop Rate':<12} | {'Rounds'}")
            print("-"*45)
            
            for phase in sorted(stats['phases'].keys()):
                phase_data = stats['phases'][phase]
                print(f"Phase {phase:<2} | {phase_data['avg_score']:<10.3f} | "
                      f"{phase_data['coop_rate']:<12.1%} | {phase_data['rounds']}")
        
        # Mistral extinction analysis
        print("\n🔍 MISTRAL EXTINCTION ANALYSIS:")
        print("-"*40)
        
        for model_key in mistral_models:
            stats = all_llm_stats[model_key]
            phases = list(stats['phases'].keys())
            last_phase = max(phases)
            
            if last_phase < 5:
                last_coop = stats['phases'][last_phase]['coop_rate']
                last_score = stats['phases'][last_phase]['avg_score']
                print(f"{stats['clean_name']} (T={stats['temperature']}):")
                print(f"  - Last seen: Phase {last_phase}")
                print(f"  - Final cooperation rate: {last_coop:.1%}")
                print(f"  - Final avg score: {last_score:.3f}")
                print(f"  - Reason for elimination: Too cooperative in defection-dominant environment")
    else:
        print("\n⚠️ NO MISTRAL MODELS FOUND IN DATA")
    
    # Complete survival analysis
    print("\n\n" + "="*60)
    print("COMPLETE SURVIVAL ANALYSIS - ALL PROVIDERS")
    print("="*60)
    
    # Models surviving all phases
    survivors = []
    early_exits = []
    
    for key, stats in all_llm_stats.items():
        phases = list(stats['phases'].keys())
        if len(phases) == 5:
            survivors.append((key, stats))
        elif max(phases) <= 2:
            early_exits.append((key, stats, max(phases)))
    
    print(f"\n✅ LLMs Surviving All 5 Phases: {len(survivors)}")
    for key, stats in sorted(survivors, key=lambda x: x[1]['provider']):
        avg_scores = [stats['phases'][p]['avg_score'] for p in range(1, 6)]
        avg_coop = [stats['phases'][p]['coop_rate'] for p in range(1, 6)]
        print(f"  • {stats['provider']:<10} - {stats['clean_name']:<25} (T={stats['temperature']})")
        print(f"    Score evolution: {' → '.join(f'{s:.2f}' for s in avg_scores)}")
        print(f"    Coop evolution:  {' → '.join(f'{c:.0%}' for c in avg_coop)}")
    
    print(f"\n❌ LLMs Eliminated by Phase 2: {len(early_exits)}")
    for key, stats, last_phase in sorted(early_exits, key=lambda x: (x[2], x[1]['provider'])):
        last_coop = stats['phases'][last_phase]['coop_rate']
        print(f"  • {stats['provider']:<10} - {stats['clean_name']:<25} (T={stats['temperature']})")
        print(f"    Eliminated: Phase {last_phase}, Final coop rate: {last_coop:.1%}")
    
    # Final ranking
    print("\n\n" + "="*60)
    print("FINAL LLM RANKING BY AVERAGE PERFORMANCE")
    print("="*60)
    
    rankings = []
    for key, stats in all_llm_stats.items():
        all_scores = []
        all_coop = []
        for phase_data in stats['phases'].values():
            all_scores.append(phase_data['avg_score'])
            all_coop.append(phase_data['coop_rate'])
        
        rankings.append({
            'name': f"{stats['clean_name']} (T={stats['temperature']})",
            'provider': stats['provider'],
            'avg_score': np.mean(all_scores),
            'avg_coop': np.mean(all_coop),
            'phases': len(stats['phases'])
        })
    
    rankings.sort(key=lambda x: x['avg_score'], reverse=True)
    
    print(f"\n{'Rank':<5} | {'Provider':<10} | {'Model':<35} | {'Score':<8} | {'Coop':<8} | {'Phases'}")
    print("-"*85)
    
    for rank, model in enumerate(rankings, 1):
        print(f"{rank:<5} | {model['provider']:<10} | {model['name']:<35} | "
              f"{model['avg_score']:<8.3f} | {model['avg_coop']:<8.1%} | {model['phases']}/5")

if __name__ == "__main__":
    comprehensive_llm_analysis()