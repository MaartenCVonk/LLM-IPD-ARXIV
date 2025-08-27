#!/usr/bin/env python3
"""
Comprehensive Analysis of IPD Tournament Results
Generates extensive visualizations and statistical analysis
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
import glob
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Set style for publication-quality figures
plt.rcParams['figure.dpi'] = 100
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['legend.fontsize'] = 10
plt.rcParams['figure.figsize'] = (12, 8)

# Color schemes
AGENT_COLORS = {
    'Classical': '#2E86AB',
    'Adaptive': '#A23B72',
    'LLM': '#F18F01',
    'Anthropic': '#C73E1D',
    'OpenAI': '#6A994E',
    'Mistral': '#BC4749',
    'Gemini': '#F2CC8F'
}

def load_all_data():
    """Load all tournament data from results folder"""
    data = {}
    
    # Load CSV files
    csv_files = glob.glob('results/**/*.csv', recursive=True)
    for file in csv_files:
        experiment = Path(file).parent.name
        phase = Path(file).stem
        if experiment not in data:
            data[experiment] = {}
        data[experiment][phase] = pd.read_csv(file)
        print(f"Loaded: {file} ({len(data[experiment][phase])} rows)")
    
    # Load JSON configs
    json_files = glob.glob('results/**/config.json', recursive=True)
    for file in json_files:
        experiment = Path(file).parent.name
        with open(file, 'r') as f:
            if experiment not in data:
                data[experiment] = {}
            data[experiment]['config'] = json.load(f)
    
    return data

def categorize_agent(agent_name):
    """Categorize agent by type"""
    if any(x in agent_name.lower() for x in ['claude', 'anthropic']):
        return 'Anthropic'
    elif any(x in agent_name.lower() for x in ['gpt', 'o3', 'openai']):
        return 'OpenAI'
    elif 'mistral' in agent_name.lower():
        return 'Mistral'
    elif 'gemini' in agent_name.lower():
        return 'Gemini'
    elif any(x in agent_name.lower() for x in ['thompson', 'q-learning', 'gradient', 'meta']):
        return 'Adaptive'
    else:
        return 'Classical'

def extract_temperature(agent_name):
    """Extract temperature from agent name"""
    import re
    match = re.search(r'T=([0-9.]+)', agent_name)
    return float(match.group(1)) if match else None

def analyze_phase_data(df, phase_name):
    """Analyze a single phase's data"""
    stats = {}
    
    # Basic stats
    stats['total_matches'] = df['match_id'].nunique()
    stats['total_rounds'] = len(df)
    stats['avg_rounds_per_match'] = df.groupby('match_id')['round'].max().mean()
    
    # Agent performance
    agent_scores = {}
    for _, row in df.iterrows():
        if row['agent1'] not in agent_scores:
            agent_scores[row['agent1']] = []
        if row['agent2'] not in agent_scores:
            agent_scores[row['agent2']] = []
        
        # Calculate round scores
        moves = (row['agent1_move'], row['agent2_move'])
        if moves == ('C', 'C'):
            agent_scores[row['agent1']].append(3)
            agent_scores[row['agent2']].append(3)
        elif moves == ('C', 'D'):
            agent_scores[row['agent1']].append(0)
            agent_scores[row['agent2']].append(5)
        elif moves == ('D', 'C'):
            agent_scores[row['agent1']].append(5)
            agent_scores[row['agent2']].append(0)
        else:  # D, D
            agent_scores[row['agent1']].append(1)
            agent_scores[row['agent2']].append(1)
    
    # Calculate average scores
    agent_avg_scores = {agent: np.mean(scores) for agent, scores in agent_scores.items()}
    stats['agent_scores'] = agent_avg_scores
    
    # Cooperation rates
    coop_rates = {}
    for agent in df['agent1'].unique():
        agent_moves = []
        agent_moves.extend(df[df['agent1'] == agent]['agent1_move'].tolist())
        agent_moves.extend(df[df['agent2'] == agent]['agent2_move'].tolist())
        coop_rates[agent] = agent_moves.count('C') / len(agent_moves) if agent_moves else 0
    stats['cooperation_rates'] = coop_rates
    
    # First move cooperation
    first_moves = df[df['round'] == 1]
    first_coop = {}
    for agent in df['agent1'].unique():
        agent_first = []
        agent_first.extend(first_moves[first_moves['agent1'] == agent]['agent1_move'].tolist())
        agent_first.extend(first_moves[first_moves['agent2'] == agent]['agent2_move'].tolist())
        first_coop[agent] = agent_first.count('C') / len(agent_first) if agent_first else 0
    stats['first_move_cooperation'] = first_coop
    
    return stats

def create_comprehensive_visualizations(data):
    """Create all visualization types"""
    
    # Get the main experiment data
    exp_keys = [k for k in data.keys() if 'experiment' in k]
    if not exp_keys:
        print("No experiment data found!")
        return
    
    main_exp = data[exp_keys[0]]
    
    # Find all phase CSVs
    phase_keys = [k for k in main_exp.keys() if 'evolutionary' in k]
    phase_keys.sort()  # Sort by phase number
    
    if not phase_keys:
        print("No phase data found!")
        return
    
    print(f"\nAnalyzing {len(phase_keys)} phases from {exp_keys[0]}")
    
    # 1. Evolution of Agent Scores Across Phases
    create_evolution_plot(main_exp, phase_keys)
    
    # 2. Cooperation Heatmap
    create_cooperation_heatmap(main_exp, phase_keys)
    
    # 3. Strategy Performance by Category
    create_category_performance(main_exp, phase_keys)
    
    # 4. Temperature Effects Analysis (for LLMs)
    create_temperature_analysis(main_exp, phase_keys)
    
    # 5. Head-to-Head Matchup Matrix
    create_matchup_matrix(main_exp, phase_keys[-1])  # Use final phase
    
    # 6. Move Dynamics Over Rounds
    create_move_dynamics(main_exp, phase_keys[-1])
    
    # 7. Strategic Footprint Analysis
    create_strategic_footprint(main_exp, phase_keys)
    
    # 8. Survival Analysis
    create_survival_analysis(main_exp, phase_keys)
    
    # 9. Pairwise Performance Delta
    create_performance_deltas(main_exp, phase_keys)
    
    # 10. Distribution Analysis
    create_distribution_analysis(main_exp, phase_keys)

def create_evolution_plot(exp_data, phase_keys):
    """Plot evolution of agent scores across phases"""
    
    # Collect scores across phases
    evolution_data = {}
    
    for phase_idx, phase_key in enumerate(phase_keys, 1):
        df = exp_data[phase_key]
        stats = analyze_phase_data(df, phase_key)
        
        for agent, score in stats['agent_scores'].items():
            if agent not in evolution_data:
                evolution_data[agent] = {'phases': [], 'scores': [], 'category': categorize_agent(agent)}
            evolution_data[agent]['phases'].append(phase_idx)
            evolution_data[agent]['scores'].append(score)
    
    # Create figure with light and dark versions
    for bg_type in ['light', 'dark']:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        if bg_type == 'dark':
            fig.patch.set_alpha(0)
            for ax in [ax1, ax2]:
                ax.set_facecolor('none')
                ax.spines['bottom'].set_color('white')
                ax.spines['top'].set_color('white')
                ax.spines['left'].set_color('white')
                ax.spines['right'].set_color('white')
                ax.xaxis.label.set_color('white')
                ax.yaxis.label.set_color('white')
                ax.tick_params(colors='white')
                ax.title.set_color('white')
        
        # Left plot: All agents
        for agent, data in evolution_data.items():
            color = AGENT_COLORS.get(data['category'], '#888888')
            if bg_type == 'dark':
                color = plt.cm.Set3(hash(agent) % 12 / 12)
            ax1.plot(data['phases'], data['scores'], marker='o', label=agent[:20], 
                    linewidth=2, markersize=6, alpha=0.8, color=color)
        
        ax1.set_xlabel('Phase')
        ax1.set_ylabel('Average Score per Move')
        ax1.set_title('Evolution of Agent Performance Across Phases')
        ax1.grid(True, alpha=0.3, color='white' if bg_type == 'dark' else 'black')
        ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8,
                  framealpha=0 if bg_type == 'dark' else 1)
        
        # Right plot: Category averages
        category_evolution = {}
        for agent, data in evolution_data.items():
            cat = data['category']
            if cat not in category_evolution:
                category_evolution[cat] = {i: [] for i in range(1, len(phase_keys)+1)}
            for phase, score in zip(data['phases'], data['scores']):
                category_evolution[cat][phase].append(score)
        
        for cat, phases_data in category_evolution.items():
            phases = []
            avg_scores = []
            std_scores = []
            for phase, scores in phases_data.items():
                if scores:
                    phases.append(phase)
                    avg_scores.append(np.mean(scores))
                    std_scores.append(np.std(scores))
            
            color = AGENT_COLORS.get(cat, '#888888')
            if bg_type == 'dark':
                color = plt.cm.Set2(list(category_evolution.keys()).index(cat) / len(category_evolution))
            
            ax2.errorbar(phases, avg_scores, yerr=std_scores, marker='s', 
                        label=cat, linewidth=3, markersize=8, capsize=5,
                        alpha=0.9, color=color)
        
        ax2.set_xlabel('Phase')
        ax2.set_ylabel('Average Score per Move')
        ax2.set_title('Category-Level Performance Evolution')
        ax2.grid(True, alpha=0.3, color='white' if bg_type == 'dark' else 'black')
        ax2.legend(loc='best', framealpha=0 if bg_type == 'dark' else 1)
        
        plt.tight_layout()
        
        # Save in multiple formats
        for dpi in [300, 1200]:
            filename = f'evolution_{bg_type}_{dpi}'
            plt.savefig(f'{filename}.png', dpi=dpi, 
                       transparent=(bg_type == 'dark'),
                       facecolor='none' if bg_type == 'dark' else 'white')
        plt.savefig(f'evolution_{bg_type}_svg.svg', 
                   transparent=(bg_type == 'dark'),
                   facecolor='none' if bg_type == 'dark' else 'white')
        plt.close()

def create_cooperation_heatmap(exp_data, phase_keys):
    """Create cooperation rate heatmap"""
    
    # Get final phase data
    final_phase = exp_data[phase_keys[-1]]
    stats = analyze_phase_data(final_phase, phase_keys[-1])
    
    # Prepare data for heatmap
    agents = sorted(stats['cooperation_rates'].keys())
    coop_matrix = np.zeros((len(agents), len(phase_keys)))
    
    for phase_idx, phase_key in enumerate(phase_keys):
        phase_stats = analyze_phase_data(exp_data[phase_key], phase_key)
        for agent_idx, agent in enumerate(agents):
            if agent in phase_stats['cooperation_rates']:
                coop_matrix[agent_idx, phase_idx] = phase_stats['cooperation_rates'][agent]
    
    # Create heatmap for both backgrounds
    for bg_type in ['light', 'dark']:
        fig, ax = plt.subplots(figsize=(12, 10))
        
        if bg_type == 'dark':
            fig.patch.set_alpha(0)
            cmap = 'YlOrRd'
        else:
            cmap = 'RdYlGn'
        
        sns.heatmap(coop_matrix, 
                   xticklabels=[f'Phase {i+1}' for i in range(len(phase_keys))],
                   yticklabels=agents,
                   annot=True, fmt='.2f', cmap=cmap,
                   cbar_kws={'label': 'Cooperation Rate'},
                   ax=ax, vmin=0, vmax=1)
        
        ax.set_title('Agent Cooperation Rates Across Phases', 
                    color='white' if bg_type == 'dark' else 'black')
        ax.set_xlabel('Phase', color='white' if bg_type == 'dark' else 'black')
        ax.set_ylabel('Agent', color='white' if bg_type == 'dark' else 'black')
        
        if bg_type == 'dark':
            ax.tick_params(colors='white')
            for spine in ax.spines.values():
                spine.set_color('white')
        
        plt.tight_layout()
        
        # Save in multiple formats
        for dpi in [300, 1200]:
            plt.savefig(f'cooperation_heatmap_{bg_type}_{dpi}.png', dpi=dpi,
                       transparent=(bg_type == 'dark'),
                       facecolor='none' if bg_type == 'dark' else 'white')
        plt.savefig(f'cooperation_heatmap_{bg_type}_svg.svg',
                   transparent=(bg_type == 'dark'),
                   facecolor='none' if bg_type == 'dark' else 'white')
        plt.close()

def create_category_performance(exp_data, phase_keys):
    """Create category-level performance comparison"""
    
    category_data = {cat: [] for cat in AGENT_COLORS.keys()}
    
    for phase_key in phase_keys:
        stats = analyze_phase_data(exp_data[phase_key], phase_key)
        for agent, score in stats['agent_scores'].items():
            cat = categorize_agent(agent)
            if cat in category_data:
                category_data[cat].append(score)
    
    # Create violin plot
    for bg_type in ['light', 'dark']:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        if bg_type == 'dark':
            fig.patch.set_alpha(0)
            plt.style.use('dark_background')
        
        # Violin plot
        plot_data = []
        plot_labels = []
        for cat, scores in category_data.items():
            if scores:
                plot_data.append(scores)
                plot_labels.append(f'{cat}\n(n={len(scores)})')
        
        parts = ax1.violinplot(plot_data, showmeans=True, showmedians=True)
        ax1.set_xticks(range(1, len(plot_labels) + 1))
        ax1.set_xticklabels(plot_labels)
        ax1.set_ylabel('Score per Move')
        ax1.set_title('Score Distribution by Agent Category')
        ax1.grid(True, alpha=0.3)
        
        # Box plot for comparison
        ax2.boxplot(plot_data, labels=plot_labels)
        ax2.set_ylabel('Score per Move')
        ax2.set_title('Score Quartiles by Agent Category')
        ax2.grid(True, alpha=0.3)
        
        if bg_type == 'dark':
            for ax in [ax1, ax2]:
                ax.set_facecolor('none')
                for spine in ax.spines.values():
                    spine.set_color('white')
                ax.tick_params(colors='white')
                ax.xaxis.label.set_color('white')
                ax.yaxis.label.set_color('white')
                ax.title.set_color('white')
        
        plt.tight_layout()
        
        # Save
        for dpi in [300, 1200]:
            plt.savefig(f'category_performance_{bg_type}_{dpi}.png', dpi=dpi,
                       transparent=(bg_type == 'dark'))
        plt.savefig(f'category_performance_{bg_type}_svg.svg',
                   transparent=(bg_type == 'dark'))
        plt.close()
        
        if bg_type == 'dark':
            plt.style.use('default')

def create_temperature_analysis(exp_data, phase_keys):
    """Analyze temperature effects for LLM agents"""
    
    temp_data = {}
    
    for phase_key in phase_keys:
        stats = analyze_phase_data(exp_data[phase_key], phase_key)
        for agent, score in stats['agent_scores'].items():
            temp = extract_temperature(agent)
            if temp is not None:
                base_name = agent.split('(T=')[0].strip()
                if base_name not in temp_data:
                    temp_data[base_name] = {}
                if temp not in temp_data[base_name]:
                    temp_data[base_name][temp] = []
                temp_data[base_name][temp].append(score)
    
    if not temp_data:
        print("No temperature data found")
        return
    
    # Create temperature effect plots
    for bg_type in ['light', 'dark']:
        fig, axes = plt.subplots(2, 2, figsize=(14, 12))
        axes = axes.flatten()
        
        if bg_type == 'dark':
            fig.patch.set_alpha(0)
        
        for idx, (model, temp_scores) in enumerate(temp_data.items()):
            if idx >= 4:
                break
            
            ax = axes[idx]
            
            temps = sorted(temp_scores.keys())
            means = [np.mean(temp_scores[t]) for t in temps]
            stds = [np.std(temp_scores[t]) for t in temps]
            
            color = plt.cm.tab10(idx)
            ax.errorbar(temps, means, yerr=stds, marker='o', 
                       linewidth=2, markersize=8, capsize=5,
                       color=color, label=model)
            
            # Add trend line
            z = np.polyfit(temps, means, 2)
            p = np.poly1d(z)
            temp_smooth = np.linspace(min(temps), max(temps), 100)
            ax.plot(temp_smooth, p(temp_smooth), '--', alpha=0.5, color=color)
            
            ax.set_xlabel('Temperature', color='white' if bg_type == 'dark' else 'black')
            ax.set_ylabel('Average Score', color='white' if bg_type == 'dark' else 'black')
            ax.set_title(f'{model} Performance vs Temperature',
                        color='white' if bg_type == 'dark' else 'black')
            ax.grid(True, alpha=0.3)
            ax.legend()
            
            if bg_type == 'dark':
                ax.set_facecolor('none')
                for spine in ax.spines.values():
                    spine.set_color('white')
                ax.tick_params(colors='white')
        
        plt.suptitle('Temperature Effects on LLM Performance',
                    color='white' if bg_type == 'dark' else 'black', fontsize=16)
        plt.tight_layout()
        
        # Save
        for dpi in [300, 1200]:
            plt.savefig(f'temperature_analysis_{bg_type}_{dpi}.png', dpi=dpi,
                       transparent=(bg_type == 'dark'))
        plt.savefig(f'temperature_analysis_{bg_type}_svg.svg',
                   transparent=(bg_type == 'dark'))
        plt.close()

def create_matchup_matrix(exp_data, phase_key):
    """Create head-to-head performance matrix"""
    
    df = exp_data[phase_key]
    
    # Calculate pairwise scores
    matchup_scores = {}
    
    for _, row in df.iterrows():
        agent1, agent2 = row['agent1'], row['agent2']
        moves = (row['agent1_move'], row['agent2_move'])
        
        if agent1 not in matchup_scores:
            matchup_scores[agent1] = {}
        if agent2 not in matchup_scores:
            matchup_scores[agent2] = {}
        
        if agent2 not in matchup_scores[agent1]:
            matchup_scores[agent1][agent2] = []
        if agent1 not in matchup_scores[agent2]:
            matchup_scores[agent2][agent1] = []
        
        # Calculate scores
        if moves == ('C', 'C'):
            matchup_scores[agent1][agent2].append(3)
            matchup_scores[agent2][agent1].append(3)
        elif moves == ('C', 'D'):
            matchup_scores[agent1][agent2].append(0)
            matchup_scores[agent2][agent1].append(5)
        elif moves == ('D', 'C'):
            matchup_scores[agent1][agent2].append(5)
            matchup_scores[agent2][agent1].append(0)
        else:
            matchup_scores[agent1][agent2].append(1)
            matchup_scores[agent2][agent1].append(1)
    
    # Create matrix
    agents = sorted(matchup_scores.keys())
    matrix = np.zeros((len(agents), len(agents)))
    
    for i, agent1 in enumerate(agents):
        for j, agent2 in enumerate(agents):
            if agent2 in matchup_scores[agent1]:
                matrix[i, j] = np.mean(matchup_scores[agent1][agent2])
    
    # Plot
    for bg_type in ['light', 'dark']:
        fig, ax = plt.subplots(figsize=(14, 12))
        
        if bg_type == 'dark':
            fig.patch.set_alpha(0)
            cmap = 'magma'
        else:
            cmap = 'coolwarm'
        
        im = ax.imshow(matrix, cmap=cmap, vmin=0, vmax=5)
        
        ax.set_xticks(np.arange(len(agents)))
        ax.set_yticks(np.arange(len(agents)))
        ax.set_xticklabels(agents, rotation=45, ha='right')
        ax.set_yticklabels(agents)
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Average Score', rotation=270, labelpad=20,
                      color='white' if bg_type == 'dark' else 'black')
        
        ax.set_title('Head-to-Head Performance Matrix',
                    color='white' if bg_type == 'dark' else 'black')
        
        if bg_type == 'dark':
            ax.tick_params(colors='white')
            cbar.ax.yaxis.set_tick_params(color='white')
            plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='white')
        
        plt.tight_layout()
        
        # Save
        for dpi in [300, 1200]:
            plt.savefig(f'matchup_matrix_{bg_type}_{dpi}.png', dpi=dpi,
                       transparent=(bg_type == 'dark'))
        plt.savefig(f'matchup_matrix_{bg_type}_svg.svg',
                   transparent=(bg_type == 'dark'))
        plt.close()

def create_move_dynamics(exp_data, phase_key):
    """Analyze move dynamics over rounds"""
    
    df = exp_data[phase_key]
    max_rounds = df['round'].max()
    
    # Track cooperation rate by round
    round_coop = {}
    for round_num in range(1, min(max_rounds + 1, 21)):  # Limit to first 20 rounds
        round_data = df[df['round'] == round_num]
        total_moves = len(round_data) * 2  # Both agents
        coop_moves = (round_data['agent1_move'] == 'C').sum() + \
                    (round_data['agent2_move'] == 'C').sum()
        round_coop[round_num] = coop_moves / total_moves if total_moves > 0 else 0
    
    # Track by category
    category_dynamics = {}
    for round_num in range(1, min(max_rounds + 1, 21)):
        round_data = df[df['round'] == round_num]
        for cat in AGENT_COLORS.keys():
            if cat not in category_dynamics:
                category_dynamics[cat] = {}
            
            cat_moves_c = 0
            cat_moves_total = 0
            
            for _, row in round_data.iterrows():
                if categorize_agent(row['agent1']) == cat:
                    cat_moves_total += 1
                    if row['agent1_move'] == 'C':
                        cat_moves_c += 1
                if categorize_agent(row['agent2']) == cat:
                    cat_moves_total += 1
                    if row['agent2_move'] == 'C':
                        cat_moves_c += 1
            
            if cat_moves_total > 0:
                category_dynamics[cat][round_num] = cat_moves_c / cat_moves_total
    
    # Plot
    for bg_type in ['light', 'dark']:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        if bg_type == 'dark':
            fig.patch.set_alpha(0)
        
        # Overall dynamics
        rounds = list(round_coop.keys())
        coop_rates = list(round_coop.values())
        
        ax1.plot(rounds, coop_rates, marker='o', linewidth=2, markersize=6,
                color='green' if bg_type == 'light' else 'lime')
        ax1.fill_between(rounds, coop_rates, alpha=0.3,
                         color='green' if bg_type == 'light' else 'lime')
        ax1.set_xlabel('Round', color='white' if bg_type == 'dark' else 'black')
        ax1.set_ylabel('Cooperation Rate', color='white' if bg_type == 'dark' else 'black')
        ax1.set_title('Overall Cooperation Dynamics', 
                     color='white' if bg_type == 'dark' else 'black')
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim(0, 1)
        
        # Category dynamics
        for cat, dynamics in category_dynamics.items():
            if dynamics:
                rounds = list(dynamics.keys())
                rates = list(dynamics.values())
                color = AGENT_COLORS.get(cat, '#888888')
                if bg_type == 'dark':
                    color = plt.cm.Set2(list(category_dynamics.keys()).index(cat) / len(category_dynamics))
                ax2.plot(rounds, rates, marker='o', label=cat,
                        linewidth=2, markersize=4, alpha=0.8, color=color)
        
        ax2.set_xlabel('Round', color='white' if bg_type == 'dark' else 'black')
        ax2.set_ylabel('Cooperation Rate', color='white' if bg_type == 'dark' else 'black')
        ax2.set_title('Cooperation Dynamics by Category',
                     color='white' if bg_type == 'dark' else 'black')
        ax2.grid(True, alpha=0.3)
        ax2.legend(loc='best', framealpha=0 if bg_type == 'dark' else 1)
        ax2.set_ylim(0, 1)
        
        if bg_type == 'dark':
            for ax in [ax1, ax2]:
                ax.set_facecolor('none')
                for spine in ax.spines.values():
                    spine.set_color('white')
                ax.tick_params(colors='white')
        
        plt.tight_layout()
        
        # Save
        for dpi in [300, 1200]:
            plt.savefig(f'move_dynamics_{bg_type}_{dpi}.png', dpi=dpi,
                       transparent=(bg_type == 'dark'))
        plt.savefig(f'move_dynamics_{bg_type}_svg.svg',
                   transparent=(bg_type == 'dark'))
        plt.close()

def create_strategic_footprint(exp_data, phase_keys):
    """Create strategic footprint visualization"""
    
    # Analyze strategic patterns
    footprints = {}
    
    for phase_key in phase_keys[-1:]:  # Use final phase
        df = exp_data[phase_key]
        stats = analyze_phase_data(df, phase_key)
        
        for agent in stats['agent_scores'].keys():
            footprints[agent] = {
                'avg_score': stats['agent_scores'][agent],
                'cooperation_rate': stats['cooperation_rates'][agent],
                'first_coop': stats['first_move_cooperation'][agent],
                'consistency': 0  # Will calculate
            }
            
            # Calculate consistency (inverse of move variance)
            agent_moves = []
            agent_moves.extend(df[df['agent1'] == agent]['agent1_move'].tolist())
            agent_moves.extend(df[df['agent2'] == agent]['agent2_move'].tolist())
            
            if len(agent_moves) > 1:
                # Measure consistency as tendency to repeat same move
                same_as_prev = sum(1 for i in range(1, len(agent_moves)) 
                                  if agent_moves[i] == agent_moves[i-1])
                footprints[agent]['consistency'] = same_as_prev / (len(agent_moves) - 1)
    
    # Create radar chart
    for bg_type in ['light', 'dark']:
        fig, axes = plt.subplots(2, 3, figsize=(15, 10), 
                                subplot_kw=dict(projection='polar'))
        axes = axes.flatten()
        
        if bg_type == 'dark':
            fig.patch.set_alpha(0)
        
        # Select diverse agents to display
        selected_agents = []
        for cat in ['Classical', 'Adaptive', 'Anthropic', 'OpenAI', 'Mistral', 'Gemini']:
            cat_agents = [a for a in footprints.keys() if categorize_agent(a) == cat]
            if cat_agents:
                selected_agents.append(cat_agents[0])
        
        categories = ['Score', 'Cooperation', 'First Move', 'Consistency']
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        angles += angles[:1]  # Complete the circle
        
        for idx, agent in enumerate(selected_agents[:6]):
            ax = axes[idx]
            
            values = [
                footprints[agent]['avg_score'] / 3,  # Normalize to 0-1
                footprints[agent]['cooperation_rate'],
                footprints[agent]['first_coop'],
                footprints[agent]['consistency']
            ]
            values += values[:1]  # Complete the circle
            
            ax.plot(angles, values, 'o-', linewidth=2, 
                   color=AGENT_COLORS.get(categorize_agent(agent), '#888888'))
            ax.fill(angles, values, alpha=0.25,
                   color=AGENT_COLORS.get(categorize_agent(agent), '#888888'))
            
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(categories, color='white' if bg_type == 'dark' else 'black')
            ax.set_ylim(0, 1)
            ax.set_title(agent[:30], color='white' if bg_type == 'dark' else 'black')
            ax.grid(True, alpha=0.3, color='white' if bg_type == 'dark' else 'black')
            
            if bg_type == 'dark':
                ax.tick_params(colors='white')
        
        plt.suptitle('Strategic Footprints', 
                    color='white' if bg_type == 'dark' else 'black', fontsize=16)
        plt.tight_layout()
        
        # Save
        for dpi in [300, 1200]:
            plt.savefig(f'strategic_footprint_{bg_type}_{dpi}.png', dpi=dpi,
                       transparent=(bg_type == 'dark'))
        plt.savefig(f'strategic_footprint_{bg_type}_svg.svg',
                   transparent=(bg_type == 'dark'))
        plt.close()

def create_survival_analysis(exp_data, phase_keys):
    """Analyze agent survival across phases"""
    
    survival_data = {}
    
    for phase_idx, phase_key in enumerate(phase_keys, 1):
        df = exp_data[phase_key]
        active_agents = set(df['agent1'].unique()) | set(df['agent2'].unique())
        
        for agent in active_agents:
            if agent not in survival_data:
                survival_data[agent] = []
            survival_data[agent].append(phase_idx)
    
    # Calculate survival metrics
    survival_lengths = {agent: max(phases) - min(phases) + 1 
                       for agent, phases in survival_data.items()}
    
    # Plot
    for bg_type in ['light', 'dark']:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        if bg_type == 'dark':
            fig.patch.set_alpha(0)
        
        # Survival timeline
        sorted_agents = sorted(survival_data.keys(), 
                             key=lambda x: (min(survival_data[x]), -len(survival_data[x])))
        
        y_pos = 0
        for agent in sorted_agents:
            phases = survival_data[agent]
            color = AGENT_COLORS.get(categorize_agent(agent), '#888888')
            if bg_type == 'dark':
                color = plt.cm.tab20(y_pos % 20 / 20)
            
            for phase in phases:
                ax1.barh(y_pos, 1, left=phase-1, height=0.8,
                        color=color, alpha=0.8)
            y_pos += 1
        
        ax1.set_yticks(range(len(sorted_agents)))
        ax1.set_yticklabels(sorted_agents, fontsize=8)
        ax1.set_xlabel('Phase', color='white' if bg_type == 'dark' else 'black')
        ax1.set_title('Agent Survival Timeline', 
                     color='white' if bg_type == 'dark' else 'black')
        ax1.grid(True, alpha=0.3, axis='x')
        
        # Survival distribution by category
        category_survival = {}
        for agent, length in survival_lengths.items():
            cat = categorize_agent(agent)
            if cat not in category_survival:
                category_survival[cat] = []
            category_survival[cat].append(length)
        
        categories = list(category_survival.keys())
        survival_values = [category_survival[cat] for cat in categories]
        
        bp = ax2.boxplot(survival_values, labels=categories, patch_artist=True)
        
        for patch, cat in zip(bp['boxes'], categories):
            patch.set_facecolor(AGENT_COLORS.get(cat, '#888888'))
            patch.set_alpha(0.7)
        
        ax2.set_ylabel('Phases Survived', color='white' if bg_type == 'dark' else 'black')
        ax2.set_title('Survival Distribution by Category',
                     color='white' if bg_type == 'dark' else 'black')
        ax2.grid(True, alpha=0.3, axis='y')
        
        if bg_type == 'dark':
            for ax in [ax1, ax2]:
                ax.set_facecolor('none')
                for spine in ax.spines.values():
                    spine.set_color('white')
                ax.tick_params(colors='white')
        
        plt.tight_layout()
        
        # Save
        for dpi in [300, 1200]:
            plt.savefig(f'survival_analysis_{bg_type}_{dpi}.png', dpi=dpi,
                       transparent=(bg_type == 'dark'))
        plt.savefig(f'survival_analysis_{bg_type}_svg.svg',
                   transparent=(bg_type == 'dark'))
        plt.close()

def create_performance_deltas(exp_data, phase_keys):
    """Create pairwise performance comparison"""
    
    if len(phase_keys) < 2:
        print("Not enough phases for delta analysis")
        return
    
    # Compare first and last phase
    first_stats = analyze_phase_data(exp_data[phase_keys[0]], phase_keys[0])
    last_stats = analyze_phase_data(exp_data[phase_keys[-1]], phase_keys[-1])
    
    # Calculate deltas
    deltas = {}
    for agent in first_stats['agent_scores']:
        if agent in last_stats['agent_scores']:
            deltas[agent] = {
                'score_delta': last_stats['agent_scores'][agent] - first_stats['agent_scores'][agent],
                'coop_delta': last_stats['cooperation_rates'][agent] - first_stats['cooperation_rates'][agent],
                'category': categorize_agent(agent)
            }
    
    if not deltas:
        print("No common agents between phases")
        return
    
    # Plot
    for bg_type in ['light', 'dark']:
        fig, ax = plt.subplots(figsize=(12, 8))
        
        if bg_type == 'dark':
            fig.patch.set_alpha(0)
        
        # Scatter plot of deltas
        for agent, delta_data in deltas.items():
            color = AGENT_COLORS.get(delta_data['category'], '#888888')
            if bg_type == 'dark':
                color = plt.cm.tab20(hash(agent) % 20 / 20)
            
            ax.scatter(delta_data['coop_delta'], delta_data['score_delta'],
                      s=100, alpha=0.7, color=color, 
                      label=delta_data['category'] if delta_data['category'] not in 
                      [d['category'] for d in list(deltas.values())[:list(deltas.keys()).index(agent)]]
                      else '')
            
            # Add agent label for significant changes
            if abs(delta_data['score_delta']) > 0.5 or abs(delta_data['coop_delta']) > 0.2:
                ax.annotate(agent[:15], 
                          (delta_data['coop_delta'], delta_data['score_delta']),
                          fontsize=8, alpha=0.8,
                          color='white' if bg_type == 'dark' else 'black')
        
        ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
        ax.axvline(x=0, color='gray', linestyle='--', alpha=0.5)
        
        ax.set_xlabel('Cooperation Rate Change', 
                     color='white' if bg_type == 'dark' else 'black')
        ax.set_ylabel('Average Score Change',
                     color='white' if bg_type == 'dark' else 'black')
        ax.set_title(f'Performance Changes: Phase 1 → Phase {len(phase_keys)}',
                    color='white' if bg_type == 'dark' else 'black')
        
        # Add quadrant labels
        ax.text(0.02, 0.02, 'Less Cooperative\nLower Score', transform=ax.transAxes,
               fontsize=9, alpha=0.5, color='white' if bg_type == 'dark' else 'black')
        ax.text(0.98, 0.02, 'More Cooperative\nLower Score', transform=ax.transAxes,
               fontsize=9, alpha=0.5, ha='right',
               color='white' if bg_type == 'dark' else 'black')
        ax.text(0.02, 0.98, 'Less Cooperative\nHigher Score', transform=ax.transAxes,
               fontsize=9, alpha=0.5, va='top',
               color='white' if bg_type == 'dark' else 'black')
        ax.text(0.98, 0.98, 'More Cooperative\nHigher Score', transform=ax.transAxes,
               fontsize=9, alpha=0.5, ha='right', va='top',
               color='white' if bg_type == 'dark' else 'black')
        
        ax.grid(True, alpha=0.3)
        ax.legend(loc='best', framealpha=0 if bg_type == 'dark' else 1)
        
        if bg_type == 'dark':
            ax.set_facecolor('none')
            for spine in ax.spines.values():
                spine.set_color('white')
            ax.tick_params(colors='white')
        
        plt.tight_layout()
        
        # Save
        for dpi in [300, 1200]:
            plt.savefig(f'performance_deltas_{bg_type}_{dpi}.png', dpi=dpi,
                       transparent=(bg_type == 'dark'))
        plt.savefig(f'performance_deltas_{bg_type}_svg.svg',
                   transparent=(bg_type == 'dark'))
        plt.close()

def create_distribution_analysis(exp_data, phase_keys):
    """Create comprehensive distribution analysis"""
    
    # Collect all scores across phases
    all_scores = []
    score_labels = []
    
    for phase_idx, phase_key in enumerate(phase_keys, 1):
        df = exp_data[phase_key]
        phase_scores = []
        
        for _, row in df.iterrows():
            moves = (row['agent1_move'], row['agent2_move'])
            if moves == ('C', 'C'):
                phase_scores.extend([3, 3])
            elif moves == ('C', 'D'):
                phase_scores.extend([0, 5])
            elif moves == ('D', 'C'):
                phase_scores.extend([5, 0])
            else:
                phase_scores.extend([1, 1])
        
        all_scores.extend(phase_scores)
        score_labels.extend([f'Phase {phase_idx}'] * len(phase_scores))
    
    # Create distribution plots
    for bg_type in ['light', 'dark']:
        fig, axes = plt.subplots(2, 2, figsize=(14, 12))
        
        if bg_type == 'dark':
            fig.patch.set_alpha(0)
        
        # 1. Overall distribution
        ax = axes[0, 0]
        ax.hist(all_scores, bins=[0, 1, 2, 3, 4, 5], 
               edgecolor='white' if bg_type == 'dark' else 'black',
               color='skyblue' if bg_type == 'light' else 'cyan',
               alpha=0.7)
        ax.set_xlabel('Score', color='white' if bg_type == 'dark' else 'black')
        ax.set_ylabel('Frequency', color='white' if bg_type == 'dark' else 'black')
        ax.set_title('Overall Score Distribution',
                    color='white' if bg_type == 'dark' else 'black')
        ax.set_xticks([0, 1, 3, 5])
        ax.grid(True, alpha=0.3)
        
        # 2. Phase evolution
        ax = axes[0, 1]
        phase_data = []
        for phase_idx in range(1, len(phase_keys) + 1):
            phase_scores = [s for s, l in zip(all_scores, score_labels) 
                          if l == f'Phase {phase_idx}']
            phase_data.append(phase_scores)
        
        bp = ax.boxplot(phase_data, labels=[f'P{i}' for i in range(1, len(phase_keys) + 1)])
        ax.set_ylabel('Score', color='white' if bg_type == 'dark' else 'black')
        ax.set_title('Score Distribution Evolution',
                    color='white' if bg_type == 'dark' else 'black')
        ax.grid(True, alpha=0.3, axis='y')
        
        # 3. Outcome proportions
        ax = axes[1, 0]
        outcomes = {'Mutual Cooperation': 0, 'Exploitation': 0, 'Mutual Defection': 0}
        
        for phase_key in phase_keys:
            df = exp_data[phase_key]
            for _, row in df.iterrows():
                moves = (row['agent1_move'], row['agent2_move'])
                if moves == ('C', 'C'):
                    outcomes['Mutual Cooperation'] += 1
                elif moves in [('C', 'D'), ('D', 'C')]:
                    outcomes['Exploitation'] += 1
                else:
                    outcomes['Mutual Defection'] += 1
        
        colors = ['green', 'orange', 'red'] if bg_type == 'light' else ['lime', 'yellow', 'crimson']
        ax.pie(outcomes.values(), labels=outcomes.keys(), autopct='%1.1f%%',
              colors=colors, textprops={'color': 'white' if bg_type == 'dark' else 'black'})
        ax.set_title('Game Outcome Distribution',
                    color='white' if bg_type == 'dark' else 'black')
        
        # 4. Cumulative distribution
        ax = axes[1, 1]
        sorted_scores = np.sort(all_scores)
        cumulative = np.arange(1, len(sorted_scores) + 1) / len(sorted_scores)
        
        ax.plot(sorted_scores, cumulative, linewidth=2,
               color='purple' if bg_type == 'light' else 'magenta')
        ax.fill_between(sorted_scores, 0, cumulative, alpha=0.3,
                       color='purple' if bg_type == 'light' else 'magenta')
        ax.set_xlabel('Score', color='white' if bg_type == 'dark' else 'black')
        ax.set_ylabel('Cumulative Probability',
                     color='white' if bg_type == 'dark' else 'black')
        ax.set_title('Cumulative Score Distribution',
                    color='white' if bg_type == 'dark' else 'black')
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, 5)
        ax.set_ylim(0, 1)
        
        if bg_type == 'dark':
            for ax in axes.flat:
                ax.set_facecolor('none')
                for spine in ax.spines.values():
                    spine.set_color('white')
                ax.tick_params(colors='white')
        
        plt.suptitle('Comprehensive Distribution Analysis',
                    color='white' if bg_type == 'dark' else 'black', fontsize=16)
        plt.tight_layout()
        
        # Save
        for dpi in [300, 1200]:
            plt.savefig(f'distribution_analysis_{bg_type}_{dpi}.png', dpi=dpi,
                       transparent=(bg_type == 'dark'))
        plt.savefig(f'distribution_analysis_{bg_type}_svg.svg',
                   transparent=(bg_type == 'dark'))
        plt.close()

# Main execution
if __name__ == "__main__":
    print("Loading tournament data...")
    data = load_all_data()
    
    if data:
        print(f"\nFound {len(data)} experiments")
        print("\nGenerating comprehensive visualizations...")
        create_comprehensive_visualizations(data)
        print("\nAnalysis complete! Check the current directory for visualization files.")
    else:
        print("No data found in results folder!")