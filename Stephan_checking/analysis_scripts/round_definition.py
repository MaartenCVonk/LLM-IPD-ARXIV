#!/usr/bin/env python3
"""Clarify what exactly constitutes a 'round' in the IPD tournament"""

import pandas as pd
from pathlib import Path

def analyze_round_structure():
    """Detailed analysis of what a 'round' means"""
    
    print("\n" + "="*80)
    print("UNDERSTANDING 'ROUNDS' IN THE IPD TOURNAMENT")
    print("="*80)
    
    # Load phase 1 data
    df = pd.read_csv('results/experiment_20250811_131553/evolutionary_shadow75_phase1.csv')
    
    print("\n📚 DEFINITION OF A 'ROUND':")
    print("-"*40)
    print("A 'round' is a SINGLE INTERACTION where:")
    print("  1. Both agents simultaneously choose C (Cooperate) or D (Defect)")
    print("  2. Both agents receive payoffs based on the payoff matrix")
    print("  3. After each round, there's a 75% chance the match ENDS")
    print("  4. If the match continues (25% chance), agents play another round")
    
    # Example match analysis
    print("\n" + "="*80)
    print("EXAMPLE MATCH BREAKDOWN")
    print("="*80)
    
    # Find a multi-round match
    match_rounds = df.groupby('match_id')['round'].max()
    multi_round_matches = match_rounds[match_rounds > 2].index.tolist()
    
    if multi_round_matches:
        example_match = multi_round_matches[0]
        match_data = df[df['match_id'] == example_match].sort_values('round')
        
        print(f"\nMatch: {example_match}")
        print(f"Total Rounds: {len(match_data)}")
        print("\nRound-by-Round Breakdown:")
        print("-"*60)
        
        cumulative_score1 = 0
        cumulative_score2 = 0
        
        for idx, row in match_data.iterrows():
            round_num = row['round']
            agent1 = row['agent1'].split('_')[0][:20]
            agent2 = row['agent2'].split('_')[0][:20]
            move1 = row['agent1_move']
            move2 = row['agent2_move']
            
            # Calculate round payoffs
            if (move1, move2) == ('C', 'C'):
                payoff1, payoff2 = 3, 3
                outcome = "Mutual Cooperation"
            elif (move1, move2) == ('C', 'D'):
                payoff1, payoff2 = 0, 5
                outcome = f"{agent2} exploits {agent1}"
            elif (move1, move2) == ('D', 'C'):
                payoff1, payoff2 = 5, 0
                outcome = f"{agent1} exploits {agent2}"
            else:
                payoff1, payoff2 = 1, 1
                outcome = "Mutual Defection"
            
            cumulative_score1 += payoff1
            cumulative_score2 += payoff2
            
            print(f"\nROUND {round_num}:")
            print(f"  {agent1:20} plays: {move1}")
            print(f"  {agent2:20} plays: {move2}")
            print(f"  Outcome: {outcome}")
            print(f"  Round payoffs: {agent1}={payoff1}, {agent2}={payoff2}")
            print(f"  Cumulative scores: {agent1}={cumulative_score1}, {agent2}={cumulative_score2}")
            
            if round_num < len(match_data):
                print(f"  → Match continues (25% chance occurred)")
            else:
                print(f"  → Match ENDS (75% termination occurred)")
    
    # Payoff matrix explanation
    print("\n" + "="*80)
    print("PAYOFF MATRIX (PER ROUND)")
    print("="*80)
    print("""
    Standard Prisoner's Dilemma Payoffs:
    
                     Agent 2
                   C        D
           ┌─────────────────────┐
         C │  (3,3)  │  (0,5)  │
    Agent 1│         │         │
         D │  (5,0)  │  (1,1)  │
           └─────────────────────┘
    
    Where: (Agent1_payoff, Agent2_payoff)
    
    - Both Cooperate (C,C): Both get 3 points
    - Both Defect (D,D): Both get 1 point  
    - One Defects: Defector gets 5, Cooperator gets 0
    """)
    
    # Statistical analysis
    print("\n" + "="*80)
    print("ROUND STATISTICS")
    print("="*80)
    
    # Count total rounds
    total_rounds = len(df)
    total_matches = df['match_id'].nunique()
    
    print(f"\nPhase 1 Statistics:")
    print(f"  Total Matches: {total_matches}")
    print(f"  Total Rounds Played: {total_rounds}")
    print(f"  Average Rounds per Match: {total_rounds/total_matches:.2f}")
    
    # Move distribution
    all_moves = pd.concat([df['agent1_move'], df['agent2_move']])
    move_dist = all_moves.value_counts()
    
    print(f"\nMove Distribution (all rounds):")
    print(f"  Cooperate (C): {move_dist.get('C', 0)} ({move_dist.get('C', 0)/len(all_moves)*100:.1f}%)")
    print(f"  Defect (D): {move_dist.get('D', 0)} ({move_dist.get('D', 0)/len(all_moves)*100:.1f}%)")
    
    # First round vs later rounds
    first_round = df[df['round'] == 1]
    later_rounds = df[df['round'] > 1]
    
    first_moves = pd.concat([first_round['agent1_move'], first_round['agent2_move']])
    first_coop_rate = (first_moves == 'C').mean()
    
    if len(later_rounds) > 0:
        later_moves = pd.concat([later_rounds['agent1_move'], later_rounds['agent2_move']])
        later_coop_rate = (later_moves == 'C').mean()
    else:
        later_coop_rate = 0
    
    print(f"\nCooperation Rates by Round:")
    print(f"  First Round (n={len(first_round)}): {first_coop_rate:.1%} cooperation")
    print(f"  Later Rounds (n={len(later_rounds)}): {later_coop_rate:.1%} cooperation")
    
    # Impact of short matches
    print("\n" + "="*80)
    print("IMPACT OF SHORT MATCH LENGTH")
    print("="*80)
    
    one_round_matches = match_rounds[match_rounds == 1]
    print(f"\nMatches ending after 1 round: {len(one_round_matches)} out of {total_matches}")
    print(f"Percentage: {len(one_round_matches)/total_matches*100:.1f}%")
    
    print("""
    Implications:
    - 74.5% of matches are determined by the FIRST MOVE
    - No opportunity for retaliation or learning in most matches
    - Reputation and reciprocity strategies (TFT, Grim) ineffective
    - Adaptive strategies (Q-Learning, Thompson) can't learn
    - First-move defectors have huge advantage
    
    This is why Gemini (which defected immediately) dominated!
    """)

if __name__ == "__main__":
    analyze_round_structure()