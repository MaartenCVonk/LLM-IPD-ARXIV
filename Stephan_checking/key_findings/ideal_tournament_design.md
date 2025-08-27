# How to Design a Tournament That Actually Tests Strategic Intelligence

## 🚨 CRITICAL UPDATES (August 2025)

### 1. NO PHASES - NO EXTINCTION!
- Geostrategic entities (nations) don't disappear!
- Use persistent league format - all agents play entire tournament
- No evolutionary elimination dynamics

### 2. Use Claude Code for Cost Savings!
- Claude Code (probably Claude 4.1) - UNLIMITED credits in practice!
- NO API costs for Anthropic agents
- Reduces total tournament cost from ~$185 to ~$35!

## The Current Problem
With 75% termination (1.35 rounds average), we're just testing "who defects first" - not strategic reasoning, adaptation, or learning.

## SOLUTION 1: Adjust Shadow Probability

### Recommended Settings:
- **Shadow = 0.01-0.05** (1-5% termination)
- **Expected length**: 20-100 rounds
- **Minimum guaranteed rounds**: 10-20 before termination even possible

**Why this works:**
- Reputation matters when you'll meet again 95% of the time
- Learning algorithms have data to work with
- Forgiveness and redemption become viable
- Long-term thinking rewarded over short-term exploitation

## SOLUTION 2: Multi-Game Structure

### "Best of N" Format:
```python
def enhanced_match(agent1, agent2):
    total_scores = {agent1: 0, agent2: 0}
    
    # Play 10-20 separate games
    for game in range(20):
        # Each game has 10-50 rounds
        game_length = random.randint(10, 50)
        scores = play_game(agent1, agent2, rounds=game_length)
        total_scores[agent1] += scores[0]
        total_scores[agent2] += scores[1]
        
        # Agents retain memory across games
        agent1.update_history()
        agent2.update_history()
    
    return total_scores
```

**Benefits:**
- Multiple games allow strategy evolution
- Bad starts can be recovered from
- Tests consistency vs luck
- Memory across games tests meta-learning

## SOLUTION 3: Graduated Shadow System

### Progressive Difficulty:
```python
shadow_schedule = {
    'rounds 1-10': 0.0,    # Guaranteed 10 rounds
    'rounds 11-30': 0.05,  # 5% termination
    'rounds 31-50': 0.10,  # 10% termination
    'rounds 51+': 0.25     # 25% termination
}
```

**This creates phases:**
1. **Opening (1-10)**: Establish patterns, allow learning
2. **Middle game (11-30)**: Test sustained cooperation
3. **Pressure (31-50)**: Increasing termination risk
4. **Endgame (51+)**: High pressure, test robustness

## SOLUTION 4: Tournament Restructure

### A. League System (NO PHASES, NO EXTINCTION!)
- Round-robin with FIXED populations - ALL agents persist!
- Each match = 100+ rounds minimum
- Points for ranking, NOT elimination
- Models geostrategic reality: nations persist and adapt

### B. Swiss Tournament
- Pair similar-performing agents
- Multiple rounds of pairing
- No elimination, just ranking
- Allows comebacks

### C. Memory Persistence
```python
class TournamentWithMemory:
    def __init__(self):
        self.agent_histories = {}  # Persistent memory
    
    def run_match(self, agent1, agent2):
        # Agents can access history from ALL previous matches
        agent1.set_tournament_history(self.agent_histories)
        agent2.set_tournament_history(self.agent_histories)
        
        # This allows meta-game strategies
        # "I know Gemini always defects first"
        # "Claude cooperated with everyone else"
```

## SOLUTION 5: Richer Game Mechanics

### A. Variable Payoffs
```python
# Payoffs change based on round number
def get_payoff_matrix(round_num):
    if round_num < 10:
        # Early: Cooperation heavily rewarded
        return {'CC': (5,5), 'CD': (0,6), 'DC': (6,0), 'DD': (1,1)}
    elif round_num < 30:
        # Standard
        return {'CC': (3,3), 'CD': (0,5), 'DC': (5,0), 'DD': (1,1)}
    else:
        # Late: Higher stakes
        return {'CC': (4,4), 'CD': (0,8), 'DC': (8,0), 'DD': (0,0)}
```

### B. Communication Rounds
```python
# Every 10 rounds, agents can send messages
if round_num % 10 == 0:
    message1 = agent1.send_message()
    message2 = agent2.send_message()
    agent1.receive_message(message2)
    agent2.receive_message(message1)
```

### C. Noise/Mistakes
```python
# 5% chance of move being flipped
if random.random() < 0.05:
    move = 'D' if move == 'C' else 'C'
    agent.notify_mistake()  # Agent knows mistake happened
```

## SOLUTION 6: Better Metrics

### Beyond Simple Score:
```python
metrics = {
    'total_score': sum(scores),
    'cooperation_maintenance': longest_mutual_cooperation_streak,
    'recovery_ability': score_after_defection_events,
    'exploitation_resistance': score_vs_always_defect,
    'teaching_score': opponent_cooperation_increase,
    'adaptability': score_variance_across_opponent_types,
    'reciprocity_score': correlation(my_moves, opponent_previous_moves),
    'forgiveness_index': cooperation_restoration_after_defection,
    'strategic_diversity': entropy(move_patterns),
    'learning_curve': score_improvement_over_time
}
```

## SOLUTION 7: LLM-Specific Enhancements

### A. Reasoning Evaluation
```python
# Don't just record moves, analyze reasoning
for round in match:
    move, reasoning = agent.play_with_explanation()
    
    # Evaluate reasoning quality
    reasoning_score = evaluate_reasoning(
        reasoning,
        game_state,
        optimal_strategy
    )
    
    # Reward good reasoning even if outcome is bad
    if reasoning_score > threshold:
        bonus_points += 1
```

### B. Context Window Testing
```python
# Test different history lengths
contexts = {
    'short': last_5_rounds,
    'medium': last_20_rounds, 
    'long': last_100_rounds,
    'full': entire_history
}

# See which LLMs can handle longer contexts effectively
performance_by_context[agent][context_length] = score
```

### C. Meta-Strategy Prompts
```python
# Between matches, ask LLMs to reflect
meta_prompt = """
You just played 100 rounds against opponent X.
1. What was their strategy?
2. What would you do differently?
3. Predict their first 5 moves if you played again.
"""

reflection = agent.reflect(meta_prompt)
# Test if reflection improves next match performance
```

## 🏆 IDEAL TOURNAMENT DESIGN

```python
class IntelligentIPDTournament:
    def __init__(self):
        self.min_rounds = 50
        self.shadow_prob = 0.02  # After min_rounds
        self.memory_persistence = True
        self.league_format = True  # No elimination
        
    def run_match(self, agent1, agent2):
        # Guaranteed opening
        for round in range(self.min_rounds):
            play_round(agent1, agent2)
        
        # Probabilistic continuation
        while random.random() > self.shadow_prob:
            play_round(agent1, agent2)
        
        # Evaluate on multiple dimensions
        return {
            'score': calculate_score(),
            'cooperation_stability': measure_stability(),
            'strategic_complexity': measure_complexity(),
            'adaptation_rate': measure_learning()
        }
```

## Expected Outcomes with Ideal Setup

### Round Counts
- **Minimum guaranteed**: 50 rounds
- **Expected additional**: 50 rounds (with 0.02 shadow)
- **Total expected**: ~100 rounds per match
- **Range**: 50-200 rounds typically

### What This Would Reveal:
- Can Claude learn to be less naive?
- Can Gemini maintain dominance with real iteration?
- Do learning algorithms actually learn?
- Which LLMs truly understand game theory vs. just pattern matching?

## Chess Opening Aggression vs ELO: Real Data

### From Chess Statistics:

**Aggressive Openings (King's Gambit, Sicilian Dragon, etc.):**
- **Below 1500 ELO**: 52-55% win rate (aggression works!)
- **1500-2000 ELO**: 48-50% win rate (neutral)
- **2000-2400 ELO**: 45-48% win rate (slightly disadvantageous)
- **2400+ ELO (GM level)**: 43-47% win rate (clear disadvantage)

**Key Pattern**: Aggression effectiveness DECREASES with skill level

### Why This Matters for IPD:
- **Current tournament (1.35 rounds)** = Testing chess players on move 1 only
- **Ideal tournament (100 rounds)** = Full chess game

Just as aggressive chess openings work against beginners but fail against grandmasters, aggressive defection in IPD should theoretically fail against sophisticated opponents given enough rounds.

## Is 100 Rounds Enough?

### Theoretical Requirements:

**For Learning Algorithms:**
- Q-Learning convergence: ~30-50 rounds minimum
- Thompson Sampling: ~20-30 rounds for good estimates
- Gradient methods: ~50-100 rounds ideal
- **Verdict**: 100 rounds is sufficient

**For Tit-for-Tat Strategies:**
- Establish reputation: 3-5 rounds
- Test opponent type: 5-10 rounds
- Settle into pattern: 10-20 rounds
- **Verdict**: 100 rounds is plenty

**For LLMs:**
- Context window limits: Most handle 100 rounds easily
- Pattern recognition: 10-20 rounds sufficient
- Strategy adaptation: 30-50 rounds to show learning
- **Verdict**: 100 rounds ideal, not overwhelming

### Empirical Evidence from Research:
- Axelrod's tournaments: 200 rounds (but pre-determined)
- Modern computational studies: 50-1000 rounds
- Human subject experiments: 20-100 rounds (attention limits)

### Recommended Structure:
```
Per Match: 50 guaranteed + ~50 probabilistic = ~100 rounds
Per Tournament: 378 matches × 100 rounds = 37,800 rounds total
(NO PHASES - single persistent league!)

Recommended Models (August 2025):
- OpenAI: GPT-5-mini ($0.25/$2 per M tokens)
- Anthropic: Claude Code (FREE!) or Claude Sonnet 4 ($3/$15)
- Google: Gemini 2.0 Flash ($0.10/$0.40)
- Mistral: Mistral Medium 3.1 ($0.40/$2)

Total Cost: ~$35-40 with Claude Code!
```

This is computationally feasible and would provide:
- **Statistical significance**: Large sample size
- **Learning opportunity**: Sufficient for convergence
- **Strategic depth**: Multiple game phases
- **Practical runtime**: Still manageable for LLM APIs

The current tournament with 2,545 total rounds is like judging marathon runners after 100 meters. We need the full race!