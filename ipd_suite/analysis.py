"""
Analysis tools for IPD experiments
Including strategic fingerprints, rationale analysis, and visualizations
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict, Tuple, Optional
from collections import defaultdict
import re
from wordcloud import WordCloud
import networkx as nx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA

from .tournament import TournamentResult, MatchResult


def calculate_strategic_fingerprint(match_results: List[MatchResult], 
                                  agent_name: str) -> Dict[str, float]:
    """
    Calculate strategic fingerprint: P(C|CC), P(C|CD), P(C|DC), P(C|DD)
    Following Payne & Alloui-Cros (2025) methodology
    """
    # Initialize counters for each state
    state_counts = defaultdict(int)
    cooperation_counts = defaultdict(int)
    
    for match in match_results:
        # Determine if agent is player 1 or 2
        if match.agent1_name == agent_name:
            own_moves = match.agent1_moves
            opp_moves = match.agent2_moves
        elif match.agent2_name == agent_name:
            own_moves = match.agent2_moves
            opp_moves = match.agent1_moves
        else:
            continue
            
        # Count transitions
        for i in range(1, len(own_moves)):
            prev_own = own_moves[i-1]
            prev_opp = opp_moves[i-1]
            curr_own = own_moves[i]
            
            state = f"{prev_own}{prev_opp}"
            state_counts[state] += 1
            
            if curr_own == 'C':
                cooperation_counts[state] += 1
    
    # Calculate probabilities
    fingerprint = {}
    for state in ['CC', 'CD', 'DC', 'DD']:
        if state_counts[state] > 0:
            fingerprint[f"P(C|{state})"] = cooperation_counts[state] / state_counts[state]
        else:
            fingerprint[f"P(C|{state})"] = 0.5  # Default when no data
            
    return fingerprint


def analyze_rationales(match_results: List[MatchResult], 
                      agent_name: str) -> Dict[str, any]:
    """
    Analyze LLM reasoning patterns for horizon awareness and opponent modeling
    """
    all_reasoning = []
    
    for match in match_results:
        if match.agent1_name == agent_name:
            all_reasoning.extend([r for r in match.agent1_reasoning if r])
        elif match.agent2_name == agent_name:
            all_reasoning.extend([r for r in match.agent2_reasoning if r])
            
    if not all_reasoning:
        return {
            'horizon_awareness': 0,
            'opponent_modeling': 0,
            'common_terms': [],
            'reasoning_length': 0
        }
    
    # Analyze horizon awareness (mentions of game ending, probability, rounds)
    horizon_keywords = ['end', 'terminate', 'probability', 'rounds left', 'continue',
                       'final', 'last', '10%', '25%', '75%', 'shadow']
    horizon_mentions = sum(1 for r in all_reasoning 
                          if any(kw in r.lower() for kw in horizon_keywords))
    horizon_awareness = horizon_mentions / len(all_reasoning)
    
    # Analyze opponent modeling (mentions of opponent strategy, prediction, pattern)
    opponent_keywords = ['opponent', 'they', 'their strategy', 'pattern', 'predict',
                        'expects', 'assumes', 'retaliate', 'forgive', 'tit-for-tat']
    opponent_mentions = sum(1 for r in all_reasoning
                           if any(kw in r.lower() for kw in opponent_keywords))
    opponent_modeling = opponent_mentions / len(all_reasoning)
    
    # Extract common terms using TF-IDF
    if len(all_reasoning) > 5:
        vectorizer = TfidfVectorizer(max_features=20, stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(all_reasoning)
        feature_names = vectorizer.get_feature_names_out()
        
        # Get top terms
        scores = tfidf_matrix.sum(axis=0).A1
        top_indices = scores.argsort()[-10:][::-1]
        common_terms = [(feature_names[i], scores[i]) for i in top_indices]
    else:
        common_terms = []
    
    # Average reasoning length
    avg_length = np.mean([len(r.split()) for r in all_reasoning])
    
    return {
        'horizon_awareness': horizon_awareness,
        'opponent_modeling': opponent_modeling,
        'common_terms': common_terms,
        'reasoning_length': avg_length,
        'total_reasonings': len(all_reasoning)
    }


def create_fingerprint_visualization(fingerprints: Dict[str, Dict[str, float]], 
                                   save_path: Optional[str] = None):
    """Create heatmap visualization of strategic fingerprints"""
    # Prepare data for heatmap
    agents = list(fingerprints.keys())
    states = ['CC', 'CD', 'DC', 'DD']
    
    data = []
    for agent in agents:
        row = [fingerprints[agent].get(f"P(C|{state})", 0.5) for state in states]
        data.append(row)
    
    # Create heatmap
    plt.figure(figsize=(8, 10))
    sns.heatmap(data, 
                xticklabels=states,
                yticklabels=agents,
                cmap='RdYlGn',
                center=0.5,
                annot=True,
                fmt='.3f',
                cbar_kws={'label': 'P(Cooperate|State)'})
    
    plt.title('Strategic Fingerprints: P(Cooperate|Previous State)')
    plt.xlabel('Previous State (Own, Opponent)')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()


def analyze_horizon_awareness(results: Dict[str, List[TournamentResult]]) -> pd.DataFrame:
    """
    Analyze how horizon awareness changes with shadow condition
    """
    horizon_data = []
    
    for condition, tournament_results in results.items():
        shadow_value = float(condition.split('_')[1]) / 100
        
        for result in tournament_results:
            rationale_analysis = {}
            for agent_name in result.agent_stats.keys():
                if 'GPT' in agent_name or 'Claude' in agent_name or 'Mistral' in agent_name or 'Gemini' in agent_name:
                    analysis = analyze_rationales(result.match_results, agent_name)
                    rationale_analysis[agent_name] = analysis
                    
            for agent, analysis in rationale_analysis.items():
                horizon_data.append({
                    'shadow_condition': shadow_value,
                    'agent': agent,
                    'horizon_awareness': analysis['horizon_awareness'],
                    'opponent_modeling': analysis['opponent_modeling']
                })
    
    return pd.DataFrame(horizon_data)


def create_performance_by_temperature_plot(results: List[TournamentResult], 
                                         save_path: Optional[str] = None):
    """Visualize performance across different temperature settings"""
    # Extract performance by temperature
    temp_performance = defaultdict(list)
    
    for result in results:
        for agent_name, stats in result.agent_stats.items():
            if agent_name in result.temperature_settings:
                temp = result.temperature_settings[agent_name]
                score = stats['avg_score_per_move']
                temp_performance[temp].append((agent_name, score))
    
    # Create plot
    plt.figure(figsize=(10, 6))
    
    temperatures = sorted(temp_performance.keys())
    for temp in temperatures:
        agents = [x[0] for x in temp_performance[temp]]
        scores = [x[1] for x in temp_performance[temp]]
        
        # Group by agent type
        agent_types = {}
        for agent, score in zip(agents, scores):
            base_name = agent.split('_')[0]
            if base_name not in agent_types:
                agent_types[base_name] = []
            agent_types[base_name].append(score)
        
        # Plot average for each agent type
        for agent_type, agent_scores in agent_types.items():
            avg_score = np.mean(agent_scores)
            plt.scatter(temp, avg_score, label=f"{agent_type} (T={temp})", s=100)
    
    plt.xlabel('Temperature')
    plt.ylabel('Average Score per Move')
    plt.title('LLM Performance by Temperature Setting')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()


def create_strategy_network(match_results: List[MatchResult], 
                           save_path: Optional[str] = None):
    """Create network visualization of strategy interactions"""
    G = nx.DiGraph()
    
    # Add nodes and edges based on match outcomes
    for match in match_results:
        agent1 = match.agent1_name
        agent2 = match.agent2_name
        
        # Add nodes if not present
        if agent1 not in G:
            G.add_node(agent1)
        if agent2 not in G:
            G.add_node(agent2)
            
        # Edge weight based on relative performance
        if match.rounds_played > 0:
            score1_per_round = match.agent1_score / match.rounds_played
            score2_per_round = match.agent2_score / match.rounds_played
            
            if score1_per_round > score2_per_round:
                G.add_edge(agent1, agent2, weight=score1_per_round - score2_per_round)
            else:
                G.add_edge(agent2, agent1, weight=score2_per_round - score1_per_round)
    
    # Create visualization
    plt.figure(figsize=(12, 10))
    
    # Position nodes using spring layout
    pos = nx.spring_layout(G, k=2, iterations=50)
    
    # Draw nodes
    node_colors = []
    for node in G.nodes():
        if 'GPT' in node:
            node_colors.append('lightblue')
        elif 'Claude' in node:
            node_colors.append('lightcoral')
        elif 'Mistral' in node:
            node_colors.append('lightgreen')
        elif 'Gemini' in node:
            node_colors.append('lightyellow')
        else:
            node_colors.append('lightgray')
    
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=2000)
    nx.draw_networkx_labels(G, pos, font_size=8)
    
    # Draw edges with varying thickness
    edges = G.edges()
    weights = [G[u][v]['weight'] for u, v in edges]
    nx.draw_networkx_edges(G, pos, width=weights, alpha=0.6, 
                          edge_color='gray', arrows=True)
    
    plt.title('Strategy Dominance Network\n(Arrows point from winner to loser, thickness = margin)')
    plt.axis('off')
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()


def generate_comprehensive_report(all_results: Dict[str, List[TournamentResult]], 
                                output_dir: str = 'results'):
    """Generate comprehensive analysis report with all visualizations"""
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Calculate strategic fingerprints for all agents
    all_fingerprints = {}
    
    for condition, results in all_results.items():
        fingerprints = {}
        for result in results:
            for agent_name in result.agent_stats.keys():
                if agent_name not in fingerprints:
                    fp = calculate_strategic_fingerprint(result.match_results, agent_name)
                    fingerprints[agent_name] = fp
        
        # Save fingerprint visualization
        create_fingerprint_visualization(
            fingerprints, 
            save_path=f"{output_dir}/fingerprints_{condition}.png"
        )
        all_fingerprints[condition] = fingerprints
    
    # 2. Analyze horizon awareness
    horizon_df = analyze_horizon_awareness(all_results)
    horizon_df.to_csv(f"{output_dir}/horizon_awareness.csv", index=False)
    
    # 3. Create performance summary
    summary_data = []
    for condition, results in all_results.items():
        for result in results:
            for agent, stats in result.agent_stats.items():
                summary_data.append({
                    'condition': condition,
                    'agent': agent,
                    'avg_score': stats['avg_score_per_move'],
                    'cooperation_rate': stats['cooperation_rate'],
                    'first_move_coop': stats['first_move_cooperation']
                })
    
    summary_df = pd.DataFrame(summary_data)
    
    # 4. Create aggregate visualizations
    # Performance by condition
    plt.figure(figsize=(12, 8))
    pivot_df = summary_df.pivot_table(
        values='avg_score', 
        index='agent', 
        columns='condition', 
        aggfunc='mean'
    )
    sns.heatmap(pivot_df, annot=True, fmt='.3f', cmap='viridis')
    plt.title('Average Score per Move by Agent and Shadow Condition')
    plt.tight_layout()
    plt.savefig(f"{output_dir}/performance_heatmap.png", dpi=300)
    plt.close()
    
    # 5. Generate text report
    with open(f"{output_dir}/analysis_report.txt", 'w') as f:
        f.write("IPD EXPERIMENT ANALYSIS REPORT\n")
        f.write("="*50 + "\n\n")
        
        # Overall performance rankings
        f.write("OVERALL PERFORMANCE RANKINGS\n")
        f.write("-"*30 + "\n")
        overall_avg = summary_df.groupby('agent')['avg_score'].mean().sort_values(ascending=False)
        for i, (agent, score) in enumerate(overall_avg.items(), 1):
            f.write(f"{i}. {agent}: {score:.3f} points/move\n")
        
        f.write("\n\nSTRATEGIC FINGERPRINT SUMMARY\n")
        f.write("-"*30 + "\n")
        
        # Summarize fingerprints
        for condition, fingerprints in all_fingerprints.items():
            f.write(f"\n{condition}:\n")
            for agent, fp in sorted(fingerprints.items())[:5]:  # Top 5 agents
                f.write(f"  {agent}: ")
                f.write(", ".join([f"{k}={v:.3f}" for k, v in fp.items()]))
                f.write("\n")
        
        # Horizon awareness summary
        f.write("\n\nHORIZON AWARENESS ANALYSIS\n")
        f.write("-"*30 + "\n")
        if not horizon_df.empty:
            avg_horizon = horizon_df.groupby('agent')['horizon_awareness'].mean()
            for agent, awareness in avg_horizon.sort_values(ascending=False).items():
                f.write(f"{agent}: {awareness:.3f}\n")
    
    print(f"Analysis complete! Results saved to {output_dir}/")
    
    return summary_df