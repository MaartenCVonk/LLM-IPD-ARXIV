#!/usr/bin/env python3
"""
Quick Analysis of Available IPD Tournament Results
Focused on shadow=0.75 experiment data
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 100
plt.rcParams['savefig.dpi'] = 300

def load_shadow75_data():
    """Load shadow 75% tournament data"""
    exp_path = Path('results/experiment_20250811_131553')
    data = {}
    
    # Load all phases
    for phase in range(1, 6):
        file_path = exp_path / f'evolutionary_shadow75_phase{phase}.csv'
        if file_path.exists():
            data[f'phase{phase}'] = pd.read_csv(file_path)
            print(f"Loaded Phase {phase}: {len(data[f'phase{phase}'])} rows")
    
    # Load config
    config_path = exp_path / 'config.json'
    if config_path.exists():
        with open(config_path, 'r') as f:
            data['config'] = json.load(f)
    
    return data

def extract_agent_base(agent_name):
    """Extract base agent name without phase/instance info"""
    # Remove phase and instance markers like _p1i1
    import re
    return re.sub(r'_p\d+i\d+', '', agent_name)

def categorize_agent(agent_name):
    """Categorize agent by type"""
    base = extract_agent_base(agent_name)
    
    if any(x in base.lower() for x in ['claude', 'anthropic']):
        return 'Anthropic'
    elif any(x in base.lower() for x in ['gpt', 'o3', 'openai']):
        return 'OpenAI' 
    elif 'mistral' in base.lower():
        return 'Mistral'
    elif 'gemini' in base.lower():
        return 'Gemini'
    elif any(x in base.lower() for x in ['thompson', 'qlearning', 'gradient', 'meta']):
        return 'Adaptive'
    else:
        return 'Classical'

def analyze_phase(df):
    """Quick analysis of a phase"""
    stats = {}
    
    # Unique agents
    agents = set(df['agent1'].unique()) | set(df['agent2'].unique())
    stats['num_agents'] = len(agents)
    
    # Calculate scores and cooperation
    agent_scores = {}
    agent_coop = {}
    
    for agent in agents:
        agent_scores[agent] = []
        agent_coop[agent] = []
    
    for _, row in df.iterrows():
        moves = (row['agent1_move'], row['agent2_move'])
        
        # Calculate round payoffs
        if moves == ('C', 'C'):
            score1, score2 = 3, 3
        elif moves == ('C', 'D'):
            score1, score2 = 0, 5
        elif moves == ('D', 'C'):
            score1, score2 = 5, 0
        else:
            score1, score2 = 1, 1
        
        agent_scores[row['agent1']].append(score1)
        agent_scores[row['agent2']].append(score2)
        
        agent_coop[row['agent1']].append(1 if row['agent1_move'] == 'C' else 0)
        agent_coop[row['agent2']].append(1 if row['agent2_move'] == 'C' else 0)
    
    # Average scores and cooperation rates
    stats['avg_scores'] = {agent: np.mean(scores) for agent, scores in agent_scores.items()}
    stats['coop_rates'] = {agent: np.mean(coop) for agent, coop in agent_coop.items()}
    
    return stats

def create_visualizations(data):
    """Create key visualizations"""
    
    print("\nGenerating visualizations...")
    
    # 1. Agent Performance Evolution
    create_performance_evolution(data)
    
    # 2. Cooperation Dynamics
    create_cooperation_dynamics(data)
    
    # 3. Category Comparison
    create_category_comparison(data)
    
    # 4. Survival Analysis
    create_survival_chart(data)
    
    # 5. Final Phase Heatmap
    create_final_heatmap(data)

def create_performance_evolution(data):
    """Track agent performance across phases"""
    
    # Collect data
    evolution_data = {}
    
    for phase_num in range(1, 6):
        phase_key = f'phase{phase_num}'
        if phase_key in data:
            stats = analyze_phase(data[phase_key])
            
            for agent, score in stats['avg_scores'].items():
                base_agent = extract_agent_base(agent)
                if base_agent not in evolution_data:
                    evolution_data[base_agent] = {
                        'phases': [],
                        'scores': [],
                        'category': categorize_agent(agent)
                    }
                evolution_data[base_agent]['phases'].append(phase_num)
                evolution_data[base_agent]['scores'].append(score)
    
    # Create plots for light and dark versions
    for bg_type in ['light', 'dark']:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        if bg_type == 'dark':
            fig.patch.set_facecolor('black')
            fig.patch.set_alpha(0)
        
        # Plot individual agents
        colors = plt.cm.tab20(np.linspace(0, 1, len(evolution_data)))
        
        for idx, (agent, data_dict) in enumerate(evolution_data.items()):
            if len(data_dict['phases']) > 1:  # Only plot agents present in multiple phases
                color = colors[idx]
                ax1.plot(data_dict['phases'], data_dict['scores'], 
                        marker='o', linewidth=1.5, markersize=4,
                        label=agent[:20], alpha=0.7, color=color)
        
        ax1.set_xlabel('Phase', color='white' if bg_type == 'dark' else 'black')
        ax1.set_ylabel('Average Score per Move', color='white' if bg_type == 'dark' else 'black')
        ax1.set_title('Agent Performance Evolution', 
                     color='white' if bg_type == 'dark' else 'black')
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim(0.5, 5.5)
        ax1.set_ylim(0, 3.5)
        
        # Category averages
        category_evolution = {}
        for agent, data_dict in evolution_data.items():
            cat = data_dict['category']
            if cat not in category_evolution:
                category_evolution[cat] = {i: [] for i in range(1, 6)}
            for phase, score in zip(data_dict['phases'], data_dict['scores']):
                category_evolution[cat][phase].append(score)
        
        category_colors = {
            'Classical': '#2E86AB',
            'Adaptive': '#A23B72', 
            'Anthropic': '#C73E1D',
            'OpenAI': '#6A994E',
            'Mistral': '#BC4749',
            'Gemini': '#F2CC8F'
        }
        
        for cat, phase_data in category_evolution.items():
            phases = []
            means = []
            stds = []
            
            for phase, scores in phase_data.items():
                if scores:
                    phases.append(phase)
                    means.append(np.mean(scores))
                    stds.append(np.std(scores))
            
            if phases:
                color = category_colors.get(cat, '#888888')
                ax2.errorbar(phases, means, yerr=stds,
                           marker='s', linewidth=2, markersize=6,
                           label=cat, alpha=0.8, capsize=3,
                           color=color)
        
        ax2.set_xlabel('Phase', color='white' if bg_type == 'dark' else 'black')
        ax2.set_ylabel('Average Score per Move', color='white' if bg_type == 'dark' else 'black')
        ax2.set_title('Category-Level Performance', 
                     color='white' if bg_type == 'dark' else 'black')
        ax2.grid(True, alpha=0.3)
        ax2.legend(loc='best')
        ax2.set_xlim(0.5, 5.5)
        ax2.set_ylim(0, 3.5)
        
        if bg_type == 'dark':
            for ax in [ax1, ax2]:
                ax.set_facecolor('black')
                ax.tick_params(colors='white')
                for spine in ax.spines.values():
                    spine.set_color('white')
        
        plt.tight_layout()
        
        # Save
        for dpi in [300, 1200]:
            plt.savefig(f'performance_evolution_{bg_type}_{dpi}.png', 
                       dpi=dpi, transparent=(bg_type == 'dark'))
        plt.savefig(f'performance_evolution_{bg_type}.svg', transparent=(bg_type == 'dark'))
        plt.close()
    
    print("✓ Performance evolution plots created")

def create_cooperation_dynamics(data):
    """Analyze cooperation rates over phases"""
    
    coop_evolution = {}
    
    for phase_num in range(1, 6):
        phase_key = f'phase{phase_num}'
        if phase_key in data:
            stats = analyze_phase(data[phase_key])
            
            for agent, coop_rate in stats['coop_rates'].items():
                base_agent = extract_agent_base(agent)
                if base_agent not in coop_evolution:
                    coop_evolution[base_agent] = []
                coop_evolution[base_agent].append((phase_num, coop_rate))
    
    # Create heatmap data
    agents = sorted(coop_evolution.keys())
    heatmap_data = np.full((len(agents), 5), np.nan)
    
    for i, agent in enumerate(agents):
        for phase, coop in coop_evolution[agent]:
            heatmap_data[i, phase-1] = coop
    
    # Plot for both backgrounds
    for bg_type in ['light', 'dark']:
        fig, ax = plt.subplots(figsize=(10, 12))
        
        if bg_type == 'dark':
            fig.patch.set_facecolor('black')
            fig.patch.set_alpha(0)
            cmap = 'magma'
        else:
            cmap = 'RdYlGn'
        
        # Mask NaN values
        masked_data = np.ma.masked_invalid(heatmap_data)
        
        im = ax.imshow(masked_data, cmap=cmap, aspect='auto', vmin=0, vmax=1)
        
        ax.set_xticks(range(5))
        ax.set_xticklabels([f'Phase {i+1}' for i in range(5)])
        ax.set_yticks(range(len(agents)))
        ax.set_yticklabels(agents, fontsize=8)
        
        ax.set_xlabel('Phase', color='white' if bg_type == 'dark' else 'black')
        ax.set_title('Agent Cooperation Rates Across Phases',
                    color='white' if bg_type == 'dark' else 'black')
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Cooperation Rate', rotation=270, labelpad=20,
                      color='white' if bg_type == 'dark' else 'black')
        
        if bg_type == 'dark':
            ax.tick_params(colors='white')
            cbar.ax.yaxis.set_tick_params(color='white')
            plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='white')
        
        plt.tight_layout()
        
        # Save
        for dpi in [300, 1200]:
            plt.savefig(f'cooperation_dynamics_{bg_type}_{dpi}.png',
                       dpi=dpi, transparent=(bg_type == 'dark'))
        plt.savefig(f'cooperation_dynamics_{bg_type}.svg', transparent=(bg_type == 'dark'))
        plt.close()
    
    print("✓ Cooperation dynamics heatmap created")

def create_category_comparison(data):
    """Compare performance by agent category"""
    
    # Collect all scores by category
    category_scores = {}
    
    for phase_num in range(1, 6):
        phase_key = f'phase{phase_num}'
        if phase_key in data:
            stats = analyze_phase(data[phase_key])
            
            for agent, score in stats['avg_scores'].items():
                cat = categorize_agent(agent)
                if cat not in category_scores:
                    category_scores[cat] = []
                category_scores[cat].append(score)
    
    # Plot
    for bg_type in ['light', 'dark']:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        if bg_type == 'dark':
            fig.patch.set_facecolor('black')
            fig.patch.set_alpha(0)
        
        # Box plot
        categories = list(category_scores.keys())
        scores = [category_scores[cat] for cat in categories]
        
        bp = ax1.boxplot(scores, labels=categories, patch_artist=True)
        
        colors = plt.cm.Set3(np.linspace(0, 1, len(categories)))
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        
        ax1.set_ylabel('Score per Move', color='white' if bg_type == 'dark' else 'black')
        ax1.set_title('Score Distribution by Category',
                     color='white' if bg_type == 'dark' else 'black')
        ax1.grid(True, alpha=0.3, axis='y')
        
        # Violin plot
        parts = ax2.violinplot(scores, showmeans=True, showmedians=True)
        ax2.set_xticks(range(1, len(categories) + 1))
        ax2.set_xticklabels(categories)
        ax2.set_ylabel('Score per Move', color='white' if bg_type == 'dark' else 'black')
        ax2.set_title('Score Density by Category',
                     color='white' if bg_type == 'dark' else 'black')
        ax2.grid(True, alpha=0.3, axis='y')
        
        if bg_type == 'dark':
            for ax in [ax1, ax2]:
                ax.set_facecolor('black')
                ax.tick_params(colors='white')
                for spine in ax.spines.values():
                    spine.set_color('white')
            
            # Color violin plot parts
            for pc in parts['bodies']:
                pc.set_facecolor('cyan')
                pc.set_alpha(0.5)
        
        plt.tight_layout()
        
        # Save
        for dpi in [300, 1200]:
            plt.savefig(f'category_comparison_{bg_type}_{dpi}.png',
                       dpi=dpi, transparent=(bg_type == 'dark'))
        plt.savefig(f'category_comparison_{bg_type}.svg', transparent=(bg_type == 'dark'))
        plt.close()
    
    print("✓ Category comparison plots created")

def create_survival_chart(data):
    """Analyze which agents survive across phases"""
    
    survival = {}
    
    for phase_num in range(1, 6):
        phase_key = f'phase{phase_num}'
        if phase_key in data:
            df = data[phase_key]
            agents = set(df['agent1'].unique()) | set(df['agent2'].unique())
            
            for agent in agents:
                base_agent = extract_agent_base(agent)
                if base_agent not in survival:
                    survival[base_agent] = []
                survival[base_agent].append(phase_num)
    
    # Sort by first appearance and survival length
    sorted_agents = sorted(survival.keys(), 
                          key=lambda x: (min(survival[x]), -len(survival[x])))
    
    # Plot
    for bg_type in ['light', 'dark']:
        fig, ax = plt.subplots(figsize=(12, 8))
        
        if bg_type == 'dark':
            fig.patch.set_facecolor('black')
            fig.patch.set_alpha(0)
        
        # Plot survival bars
        y_pos = 0
        colors = plt.cm.tab20(np.linspace(0, 1, len(sorted_agents)))
        
        for agent in sorted_agents:
            phases = survival[agent]
            cat = categorize_agent(agent)
            
            # Color by category
            cat_colors = {
                'Classical': '#2E86AB',
                'Adaptive': '#A23B72',
                'Anthropic': '#C73E1D',
                'OpenAI': '#6A994E',
                'Mistral': '#BC4749',
                'Gemini': '#F2CC8F'
            }
            color = cat_colors.get(cat, '#888888')
            
            for phase in phases:
                ax.barh(y_pos, 1, left=phase-1, height=0.8,
                       color=color, alpha=0.8, edgecolor='white' if bg_type == 'dark' else 'black',
                       linewidth=0.5)
            
            y_pos += 1
        
        ax.set_yticks(range(len(sorted_agents)))
        ax.set_yticklabels(sorted_agents, fontsize=8,
                          color='white' if bg_type == 'dark' else 'black')
        ax.set_xlabel('Phase', color='white' if bg_type == 'dark' else 'black')
        ax.set_title('Agent Survival Across Phases',
                    color='white' if bg_type == 'dark' else 'black')
        ax.set_xlim(0, 5)
        ax.grid(True, alpha=0.3, axis='x')
        
        if bg_type == 'dark':
            ax.set_facecolor('black')
            ax.tick_params(colors='white')
            for spine in ax.spines.values():
                spine.set_color('white')
        
        plt.tight_layout()
        
        # Save
        for dpi in [300, 1200]:
            plt.savefig(f'survival_chart_{bg_type}_{dpi}.png',
                       dpi=dpi, transparent=(bg_type == 'dark'))
        plt.savefig(f'survival_chart_{bg_type}.svg', transparent=(bg_type == 'dark'))
        plt.close()
    
    print("✓ Survival chart created")

def create_final_heatmap(data):
    """Create performance heatmap for final phase"""
    
    if 'phase5' not in data:
        print("⚠ Phase 5 data not found")
        return
    
    df = data['phase5']
    
    # Calculate pairwise average scores
    matchup_scores = {}
    
    for _, row in df.iterrows():
        agent1 = extract_agent_base(row['agent1'])
        agent2 = extract_agent_base(row['agent2'])
        moves = (row['agent1_move'], row['agent2_move'])
        
        if agent1 not in matchup_scores:
            matchup_scores[agent1] = {}
        if agent2 not in matchup_scores[agent1]:
            matchup_scores[agent1][agent2] = []
        
        # Calculate score for agent1
        if moves == ('C', 'C'):
            score = 3
        elif moves == ('C', 'D'):
            score = 0
        elif moves == ('D', 'C'):
            score = 5
        else:
            score = 1
        
        matchup_scores[agent1][agent2].append(score)
    
    # Create matrix
    agents = sorted(set(matchup_scores.keys()))
    if len(agents) < 2:
        print("⚠ Not enough agents for heatmap")
        return
    
    matrix = np.zeros((len(agents), len(agents)))
    
    for i, agent1 in enumerate(agents):
        for j, agent2 in enumerate(agents):
            if agent1 in matchup_scores and agent2 in matchup_scores[agent1]:
                matrix[i, j] = np.mean(matchup_scores[agent1][agent2])
    
    # Plot
    for bg_type in ['light', 'dark']:
        fig, ax = plt.subplots(figsize=(10, 8))
        
        if bg_type == 'dark':
            fig.patch.set_facecolor('black')
            fig.patch.set_alpha(0)
            cmap = 'inferno'
        else:
            cmap = 'coolwarm'
        
        im = ax.imshow(matrix, cmap=cmap, vmin=0, vmax=5)
        
        ax.set_xticks(range(len(agents)))
        ax.set_yticks(range(len(agents)))
        ax.set_xticklabels(agents, rotation=45, ha='right', fontsize=8)
        ax.set_yticklabels(agents, fontsize=8)
        
        ax.set_title('Final Phase Performance Matrix',
                    color='white' if bg_type == 'dark' else 'black')
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Average Score', rotation=270, labelpad=20,
                      color='white' if bg_type == 'dark' else 'black')
        
        if bg_type == 'dark':
            ax.tick_params(colors='white')
            cbar.ax.yaxis.set_tick_params(color='white')
            plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='white')
        
        plt.tight_layout()
        
        # Save
        for dpi in [300, 1200]:
            plt.savefig(f'final_heatmap_{bg_type}_{dpi}.png',
                       dpi=dpi, transparent=(bg_type == 'dark'))
        plt.savefig(f'final_heatmap_{bg_type}.svg', transparent=(bg_type == 'dark'))
        plt.close()
    
    print("✓ Final phase heatmap created")

def print_summary_statistics(data):
    """Print key statistics from the tournament"""
    
    print("\n" + "="*60)
    print("TOURNAMENT SUMMARY STATISTICS")
    print("="*60)
    
    for phase_num in range(1, 6):
        phase_key = f'phase{phase_num}'
        if phase_key in data:
            df = data[phase_key]
            stats = analyze_phase(df)
            
            print(f"\n📊 Phase {phase_num}:")
            print(f"   Agents: {stats['num_agents']}")
            print(f"   Matches: {df['match_id'].nunique()}")
            print(f"   Total rounds: {len(df)}")
            print(f"   Avg rounds/match: {df.groupby('match_id')['round'].max().mean():.2f}")
            
            # Top performers
            top_agents = sorted(stats['avg_scores'].items(), 
                              key=lambda x: x[1], reverse=True)[:3]
            print(f"\n   Top 3 Agents:")
            for agent, score in top_agents:
                base = extract_agent_base(agent)
                coop = stats['coop_rates'][agent]
                print(f"     • {base}: {score:.3f} (coop: {coop:.2%})")
            
            # Category averages
            cat_scores = {}
            for agent, score in stats['avg_scores'].items():
                cat = categorize_agent(agent)
                if cat not in cat_scores:
                    cat_scores[cat] = []
                cat_scores[cat].append(score)
            
            print(f"\n   Category Averages:")
            for cat in sorted(cat_scores.keys()):
                avg = np.mean(cat_scores[cat])
                print(f"     • {cat}: {avg:.3f}")
    
    print("\n" + "="*60)

# Main execution
if __name__ == "__main__":
    print("Loading Shadow 75% tournament data...")
    data = load_shadow75_data()
    
    if data:
        print(f"\nFound {len([k for k in data.keys() if 'phase' in k])} phases of data")
        
        # Print summary
        print_summary_statistics(data)
        
        # Create visualizations
        create_visualizations(data)
        
        print("\n✅ Analysis complete! Generated 5 visualization sets in 6 formats each.")
        print("   Files created: *_light_300.png, *_light_1200.png, *_light.svg")
        print("                  *_dark_300.png, *_dark_1200.png, *_dark.svg")
    else:
        print("❌ No data found!")