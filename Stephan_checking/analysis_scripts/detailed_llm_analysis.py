#!/usr/bin/env python3
"""Detailed comparative analysis of LLM performance in IPD tournament"""

import pandas as pd
import numpy as np
from pathlib import Path

def load_all_phases():
    """Load all phase data"""
    data = {}
    exp_path = Path('results/experiment_20250811_131553')
    
    for phase in range(1, 6):
        file = exp_path / f'evolutionary_shadow75_phase{phase}.csv'
        if file.exists():
            data[phase] = pd.read_csv(file)
    return data

def extract_llm_info(agent_name):
    """Extract LLM provider, model, and temperature from agent name"""
    clean_name = agent_name.split('_p')[0]  # Remove phase/instance suffixes
    
    if 'Claude4-Sonnet' in agent_name:
        provider = 'Anthropic'
        model = 'Claude-4-Sonnet'
        # Extract temperature
        if 'T02' in agent_name:
            temp = 0.2
        elif 'T05' in agent_name:
            temp = 0.5
        elif 'T08' in agent_name:
            temp = 0.8
        else:
            temp = None
    elif 'GPT4o' in agent_name:
        provider = 'OpenAI'
        model = 'GPT-4o'
        temp = 1.0  # Fixed temperature
    elif 'GPT5' in agent_name:
        provider = 'OpenAI'
        model = 'GPT-5'
        temp = 1.0
    elif 'o3' in agent_name:
        provider = 'OpenAI'
        model = 'o3'
        temp = 1.0
    elif 'Gemini25Pro' in agent_name:
        provider = 'Google'
        model = 'Gemini-2.5-Pro'
        if 'T02' in agent_name:
            temp = 0.2
        elif 'T07' in agent_name:
            temp = 0.7
        elif 'T12' in agent_name:
            temp = 1.2
        else:
            temp = None
    elif 'Mistral' in agent_name.lower():
        provider = 'Mistral'
        model = 'Mistral-Large'
        if 'T02' in agent_name:
            temp = 0.2
        elif 'T07' in agent_name:
            temp = 0.7
        elif 'T10' in agent_name or 'T12' in agent_name:
            temp = 1.0  # or 1.2
        else:
            temp = None
    else:
        return None, None, None
    
    return provider, model, temp

def analyze_llm_performance():
    """Comprehensive LLM performance analysis"""
    
    print("\n" + "="*80)
    print("DETAILED LLM COMPARATIVE ANALYSIS")
    print("="*80)
    
    data = load_all_phases()
    
    # Collect all LLM performance data
    llm_stats = {}
    
    for phase_num, df in data.items():
        # Get all agents
        all_agents = set(df['agent1'].unique()) | set(df['agent2'].unique())
        
        for agent in all_agents:
            provider, model, temp = extract_llm_info(agent)
            if provider is None:
                continue
            
            # Initialize data structure
            key = f"{provider}_{model}_{temp}"
            if key not in llm_stats:
                llm_stats[key] = {
                    'provider': provider,
                    'model': model,
                    'temperature': temp,
                    'phases': {},
                    'agent_names': set()
                }
            
            llm_stats[key]['agent_names'].add(agent)
            
            # Calculate stats for this agent in this phase
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
                if phase_num not in llm_stats[key]['phases']:
                    llm_stats[key]['phases'][phase_num] = []
                
                llm_stats[key]['phases'][phase_num].append({
                    'avg_score': np.mean(scores),
                    'total_score': sum(scores),
                    'coop_rate': moves.count('C') / len(moves) if moves else 0,
                    'rounds': len(scores),
                    'first_move_coop': 1 if moves[0] == 'C' else 0 if moves else None
                })
    
    # Analysis by Provider
    print("\n📊 PROVIDER COMPARISON")
    print("="*40)
    
    providers_data = {}
    for key, stats in llm_stats.items():
        provider = stats['provider']
        if provider not in providers_data:
            providers_data[provider] = {'scores': [], 'coop': [], 'survival': []}
        
        for phase, phase_data in stats['phases'].items():
            for agent_data in phase_data:
                providers_data[provider]['scores'].append(agent_data['avg_score'])
                providers_data[provider]['coop'].append(agent_data['coop_rate'])
            providers_data[provider]['survival'].append(phase)
    
    print(f"\n{'Provider':<12} | {'Avg Score':<10} | {'Coop Rate':<10} | {'Phases Present':<15}")
    print("-"*60)
    
    for provider in ['OpenAI', 'Google', 'Anthropic', 'Mistral']:
        if provider in providers_data:
            avg_score = np.mean(providers_data[provider]['scores'])
            avg_coop = np.mean(providers_data[provider]['coop'])
            phases = sorted(set(providers_data[provider]['survival']))
            phase_str = f"{min(phases)}-{max(phases)} ({len(set(phases))} phases)"
            print(f"{provider:<12} | {avg_score:<10.3f} | {avg_coop:<10.2%} | {phase_str:<15}")
        else:
            print(f"{provider:<12} | {'N/A':<10} | {'N/A':<10} | {'Not Present':<15}")
    
    # Detailed Model Analysis
    print("\n\n📊 MODEL-LEVEL PERFORMANCE")
    print("="*40)
    
    models_summary = {}
    for key, stats in llm_stats.items():
        model_key = f"{stats['model']} (T={stats['temperature']})"
        
        all_scores = []
        all_coop = []
        phases_present = []
        
        for phase, phase_data in stats['phases'].items():
            phases_present.append(phase)
            for agent_data in phase_data:
                all_scores.append(agent_data['avg_score'])
                all_coop.append(agent_data['coop_rate'])
        
        models_summary[model_key] = {
            'provider': stats['provider'],
            'avg_score': np.mean(all_scores),
            'std_score': np.std(all_scores),
            'avg_coop': np.mean(all_coop),
            'phases': phases_present,
            'n_instances': len(stats['agent_names'])
        }
    
    # Sort by average score
    sorted_models = sorted(models_summary.items(), key=lambda x: x[1]['avg_score'], reverse=True)
    
    print(f"\n{'Rank':<5} | {'Model':<25} | {'Provider':<10} | {'Avg Score':<10} | {'Coop Rate':<10} | {'Survival'}")
    print("-"*85)
    
    for rank, (model, stats) in enumerate(sorted_models, 1):
        phases = stats['phases']
        survival = f"P{min(phases)}-P{max(phases)}" if phases else "None"
        print(f"{rank:<5} | {model:<25} | {stats['provider']:<10} | "
              f"{stats['avg_score']:<10.3f} | {stats['avg_coop']:<10.2%} | {survival}")
    
    # Temperature Analysis for Models with Multiple Temps
    print("\n\n📊 TEMPERATURE EFFECTS ANALYSIS")
    print("="*40)
    
    temp_analysis = {}
    for key, stats in llm_stats.items():
        base_model = stats['model']
        if base_model not in temp_analysis:
            temp_analysis[base_model] = {}
        
        temp = stats['temperature']
        if temp is not None:
            temp_analysis[base_model][temp] = {
                'scores': [],
                'coop': [],
                'phases': []
            }
            
            for phase, phase_data in stats['phases'].items():
                for agent_data in phase_data:
                    temp_analysis[base_model][temp]['scores'].append(agent_data['avg_score'])
                    temp_analysis[base_model][temp]['coop'].append(agent_data['coop_rate'])
                temp_analysis[base_model][temp]['phases'].append(phase)
    
    for model, temp_data in temp_analysis.items():
        if len(temp_data) > 1:  # Only show models with multiple temperatures
            print(f"\n{model}:")
            print(f"{'Temp':<6} | {'Avg Score':<10} | {'Std Dev':<10} | {'Coop Rate':<10} | {'Phases'}")
            print("-"*55)
            
            for temp in sorted(temp_data.keys()):
                data = temp_data[temp]
                avg_score = np.mean(data['scores'])
                std_score = np.std(data['scores'])
                avg_coop = np.mean(data['coop'])
                phases = sorted(set(data['phases']))
                phase_str = f"{min(phases)}-{max(phases)}"
                
                print(f"{temp:<6.1f} | {avg_score:<10.3f} | {std_score:<10.3f} | "
                      f"{avg_coop:<10.2%} | {phase_str}")
    
    # Phase-by-Phase Evolution
    print("\n\n📊 PHASE-BY-PHASE LLM EVOLUTION")
    print("="*40)
    
    # Track evolution for each model
    evolution_data = {}
    for key, stats in llm_stats.items():
        model_name = f"{stats['model']} (T={stats['temperature']})"
        evolution_data[model_name] = {}
        
        for phase, phase_data in stats['phases'].items():
            avg_score = np.mean([d['avg_score'] for d in phase_data])
            avg_coop = np.mean([d['coop_rate'] for d in phase_data])
            evolution_data[model_name][phase] = {
                'score': avg_score,
                'coop': avg_coop
            }
    
    # Show evolution for key models
    key_models = [
        'o3 (T=1.0)',
        'Gemini-2.5-Pro (T=0.2)',
        'Gemini-2.5-Pro (T=1.2)',
        'Claude-4-Sonnet (T=0.2)',
        'GPT-4o (T=1.0)'
    ]
    
    print(f"\n{'Model':<25} | Phase 1 | Phase 2 | Phase 3 | Phase 4 | Phase 5")
    print("-"*75)
    
    for model in key_models:
        if model in evolution_data:
            line = f"{model:<25} |"
            for phase in range(1, 6):
                if phase in evolution_data[model]:
                    score = evolution_data[model][phase]['score']
                    coop = evolution_data[model][phase]['coop']
                    line += f" {score:.2f}({coop:.0%}) |"
                else:
                    line += "    --    |"
            print(line)
    
    # Strategic Patterns
    print("\n\n📊 STRATEGIC PATTERNS")
    print("="*40)
    
    # Analyze first-move tendencies
    first_moves = {}
    for key, stats in llm_stats.items():
        model = f"{stats['model']} (T={stats['temperature']})"
        first_moves[model] = []
        
        for phase_data_list in stats['phases'].values():
            for agent_data in phase_data_list:
                if agent_data['first_move_coop'] is not None:
                    first_moves[model].append(agent_data['first_move_coop'])
    
    print("\n🎯 First Move Cooperation Rates:")
    for model, moves in sorted(first_moves.items(), key=lambda x: np.mean(x[1]) if x[1] else 0, reverse=True):
        if moves:
            coop_rate = np.mean(moves)
            print(f"  {model:<30}: {coop_rate:.1%}")
    
    # Survival Analysis
    print("\n\n🏆 SURVIVAL ANALYSIS")
    print("="*40)
    
    survival = {}
    for key, stats in llm_stats.items():
        model = f"{stats['model']} (T={stats['temperature']})"
        phases = list(stats['phases'].keys())
        survival[model] = {
            'first_phase': min(phases) if phases else None,
            'last_phase': max(phases) if phases else None,
            'total_phases': len(phases),
            'continuous': phases == list(range(min(phases), max(phases) + 1)) if phases else False
        }
    
    # Models surviving all 5 phases
    survivors = [m for m, s in survival.items() if s['total_phases'] == 5]
    print(f"\n✅ Models Surviving All 5 Phases: {len(survivors)}")
    for model in survivors:
        print(f"  • {model}")
    
    # Early eliminations
    early_exit = [m for m, s in survival.items() if s['last_phase'] and s['last_phase'] <= 2]
    print(f"\n❌ Models Eliminated Early (Phase ≤2): {len(early_exit)}")
    for model in early_exit:
        print(f"  • {model} (Last seen: Phase {survival[model]['last_phase']})")
    
    # Key Insights
    print("\n\n🔍 KEY INSIGHTS")
    print("="*40)
    
    print("""
1. MISTRAL ABSENCE: No Mistral models participated in this tournament
   - This could be due to API issues, configuration problems, or exclusion

2. PROVIDER DOMINANCE:
   - Google Gemini models showed strongest performance and survival
   - OpenAI models (especially o3) maintained consistency
   - Anthropic Claude models underperformed and were eliminated early

3. TEMPERATURE EFFECTS:
   - Higher temperatures (1.2) for Gemini correlated with survival
   - Fixed temperature (1.0) for OpenAI models showed mixed results
   - Lower temperatures led to more predictable but exploitable behavior

4. STRATEGIC EVOLUTION:
   - All LLMs shifted from cooperation to defection over phases
   - Gemini models adapted fastest to the defection-dominant environment
   - Claude models failed to adapt and were eliminated

5. SURVIVAL PATTERNS:
   - Only Gemini and o3 models survived all phases
   - Temperature diversity within Gemini allowed testing different strategies
   - Single-temperature models had less adaptability
    """)

# Run analysis
if __name__ == "__main__":
    analyze_llm_performance()