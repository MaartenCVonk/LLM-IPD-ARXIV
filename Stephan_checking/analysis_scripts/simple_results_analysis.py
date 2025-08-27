#!/usr/bin/env python3
"""Simple but comprehensive analysis of tournament results"""

import pandas as pd
import numpy as np
import json
from pathlib import Path

def load_data():
    """Load available tournament data"""
    results = {}
    exp_path = Path('results/experiment_20250811_131553')
    
    # Load phases
    for phase in range(1, 6):
        file = exp_path / f'evolutionary_shadow75_phase{phase}.csv' 
        if file.exists():
            results[f'phase{phase}'] = pd.read_csv(file)
            
    return results

def analyze_tournament(data):
    """Comprehensive analysis of tournament data"""
    
    print("\n" + "="*80)
    print("IPD TOURNAMENT ANALYSIS - SHADOW 75%")
    print("="*80)
    
    all_agents = set()
    phase_stats = {}
    
    for phase_name, df in data.items():
        phase_num = int(phase_name.replace('phase', ''))
        
        # Basic stats
        agents = set(df['agent1'].unique()) | set(df['agent2'].unique())
        all_agents.update(agents)
        
        # Clean agent names (remove _p1i1 suffixes)
        clean_agents = set()
        for agent in agents:
            clean_name = agent.replace('_p1i1', '').replace('_p2i1', '').replace('_p3i1', '')
            clean_name = clean_name.replace('_p4i1', '').replace('_p5i1', '')
            clean_agents.add(clean_name)
        
        # Calculate scores
        agent_scores = {}
        agent_coop = {}
        agent_rounds = {}
        
        for agent in agents:
            agent_scores[agent] = []
            agent_coop[agent] = []
            agent_rounds[agent] = 0
        
        # Process each round
        for _, row in df.iterrows():
            a1, a2 = row['agent1'], row['agent2']
            m1, m2 = row['agent1_move'], row['agent2_move']
            
            # Calculate payoffs
            if (m1, m2) == ('C', 'C'):
                s1, s2 = 3, 3
            elif (m1, m2) == ('C', 'D'):
                s1, s2 = 0, 5
            elif (m1, m2) == ('D', 'C'):
                s1, s2 = 5, 0
            else:
                s1, s2 = 1, 1
            
            agent_scores[a1].append(s1)
            agent_scores[a2].append(s2)
            agent_coop[a1].append(1 if m1 == 'C' else 0)
            agent_coop[a2].append(1 if m2 == 'C' else 0)
            agent_rounds[a1] += 1
            agent_rounds[a2] += 1
        
        # Summary stats
        phase_stats[phase_num] = {
            'num_agents': len(clean_agents),
            'num_matches': df['match_id'].nunique(),
            'total_rounds': len(df),
            'avg_rounds_per_match': df.groupby('match_id')['round'].max().mean(),
            'agent_performance': {}
        }
        
        # Agent performance
        for agent in agents:
            clean_name = agent.replace('_p1i1', '').replace('_p2i1', '').replace('_p3i1', '')
            clean_name = clean_name.replace('_p4i1', '').replace('_p5i1', '')
            
            if agent_scores[agent]:
                phase_stats[phase_num]['agent_performance'][clean_name] = {
                    'avg_score': np.mean(agent_scores[agent]),
                    'total_score': sum(agent_scores[agent]),
                    'coop_rate': np.mean(agent_coop[agent]),
                    'rounds_played': agent_rounds[agent]
                }
        
        print(f"\n📊 PHASE {phase_num}")
        print(f"{'='*40}")
        print(f"Active Agents: {phase_stats[phase_num]['num_agents']}")
        print(f"Total Matches: {phase_stats[phase_num]['num_matches']}")
        print(f"Total Rounds: {phase_stats[phase_num]['total_rounds']}")
        print(f"Avg Rounds/Match: {phase_stats[phase_num]['avg_rounds_per_match']:.2f}")
        
        # Top performers
        perf = phase_stats[phase_num]['agent_performance']
        sorted_agents = sorted(perf.items(), key=lambda x: x[1]['avg_score'], reverse=True)
        
        print(f"\n🏆 Top 5 Agents by Average Score:")
        for i, (agent, stats) in enumerate(sorted_agents[:5], 1):
            print(f"   {i}. {agent[:30]:<30} Score: {stats['avg_score']:.3f} Coop: {stats['coop_rate']:.2%}")
        
        print(f"\n🤝 Most Cooperative Agents:")
        sorted_coop = sorted(perf.items(), key=lambda x: x[1]['coop_rate'], reverse=True)
        for i, (agent, stats) in enumerate(sorted_coop[:3], 1):
            print(f"   {i}. {agent[:30]:<30} Coop: {stats['coop_rate']:.2%} Score: {stats['avg_score']:.3f}")
        
        print(f"\n⚔️ Most Defective Agents:")
        for i, (agent, stats) in enumerate(sorted_coop[-3:], 1):
            print(f"   {i}. {agent[:30]:<30} Coop: {stats['coop_rate']:.2%} Score: {stats['avg_score']:.3f}")
    
    # Cross-phase analysis
    print(f"\n{'='*80}")
    print("CROSS-PHASE ANALYSIS")
    print(f"{'='*80}")
    
    # Track agent survival
    agent_phases = {}
    for phase_num, stats in phase_stats.items():
        for agent in stats['agent_performance']:
            if agent not in agent_phases:
                agent_phases[agent] = []
            agent_phases[agent].append(phase_num)
    
    # Categorize agents
    def categorize(name):
        name_lower = name.lower()
        if 'claude' in name_lower or 'anthropic' in name_lower:
            return 'Anthropic'
        elif 'gpt' in name_lower or 'o3' in name_lower:
            return 'OpenAI'
        elif 'mistral' in name_lower:
            return 'Mistral'
        elif 'gemini' in name_lower:
            return 'Gemini'
        elif any(x in name_lower for x in ['thompson', 'qlearning', 'gradient', 'meta']):
            return 'Adaptive'
        else:
            return 'Classical'
    
    # Category performance
    category_scores = {phase: {} for phase in range(1, 6)}
    for phase_num, stats in phase_stats.items():
        for agent, perf in stats['agent_performance'].items():
            cat = categorize(agent)
            if cat not in category_scores[phase_num]:
                category_scores[phase_num][cat] = []
            category_scores[phase_num][cat].append(perf['avg_score'])
    
    print("\n📈 Category Performance Evolution:")
    categories = ['Classical', 'Adaptive', 'Anthropic', 'OpenAI', 'Mistral', 'Gemini']
    
    for cat in categories:
        scores_by_phase = []
        for phase in range(1, 6):
            if phase in category_scores and cat in category_scores[phase]:
                avg = np.mean(category_scores[phase][cat])
                scores_by_phase.append(f"{avg:.2f}")
            else:
                scores_by_phase.append("--")
        
        print(f"   {cat:12} | " + " | ".join(f"P{i}: {s:5}" for i, s in enumerate(scores_by_phase, 1)))
    
    # Survival analysis
    survivors_all = [agent for agent, phases in agent_phases.items() if len(phases) == 5]
    eliminated_early = [agent for agent, phases in agent_phases.items() if max(phases) <= 2]
    
    print(f"\n🏅 Agents Surviving All 5 Phases: {len(survivors_all)}")
    for agent in sorted(survivors_all)[:10]:
        phases = agent_phases[agent]
        avg_scores = []
        for p in phases:
            if agent in phase_stats[p]['agent_performance']:
                avg_scores.append(phase_stats[p]['agent_performance'][agent]['avg_score'])
        if avg_scores:
            print(f"   • {agent[:40]} (Avg: {np.mean(avg_scores):.3f})")
    
    print(f"\n❌ Agents Eliminated Early (Phase ≤2): {len(eliminated_early)}")
    for agent in sorted(eliminated_early)[:5]:
        phases = agent_phases[agent]
        print(f"   • {agent[:40]} (Phases: {phases})")
    
    # Performance trends
    print(f"\n📊 Overall Tournament Trends:")
    
    total_coop_by_phase = []
    avg_score_by_phase = []
    
    for phase in range(1, 6):
        if phase in phase_stats:
            all_scores = []
            all_coop = []
            for agent, perf in phase_stats[phase]['agent_performance'].items():
                all_scores.append(perf['avg_score'])
                all_coop.append(perf['coop_rate'])
            
            total_coop_by_phase.append(np.mean(all_coop))
            avg_score_by_phase.append(np.mean(all_scores))
    
    print(f"   Average Score:      " + " → ".join(f"{s:.2f}" for s in avg_score_by_phase))
    print(f"   Cooperation Rate:   " + " → ".join(f"{c:.1%}" for c in total_coop_by_phase))
    
    # Most improved/declined
    print(f"\n📈 Most Improved Agents (Phase 1→5):")
    improvements = []
    for agent in agent_phases:
        if 1 in agent_phases[agent] and 5 in agent_phases[agent]:
            if agent in phase_stats[1]['agent_performance'] and agent in phase_stats[5]['agent_performance']:
                score1 = phase_stats[1]['agent_performance'][agent]['avg_score']
                score5 = phase_stats[5]['agent_performance'][agent]['avg_score']
                improvements.append((agent, score5 - score1, score1, score5))
    
    improvements.sort(key=lambda x: x[1], reverse=True)
    for agent, improvement, s1, s5 in improvements[:3]:
        print(f"   • {agent[:30]} (+{improvement:.3f}): {s1:.3f} → {s5:.3f}")
    
    print(f"\n📉 Most Declined Agents (Phase 1→5):")
    for agent, decline, s1, s5 in improvements[-3:]:
        if decline < 0:
            print(f"   • {agent[:30]} ({decline:.3f}): {s1:.3f} → {s5:.3f}")
    
    print(f"\n{'='*80}")
    print("ANALYSIS COMPLETE")
    print(f"{'='*80}\n")

# Run analysis
if __name__ == "__main__":
    print("Loading tournament data...")
    data = load_data()
    
    if data:
        print(f"Found {len(data)} phases of data")
        analyze_tournament(data)
    else:
        print("No data found in results folder")