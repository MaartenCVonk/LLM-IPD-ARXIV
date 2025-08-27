#!/usr/bin/env python3
"""
Generate all comprehensive visualizations for the tournament analysis.
Creates both light and dark versions at multiple DPI settings.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

# Configure matplotlib for better rendering
plt.rcParams['figure.max_open_warning'] = 50
plt.rcParams['svg.fonttype'] = 'none'

def load_all_tournament_data():
    """Load and process all tournament data"""
    
    base_path = Path("/mnt/c/Apps/LLM-IPD-ARXIV/results/experiment_20250811_131553")
    all_data = {}
    
    for phase in range(1, 6):
        csv_file = base_path / f"evolutionary_shadow75_phase{phase}.csv"
        df = pd.read_csv(csv_file)
        all_data[phase] = df
    
    return all_data

def extract_detailed_stats(all_data):
    """Extract comprehensive statistics from all data"""
    
    # Agent performance tracking
    agent_stats = defaultdict(lambda: {
        'scores': [], 'cooperations': 0, 'defections': 0, 
        'phases': set(), 'matches': 0, 'provider': None
    })
    
    # Phase-by-phase analysis
    phase_analysis = {}
    
    for phase, df in all_data.items():
        # Get unique agents and their stats
        phase_agents = set()
        phase_coop_rate = 0
        phase_scores = []
        
        for _, row in df.iterrows():
            # Process agent1
            agent1 = row['agent1'].split('_p')[0] if '_p' in row['agent1'] else row['agent1']
            phase_agents.add(agent1)
            agent_stats[agent1]['scores'].append(row['agent1_total_score'])
            agent_stats[agent1]['phases'].add(phase)
            agent_stats[agent1]['matches'] += 1
            
            if row['agent1_move'] == 'C':
                agent_stats[agent1]['cooperations'] += 1
            else:
                agent_stats[agent1]['defections'] += 1
            
            # Process agent2
            agent2 = row['agent2'].split('_p')[0] if '_p' in row['agent2'] else row['agent2']
            phase_agents.add(agent2)
            agent_stats[agent2]['scores'].append(row['agent2_total_score'])
            agent_stats[agent2]['phases'].add(phase)
            agent_stats[agent2]['matches'] += 1
            
            if row['agent2_move'] == 'C':
                agent_stats[agent2]['cooperations'] += 1
            else:
                agent_stats[agent2]['defections'] += 1
            
            phase_scores.extend([row['agent1_total_score'], row['agent2_total_score']])
        
        # Calculate phase cooperation rate
        total_moves = len(df) * 2
        coop_moves = (df['agent1_move'] == 'C').sum() + (df['agent2_move'] == 'C').sum()
        phase_coop_rate = coop_moves / total_moves if total_moves > 0 else 0
        
        phase_analysis[phase] = {
            'agents': phase_agents,
            'n_agents': len(phase_agents),
            'cooperation_rate': phase_coop_rate,
            'avg_score': np.mean(phase_scores) if phase_scores else 0,
            'n_matches': len(df)
        }
    
    # Identify providers
    for agent, stats in agent_stats.items():
        if any(x in agent for x in ['GPT', 'o3', 'o1']):
            stats['provider'] = 'OpenAI'
        elif 'Claude' in agent:
            stats['provider'] = 'Anthropic'
        elif any(x in agent for x in ['Mistral', 'Ministral']):
            stats['provider'] = 'Mistral'
        elif 'Gemini' in agent:
            stats['provider'] = 'Google'
        else:
            stats['provider'] = 'Classical'
        
        # Calculate derived stats
        total_moves = stats['cooperations'] + stats['defections']
        stats['cooperation_rate'] = stats['cooperations'] / total_moves if total_moves > 0 else 0
        stats['avg_score'] = np.mean(stats['scores']) if stats['scores'] else 0
        stats['max_phase'] = max(stats['phases']) if stats['phases'] else 0
    
    return dict(agent_stats), phase_analysis

def create_evolution_visualization(phase_analysis, agent_stats):
    """Create population evolution visualization"""
    
    viz_dir = Path("/mnt/c/Apps/LLM-IPD-ARXIV/Stephan_checking/visualizations")
    viz_dir.mkdir(exist_ok=True)
    
    # Prepare data
    phases = sorted(phase_analysis.keys())
    
    # Count agents by provider per phase
    provider_counts = defaultdict(list)
    for phase in phases:
        phase_agents = phase_analysis[phase]['agents']
        phase_provider_count = defaultdict(int)
        
        for agent in phase_agents:
            if agent in agent_stats:
                provider = agent_stats[agent]['provider']
                if provider != 'Classical':
                    phase_provider_count[provider] += 1
        
        for provider in ['OpenAI', 'Anthropic', 'Mistral', 'Google']:
            provider_counts[provider].append(phase_provider_count.get(provider, 0))
    
    # Create figure with subplots
    fig = plt.figure(figsize=(16, 12))
    
    # 1. Stacked area chart for provider evolution
    ax1 = plt.subplot(3, 2, 1)
    colors = {'OpenAI': '#00A67E', 'Anthropic': '#7C65C7', 
             'Mistral': '#FF6B00', 'Google': '#4285F4'}
    
    bottom = np.zeros(len(phases))
    for provider in ['OpenAI', 'Anthropic', 'Mistral', 'Google']:
        counts = provider_counts[provider]
        ax1.fill_between(phases, bottom, bottom + np.array(counts), 
                        label=provider, color=colors[provider], alpha=0.7)
        bottom += np.array(counts)
    
    ax1.set_xlabel('Phase', fontsize=11)
    ax1.set_ylabel('Number of Agent Types', fontsize=11)
    ax1.set_title('Provider Representation Evolution', fontsize=13, fontweight='bold')
    ax1.legend(loc='upper right')
    ax1.grid(True, alpha=0.3)
    ax1.set_xticks(phases)
    
    # Mark Mistral extinction
    ax1.axvline(x=2.5, color='darkred', linestyle='--', alpha=0.5)
    ax1.text(2.5, ax1.get_ylim()[1]*0.9, 'Mistral\nExtinct', 
            ha='center', fontsize=10, color='darkred', fontweight='bold')
    
    # 2. Cooperation rate evolution
    ax2 = plt.subplot(3, 2, 2)
    coop_rates = [phase_analysis[p]['cooperation_rate'] * 100 for p in phases]
    
    ax2.plot(phases, coop_rates, 'o-', linewidth=3, markersize=10, color='coral')
    ax2.fill_between(phases, 0, coop_rates, alpha=0.3, color='coral')
    
    for i, rate in enumerate(coop_rates, 1):
        ax2.text(i, rate + 2, f'{rate:.1f}%', ha='center', fontsize=9)
    
    ax2.set_xlabel('Phase', fontsize=11)
    ax2.set_ylabel('Cooperation Rate (%)', fontsize=11)
    ax2.set_title('Cooperation Collapse Over Time', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.set_xticks(phases)
    ax2.set_ylim([0, max(coop_rates) * 1.2])
    
    # 3. Average score evolution
    ax3 = plt.subplot(3, 2, 3)
    avg_scores = [phase_analysis[p]['avg_score'] for p in phases]
    
    ax3.bar(phases, avg_scores, color='steelblue', alpha=0.7)
    ax3.set_xlabel('Phase', fontsize=11)
    ax3.set_ylabel('Average Score per Move', fontsize=11)
    ax3.set_title('Average Performance Evolution', fontsize=13, fontweight='bold')
    ax3.grid(axis='y', alpha=0.3)
    ax3.set_xticks(phases)
    
    for i, score in enumerate(avg_scores, 1):
        ax3.text(i, score + 0.05, f'{score:.2f}', ha='center', fontsize=9)
    
    # 4. Survival analysis by provider
    ax4 = plt.subplot(3, 2, 4)
    
    survival_matrix = []
    providers_list = ['OpenAI', 'Anthropic', 'Mistral', 'Google']
    
    for provider in providers_list:
        row = []
        for phase in phases:
            count = provider_counts[provider][phase - 1]
            row.append(1 if count > 0 else 0)
        survival_matrix.append(row)
    
    im = ax4.imshow(survival_matrix, cmap='RdYlGn', aspect='auto', vmin=0, vmax=1)
    ax4.set_xticks(range(len(phases)))
    ax4.set_xticklabels([f'P{p}' for p in phases])
    ax4.set_yticks(range(len(providers_list)))
    ax4.set_yticklabels(providers_list)
    ax4.set_xlabel('Phase', fontsize=11)
    ax4.set_title('Provider Survival Matrix', fontsize=13, fontweight='bold')
    
    # Add text annotations
    for i, provider in enumerate(providers_list):
        for j, phase in enumerate(phases):
            val = survival_matrix[i][j]
            color = 'white' if val == 0 else 'black'
            text = '✓' if val == 1 else '✗'
            ax4.text(j, i, text, ha='center', va='center', color=color, fontsize=12)
    
    # 5. Top performers
    ax5 = plt.subplot(3, 2, 5)
    
    # Get top 10 agents by average score
    sorted_agents = sorted(agent_stats.items(), 
                          key=lambda x: x[1]['avg_score'], reverse=True)[:10]
    
    agent_names = [a[0][:15] for a in sorted_agents]
    scores = [a[1]['avg_score'] for a in sorted_agents]
    providers = [a[1]['provider'] for a in sorted_agents]
    
    bar_colors = [colors.get(p, 'gray') for p in providers]
    
    y_pos = np.arange(len(agent_names))
    ax5.barh(y_pos, scores, color=bar_colors, alpha=0.7)
    ax5.set_yticks(y_pos)
    ax5.set_yticklabels(agent_names, fontsize=9)
    ax5.invert_yaxis()
    ax5.set_xlabel('Average Score', fontsize=11)
    ax5.set_title('Top 10 Performing Agents', fontsize=13, fontweight='bold')
    ax5.grid(axis='x', alpha=0.3)
    
    # 6. Cooperation vs Performance scatter
    ax6 = plt.subplot(3, 2, 6)
    
    # Prepare data for scatter plot
    for provider in ['OpenAI', 'Anthropic', 'Mistral', 'Google']:
        provider_agents = [(a, s) for a, s in agent_stats.items() 
                          if s['provider'] == provider]
        
        if provider_agents:
            x = [s['cooperation_rate'] * 100 for _, s in provider_agents]
            y = [s['avg_score'] for _, s in provider_agents]
            
            ax6.scatter(x, y, label=provider, color=colors[provider], 
                       s=100, alpha=0.6, edgecolors='black', linewidth=0.5)
    
    ax6.set_xlabel('Cooperation Rate (%)', fontsize=11)
    ax6.set_ylabel('Average Score', fontsize=11)
    ax6.set_title('Cooperation vs Performance by Provider', fontsize=13, fontweight='bold')
    ax6.legend(loc='best', fontsize=9)
    ax6.grid(True, alpha=0.3)
    
    # Add trend line
    all_coop = [s['cooperation_rate'] * 100 for s in agent_stats.values()]
    all_scores = [s['avg_score'] for s in agent_stats.values()]
    if len(all_coop) > 1:
        z = np.polyfit(all_coop, all_scores, 1)
        p = np.poly1d(z)
        x_trend = np.linspace(0, 100, 100)
        ax6.plot(x_trend, p(x_trend), 'r--', alpha=0.5, linewidth=2)
    
    plt.suptitle('Complete Tournament Analysis - Shadow 75%', 
                fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()
    
    # Save the figure
    for dpi in [300, 1200]:
        filename = viz_dir / f"complete_analysis_{dpi}dpi.png"
        plt.savefig(filename, dpi=dpi, bbox_inches='tight')
        print(f"  Saved: complete_analysis_{dpi}dpi.png")
    
    filename = viz_dir / "complete_analysis.svg"
    plt.savefig(filename, format='svg', bbox_inches='tight')
    print(f"  Saved: complete_analysis.svg")
    
    plt.close()

def create_mistral_focused_visualization(agent_stats, phase_analysis):
    """Create Mistral-specific visualizations"""
    
    viz_dir = Path("/mnt/c/Apps/LLM-IPD-ARXIV/Stephan_checking/visualizations")
    
    # Get Mistral agents
    mistral_agents = {a: s for a, s in agent_stats.items() 
                     if s['provider'] == 'Mistral'}
    
    if not mistral_agents:
        print("  No Mistral agents to visualize")
        return
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 12))
    
    # 1. Mistral cooperation rates
    names = list(mistral_agents.keys())
    coop_rates = [s['cooperation_rate'] * 100 for s in mistral_agents.values()]
    
    bars = ax1.bar(range(len(names)), coop_rates, color='#FF6B00', alpha=0.7)
    ax1.set_xticks(range(len(names)))
    ax1.set_xticklabels([n[:15] for n in names], rotation=45, ha='right')
    ax1.set_ylabel('Cooperation Rate (%)', fontsize=11)
    ax1.set_title('Mistral Agent Cooperation Rates', fontsize=13, fontweight='bold')
    ax1.grid(axis='y', alpha=0.3)
    
    # Add value labels
    for bar, rate in zip(bars, coop_rates):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f'{rate:.1f}%', ha='center', fontsize=9)
    
    # Add average line
    avg_coop = np.mean(coop_rates)
    ax1.axhline(y=avg_coop, color='red', linestyle='--', alpha=0.5)
    ax1.text(len(names)-0.5, avg_coop, f'Avg: {avg_coop:.1f}%', 
            fontsize=10, color='red')
    
    # 2. Mistral scores
    scores = [s['avg_score'] for s in mistral_agents.values()]
    
    bars = ax2.bar(range(len(names)), scores, color='#FF6B00', alpha=0.7)
    ax2.set_xticks(range(len(names)))
    ax2.set_xticklabels([n[:15] for n in names], rotation=45, ha='right')
    ax2.set_ylabel('Average Score', fontsize=11)
    ax2.set_title('Mistral Agent Performance', fontsize=13, fontweight='bold')
    ax2.grid(axis='y', alpha=0.3)
    
    for bar, score in zip(bars, scores):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                f'{score:.2f}', ha='center', fontsize=9)
    
    # 3. Survival phases
    survival_phases = [s['max_phase'] for s in mistral_agents.values()]
    
    phase_counts = {i: survival_phases.count(i) for i in range(1, 6)}
    
    bars = ax3.bar(phase_counts.keys(), phase_counts.values(), 
                   color='#FF6B00', alpha=0.7)
    ax3.set_xlabel('Last Phase Survived', fontsize=11)
    ax3.set_ylabel('Number of Agents', fontsize=11)
    ax3.set_title('Mistral Extinction Timeline', fontsize=13, fontweight='bold')
    ax3.set_xticks(list(phase_counts.keys()))
    ax3.grid(axis='y', alpha=0.3)
    
    # Mark extinction point
    ax3.axvline(x=2.5, color='darkred', linestyle='--', alpha=0.5, linewidth=2)
    ax3.text(2.5, max(phase_counts.values())*0.8, 'EXTINCT →',
            ha='center', fontsize=11, fontweight='bold', color='darkred')
    
    # 4. Comparison with other providers
    provider_stats = defaultdict(lambda: {'coop': [], 'scores': []})
    
    for agent, stats in agent_stats.items():
        provider = stats['provider']
        if provider != 'Classical':
            provider_stats[provider]['coop'].append(stats['cooperation_rate'] * 100)
            provider_stats[provider]['scores'].append(stats['avg_score'])
    
    providers = ['OpenAI', 'Anthropic', 'Mistral', 'Google']
    avg_coops = []
    avg_scores = []
    
    for provider in providers:
        if provider in provider_stats and provider_stats[provider]['coop']:
            avg_coops.append(np.mean(provider_stats[provider]['coop']))
            avg_scores.append(np.mean(provider_stats[provider]['scores']))
        else:
            avg_coops.append(0)
            avg_scores.append(0)
    
    x = np.arange(len(providers))
    width = 0.35
    
    bars1 = ax4.bar(x - width/2, avg_coops, width, label='Cooperation %', 
                    color='coral', alpha=0.7)
    bars2 = ax4.bar(x + width/2, avg_scores, width, label='Avg Score', 
                    color='steelblue', alpha=0.7)
    
    ax4.set_xlabel('Provider', fontsize=11)
    ax4.set_ylabel('Value', fontsize=11)
    ax4.set_title('Provider Comparison', fontsize=13, fontweight='bold')
    ax4.set_xticks(x)
    ax4.set_xticklabels(providers)
    ax4.legend()
    ax4.grid(axis='y', alpha=0.3)
    
    # Highlight Mistral
    mistral_idx = providers.index('Mistral')
    ax4.axvspan(mistral_idx - 0.4, mistral_idx + 0.4, alpha=0.2, color='#FF6B00')
    
    plt.suptitle('Mistral Agent Analysis - Tournament Shadow 75%', 
                fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    # Save
    for dpi in [300, 1200]:
        filename = viz_dir / f"mistral_analysis_{dpi}dpi.png"
        plt.savefig(filename, dpi=dpi, bbox_inches='tight')
        print(f"  Saved: mistral_analysis_{dpi}dpi.png")
    
    filename = viz_dir / "mistral_analysis.svg"
    plt.savefig(filename, format='svg', bbox_inches='tight')
    print(f"  Saved: mistral_analysis.svg")
    
    plt.close()

def create_cooperation_heatmap(all_data, agent_stats):
    """Create cooperation heatmap between different agent types"""
    
    viz_dir = Path("/mnt/c/Apps/LLM-IPD-ARXIV/Stephan_checking/visualizations")
    
    # Build cooperation matrix
    coop_matrix = defaultdict(lambda: defaultdict(lambda: {'C': 0, 'D': 0}))
    
    for phase, df in all_data.items():
        for _, row in df.iterrows():
            agent1 = row['agent1'].split('_p')[0] if '_p' in row['agent1'] else row['agent1']
            agent2 = row['agent2'].split('_p')[0] if '_p' in row['agent2'] else row['agent2']
            
            # Get moves
            move1 = row['agent1_move']
            move2 = row['agent2_move']
            
            coop_matrix[agent1][agent2][move1] += 1
            coop_matrix[agent2][agent1][move2] += 1
    
    # Select top agents for visualization
    top_agents = sorted(agent_stats.keys(), 
                       key=lambda x: agent_stats[x]['matches'], reverse=True)[:20]
    
    # Build matrix for heatmap
    matrix_data = []
    for agent1 in top_agents:
        row = []
        for agent2 in top_agents:
            if agent1 == agent2:
                row.append(0)
            else:
                total = coop_matrix[agent1][agent2]['C'] + coop_matrix[agent1][agent2]['D']
                if total > 0:
                    coop_rate = coop_matrix[agent1][agent2]['C'] / total
                else:
                    coop_rate = 0
                row.append(coop_rate * 100)
        matrix_data.append(row)
    
    # Create heatmap
    fig, ax = plt.subplots(figsize=(14, 12))
    
    sns.heatmap(matrix_data, 
               xticklabels=[a[:15] for a in top_agents],
               yticklabels=[a[:15] for a in top_agents],
               cmap='RdYlGn',
               vmin=0, vmax=100,
               annot=False,
               cbar_kws={'label': 'Cooperation Rate (%)'},
               ax=ax)
    
    ax.set_title('Agent Cooperation Patterns (Top 20 Agents)', 
                fontsize=14, fontweight='bold')
    ax.set_xlabel('Opponent', fontsize=12)
    ax.set_ylabel('Agent', fontsize=12)
    
    # Rotate labels
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right', fontsize=8)
    plt.setp(ax.get_yticklabels(), rotation=0, fontsize=8)
    
    plt.tight_layout()
    
    # Save
    for dpi in [300, 1200]:
        filename = viz_dir / f"cooperation_heatmap_{dpi}dpi.png"
        plt.savefig(filename, dpi=dpi, bbox_inches='tight')
        print(f"  Saved: cooperation_heatmap_{dpi}dpi.png")
    
    filename = viz_dir / "cooperation_heatmap.svg"
    plt.savefig(filename, format='svg', bbox_inches='tight')
    print(f"  Saved: cooperation_heatmap.svg")
    
    plt.close()

def main():
    """Generate all visualizations"""
    
    print("\n📊 Generating comprehensive visualizations...")
    
    # Load all data
    all_data = load_all_tournament_data()
    
    # Extract statistics
    agent_stats, phase_analysis = extract_detailed_stats(all_data)
    
    # Generate visualizations
    print("\n✨ Creating visualizations:")
    
    print("  1. Complete tournament analysis...")
    create_evolution_visualization(phase_analysis, agent_stats)
    
    print("  2. Mistral-focused analysis...")
    create_mistral_focused_visualization(agent_stats, phase_analysis)
    
    print("  3. Cooperation heatmap...")
    create_cooperation_heatmap(all_data, agent_stats)
    
    print("\n✅ All visualizations generated successfully!")
    print("📁 Saved to: /mnt/c/Apps/LLM-IPD-ARXIV/Stephan_checking/visualizations/")

if __name__ == "__main__":
    main()