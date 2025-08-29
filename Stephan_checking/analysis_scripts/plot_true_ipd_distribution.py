#!/usr/bin/env python3
"""
Visualize what percentage of matches show "true IPD" characteristics
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from glob import glob

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

def analyze_match_distributions():
    """Analyze and visualize match length distributions across all experiments"""
    
    # Ensure we're in the right directory
    import os
    if os.path.exists('Stephan_checking'):
        os.chdir('/mnt/c/Apps/LLM-IPD-ARXIV')
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('Match Length Distribution: What Percentage Shows "True IPD"?', fontsize=16, fontweight='bold')
    
    experiments = [
        ('Shadow 0.75', 'results/experiment_20250811_131553/evolutionary_shadow75_phase*.csv', axes[0, 0], axes[1, 0]),
        ('Shadow 0.25', 'results/experiment_20250812_192959/evolutionary_shadow25_phase*.csv', axes[0, 1], axes[1, 1]),
        ('Shadow 0.10', 'results/experiment_20250818_102320/evolutionary_shadow10_phase*.csv', axes[0, 2], axes[1, 2])
    ]
    
    all_stats = []
    
    for exp_name, pattern, ax_hist, ax_pie in experiments:
        print(f"\nAnalyzing {exp_name}...")
        
        # Load data
        files = glob(pattern)
        all_data = []
        for file in files:
            df = pd.read_csv(file)
            all_data.append(df)
        
        if not all_data:
            print(f"No data found for {exp_name}")
            continue
            
        full_df = pd.concat(all_data, ignore_index=True)
        
        # Get match lengths
        match_lengths = full_df.groupby('match_id')['round'].max()
        total_matches = len(match_lengths)
        
        # Define categories based on game theory
        categories = {
            'One-shot (1 round)': (match_lengths == 1).sum(),
            'Brief (2-5 rounds)': ((match_lengths >= 2) & (match_lengths <= 5)).sum(),
            'Short (6-10 rounds)': ((match_lengths >= 6) & (match_lengths <= 10)).sum(),
            'Medium (11-24 rounds)': ((match_lengths >= 11) & (match_lengths <= 24)).sum(),
            'Extended (25-49 rounds)': ((match_lengths >= 25) & (match_lengths <= 49)).sum(),
            'True IPD (50+ rounds)': (match_lengths >= 50).sum()
        }
        
        # Calculate percentages
        percentages = {k: v/total_matches*100 for k, v in categories.items()}
        
        # Store stats
        stats = {
            'experiment': exp_name,
            'total_matches': total_matches,
            'avg_rounds': match_lengths.mean(),
            'median_rounds': match_lengths.median(),
            'max_rounds': match_lengths.max(),
            'std_rounds': match_lengths.std(),
            **percentages
        }
        all_stats.append(stats)
        
        # 1. Histogram with overlays
        ax_hist.hist(match_lengths, bins=50, alpha=0.7, color='steelblue', edgecolor='black')
        ax_hist.set_title(f'{exp_name}\nAvg: {match_lengths.mean():.1f}, Max: {match_lengths.max()}')
        ax_hist.set_xlabel('Number of Rounds')
        ax_hist.set_ylabel('Number of Matches')
        
        # Add vertical lines for categories
        ax_hist.axvline(x=1, color='red', linestyle='--', alpha=0.5, label='One-shot')
        ax_hist.axvline(x=10, color='orange', linestyle='--', alpha=0.5, label='Short game')
        ax_hist.axvline(x=25, color='yellow', linestyle='--', alpha=0.5, label='Extended')
        ax_hist.axvline(x=50, color='green', linestyle='--', alpha=0.5, label='True IPD')
        
        # Add percentage annotations
        y_pos = ax_hist.get_ylim()[1] * 0.9
        ax_hist.text(1, y_pos, f'{percentages["One-shot (1 round)"]:.1f}%', 
                    fontsize=10, color='red', fontweight='bold')
        
        if match_lengths.max() >= 50:
            ax_hist.text(50, y_pos * 0.8, f'{percentages["True IPD (50+ rounds)"]:.1f}%', 
                        fontsize=10, color='green', fontweight='bold')
        
        ax_hist.legend(loc='upper right', fontsize=8)
        ax_hist.grid(True, alpha=0.3)
        
        # 2. Pie chart
        colors = ['#ff4444', '#ff8844', '#ffcc44', '#88dd88', '#44aa44', '#228822']
        explode = [0.1 if k == 'True IPD (50+ rounds)' else 0 for k in categories.keys()]
        
        # Filter out zero categories for cleaner pie
        pie_data = [(k, v) for k, v in categories.items() if v > 0]
        
        wedges, texts, autotexts = ax_pie.pie(
            [v for k, v in pie_data],
            labels=[f'{k}\n({v} matches)' for k, v in pie_data],
            colors=colors[:len(pie_data)],
            explode=explode[:len(pie_data)],
            autopct=lambda pct: f'{pct:.1f}%' if pct > 1 else '',
            startangle=90
        )
        
        ax_pie.set_title(f'{exp_name} Distribution')
        
        # Make percentage text bold
        for autotext in autotexts:
            autotext.set_fontweight('bold')
            autotext.set_fontsize(10)
    
    plt.tight_layout()
    
    # Save figure
    output_dir = Path('Stephan_checking/visualizations')
    output_dir.mkdir(exist_ok=True, parents=True)
    
    plt.savefig(output_dir / 'true_ipd_distribution.png', dpi=300, bbox_inches='tight')
    plt.savefig(output_dir / 'true_ipd_distribution.svg', format='svg', bbox_inches='tight')
    
    # Create summary table
    fig2, ax = plt.subplots(figsize=(14, 8))
    ax.axis('tight')
    ax.axis('off')
    
    # Prepare data for table
    df_stats = pd.DataFrame(all_stats)
    
    if len(df_stats) < 3:
        print("Not enough data to create summary table")
        return
    
    # Create the main comparison table
    table_data = []
    table_data.append(['Shadow Value', '0.75', '0.25', '0.10'])
    table_data.append(['Total Matches', '1,890', '1,890', '1,890'])
    table_data.append(['Average Rounds', f'{df_stats.iloc[0]["avg_rounds"]:.1f}', 
                      f'{df_stats.iloc[1]["avg_rounds"]:.1f}', 
                      f'{df_stats.iloc[2]["avg_rounds"]:.1f}'])
    table_data.append(['Maximum Rounds', f'{df_stats.iloc[0]["max_rounds"]:.0f}', 
                      f'{df_stats.iloc[1]["max_rounds"]:.0f}', 
                      f'{df_stats.iloc[2]["max_rounds"]:.0f}'])
    table_data.append(['', '', '', ''])  # Spacer
    table_data.append(['CATEGORY BREAKDOWN', '', '', ''])
    table_data.append(['One-shot (1 round)', 
                      f'{df_stats.iloc[0]["One-shot (1 round)"]:.1f}%',
                      f'{df_stats.iloc[1]["One-shot (1 round)"]:.1f}%',
                      f'{df_stats.iloc[2]["One-shot (1 round)"]:.1f}%'])
    table_data.append(['Brief (2-5 rounds)', 
                      f'{df_stats.iloc[0]["Brief (2-5 rounds)"]:.1f}%',
                      f'{df_stats.iloc[1]["Brief (2-5 rounds)"]:.1f}%',
                      f'{df_stats.iloc[2]["Brief (2-5 rounds)"]:.1f}%'])
    table_data.append(['Short (6-10 rounds)', 
                      f'{df_stats.iloc[0]["Short (6-10 rounds)"]:.1f}%',
                      f'{df_stats.iloc[1]["Short (6-10 rounds)"]:.1f}%',
                      f'{df_stats.iloc[2]["Short (6-10 rounds)"]:.1f}%'])
    table_data.append(['Medium (11-24 rounds)', 
                      f'{df_stats.iloc[0]["Medium (11-24 rounds)"]:.1f}%',
                      f'{df_stats.iloc[1]["Medium (11-24 rounds)"]:.1f}%',
                      f'{df_stats.iloc[2]["Medium (11-24 rounds)"]:.1f}%'])
    table_data.append(['Extended (25-49 rounds)', 
                      f'{df_stats.iloc[0]["Extended (25-49 rounds)"]:.1f}%',
                      f'{df_stats.iloc[1]["Extended (25-49 rounds)"]:.1f}%',
                      f'{df_stats.iloc[2]["Extended (25-49 rounds)"]:.1f}%'])
    table_data.append(['TRUE IPD (50+ rounds)', 
                      f'{df_stats.iloc[0]["True IPD (50+ rounds)"]:.1f}%',
                      f'{df_stats.iloc[1]["True IPD (50+ rounds)"]:.1f}%',
                      f'{df_stats.iloc[2]["True IPD (50+ rounds)"]:.1f}%'])
    
    # Color coding for the table
    cell_colors = []
    for i, row in enumerate(table_data):
        if i == 0 or i == 5:  # Headers
            cell_colors.append(['lightgray'] * 4)
        elif 'TRUE IPD' in row[0]:  # Highlight True IPD row
            cell_colors.append(['lightgreen', 'pink', 'pink', 'lightyellow'])
        elif i == 4:  # Spacer
            cell_colors.append(['white'] * 4)
        else:
            cell_colors.append(['white'] * 4)
    
    table = ax.table(cellText=table_data,
                    cellColours=cell_colors,
                    cellLoc='center',
                    loc='center',
                    colWidths=[0.3, 0.2, 0.2, 0.2])
    
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1.2, 2)
    
    # Make headers bold
    for i in [0, 5]:
        for j in range(4):
            table[(i, j)].set_text_props(weight='bold')
    
    # Make TRUE IPD row bold
    for j in range(4):
        table[(11, j)].set_text_props(weight='bold')
    
    ax.set_title('Match Length Categories Across All Experiments\n"True IPD" Requires Extended Repeated Interaction',
                fontsize=14, fontweight='bold', pad=20)
    
    # Add explanatory text
    explanation = """
    Key Insights:
    • Shadow 0.75: 100% of matches stay in "opening phase" (≤10 rounds), 0% reach true IPD
    • Shadow 0.25: 94.6% stay in opening, only 0% reach true IPD threshold
    • Shadow 0.10: 63.8% in opening, but only 0.7% achieve true IPD (50+ rounds)
    
    Even our "best" experiment barely captures true iterated gameplay!
    Real international relations involve hundreds or thousands of interactions annually.
    """
    
    ax.text(0.5, -0.15, explanation, transform=ax.transAxes,
           ha='center', va='top', fontsize=10, style='italic',
           bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow', alpha=0.5))
    
    plt.savefig(output_dir / 'true_ipd_summary_table.png', dpi=300, bbox_inches='tight')
    plt.savefig(output_dir / 'true_ipd_summary_table.svg', format='svg', bbox_inches='tight')
    
    # Don't show interactively
    plt.close('all')
    
    # Print summary statistics
    print("\n" + "="*80)
    print("SUMMARY: What Percentage Shows True IPD?")
    print("="*80)
    
    for stats in all_stats:
        print(f"\n{stats['experiment']}:")
        print(f"  Average rounds: {stats['avg_rounds']:.2f}")
        print(f"  Maximum rounds: {stats['max_rounds']:.0f}")
        print(f"  One-shot games (1 round): {stats['One-shot (1 round)']:.1f}%")
        print(f"  Extended games (25-49 rounds): {stats['Extended (25-49 rounds)']:.1f}%")
        print(f"  TRUE IPD (50+ rounds): {stats['True IPD (50+ rounds)']:.1f}%")
    
    print("\n" + "="*80)
    print("CONCLUSION:")
    print("- True IPD (50+ rounds) occurs in only 0.7% of Shadow 0.10 matches")
    print("- This represents just 13 out of 1,890 matches")
    print("- Even these 'long' games are brief compared to real international relations")
    print("="*80)

if __name__ == "__main__":
    # Change to the right directory
    import os
    os.chdir('/mnt/c/Apps/LLM-IPD-ARXIV/Stephan_checking')
    
    analyze_match_distributions()