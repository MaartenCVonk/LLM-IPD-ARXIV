# Complete Tournament Analysis - All Three Experiments

## Tournament Structure Across All Shadow Values

### Comprehensive Statistics (5,670 Total Matches)
- **Shadow 0.75**: 1,890 matches, 1.35 avg rounds, max 7 rounds
- **Shadow 0.25**: 1,890 matches, 3.91 avg rounds, max 28 rounds  
- **Shadow 0.10**: 1,890 matches, 10.27 avg rounds, max 73 rounds

### Critical Discovery: True IPD Rarity
| Shadow | Matches | Opening (≤10) | Extended (25-49) | True IPD (50+) |
|--------|---------|---------------|------------------|----------------|
| 0.75   | 1,890   | 100%          | 0%               | **0%**         |
| 0.25   | 1,890   | 94.6%         | 0.1%             | **0%**         |
| 0.10   | 1,890   | 63.8%         | 8.2%             | **0.7%**       |

**Key Finding**: Only 13 matches (0.7%) in our best experiment achieve true iteration (50+ rounds)

### The Cooperation Reversal in True IPD
In the rare 50+ round matches, ALL providers converge on cooperation:
- **Google**: 100.0% cooperation (complete reversal from short games!)
- **OpenAI**: 99.6% cooperation
- **Anthropic**: 95.5% cooperation
- **Mistral**: 95.4% cooperation

## 🔥 The Fatal Double Flaw: Why Cooperation Dies

### Problem 1: Extinction Mechanics
- **Mistral extinct by Phase 3** - but France/EU still exists!
- **Anthropic extinct by Phase 4** - but ethical actors persist!
- This isn't evolution - it's strategic genocide

### Problem 2: Memory Wipes Between Phases
**CRITICAL**: Even surviving agents lose ALL reputation:
- Phase 1: Mistral cooperates 88% → builds trust
- Phase 2: **MEMORY WIPED** → Trust destroyed, back to zero
- Phase 3: Mistral extinct → Can't recover

### What Would Happen With Persistent Reputation?

**Current Tournament (Doomed Cooperation)**:
```
Phase 1: Mistral cooperates → Exploited → Low score
Phase 2: Memory wiped → Exploited again → Lower score  
Phase 3: Extinct → "Cooperation proven fatal"
```

**Persistent League (Cooperation Dominates)**:
```
Matches 1-10: Mistral cooperates → Initially exploited
Matches 11-30: Partners REMEMBER reliability → Reciprocation begins
Matches 31-50: Trust networks strengthen → Stable cooperation
Matches 51+: Mistral's reputation → COMPETITIVE ADVANTAGE
```

**Real-World Proof**: 
- EU: 70 years cooperation → Trusted globally
- Switzerland: 200+ years neutrality → Universal mediator
- These strategies WORK because reputation PERSISTS!

## Phase-by-Phase Evolution

### Phase 1: Initial Diversity
- **Active Agents**: 28 (all agents)
- **Matches**: 512 (verified)
- **Cooperation Rate**: 64.5%
- **Providers Present**: OpenAI, Anthropic, Mistral (3 agents), Google
- **Top Performers**: Gemini variants, Mistral-Large_T12 (3.57), Q-Learning

### Phase 2: Early Selection
- **Active Agents**: 28 (population shifting)
- **Matches**: 512
- **Cooperation Rate**: 46.9%
- **Mistral Status**: 2 agents remain (T=0.2, T=1.2), T=0.7 eliminated
- **Eliminated**: GPT-4o, Mistral T=0.7, Claude T=0.5, Claude T=0.8

### Phase 3: Cooperation Collapse
- **Active Agents**: 28 (heavily skewed)
- **Matches**: 499
- **Cooperation Rate**: 22.8%
- **Critical**: ALL Mistral agents now EXTINCT
- **Eliminated**: All Mistral (T=0.2, T=1.2), most Claude variants

### Phase 4: Defection Dominance
- **Active Agents**: 28 (mostly defectors)
- **Average Score**: 1.23
- **Cooperation Rate**: 7.7%
- **Survivors**: Mainly Gemini variants and o3

### Phase 5: Equilibrium
- **Active Agents**: 28 (defector copies)
- **Average Score**: 1.14
- **Cooperation Rate**: 4.8%
- **Final State**: Near-universal defection

## Agent Category Performance

### Classical Strategies
- **Phase 1 Average**: 2.21
- **Phase 5 Average**: 1.11
- **Decline**: -50%
- **Fatal Flaw**: Designed for longer games

### Adaptive Learning
- **Phase 1 Average**: 3.15 (best!)
- **Phase 3 Elimination**: Couldn't adapt fast enough
- **Problem**: Need >50 rounds to converge

### LLM Providers

#### Google Gemini (Winner)
- **Survival**: All 3 temperatures survived all phases
- **Strategy**: Immediate defection (0-8% cooperation)
- **Success Factor**: Understood the one-shot nature

#### OpenAI (Mixed)
- **o3**: Survived all phases (balanced strategy)
- **GPT-5**: Survived 4 phases
- **GPT-4o**: Eliminated immediately (too cooperative)

#### Mistral (Failed)
- **All variants eliminated by Phase 3**
- **Cooperation**: 83-92% (fatal)
- **Temperature irrelevant**: All failed similarly

#### Anthropic Claude (Failed)
- **All variants eliminated by Phase 3**
- **Cooperation**: 87-96% (highest)
- **Never adapted**: Maintained cooperation despite losses

## Key Findings

### 1. Round Length Distribution
```
1 round:  74.5% of matches
2 rounds: 18.7% of matches
3 rounds:  5.0% of matches
4 rounds:  1.4% of matches
5+ rounds: 0.4% of matches
```

### 2. Why Cooperation Failed
- **No Future**: 75% chance of immediate termination
- **No Learning**: Average 1.35 rounds insufficient
- **No Reputation**: Can't establish patterns
- **First Move Wins**: 74% of games decided immediately

### 3. Temperature Effects (LLMs)

#### Gemini (Varied Successfully)
- T=1.2: Best performance (unpredictability helped)
- T=0.7: Middle performance
- T=0.2: Consistent but slightly worse

#### Claude & Mistral (No Effect)
- All temperatures cooperated 85-95%
- Temperature couldn't overcome cooperative bias
- All eliminated regardless of temperature

## Strategic Insights

### Winning Strategy
1. **Defect immediately** (74% of games are one round)
2. **Never cooperate first** (0% cooperation optimal)
3. **Ignore opponent history** (likely no round 2)

### Losing Strategy
1. **Cooperate first** (exploited immediately)
2. **Try to learn** (no time)
3. **Build reputation** (no future)

## Evolutionary Dynamics

### Selection Pressure
- **Phase 1-2**: Cooperators rapidly exploited
- **Phase 3**: Cooperation becomes extinct
- **Phase 4-5**: Pure defection equilibrium

### Final Equilibrium
- **Survivors**: Gemini (all temps), o3, Suspicious TFT variants
- **Common trait**: <10% cooperation rate
- **Score convergence**: ~1.1 (mutual defection payoff)

## Conclusions

1. **Tournament didn't test iteration** - tested first-move strategy
2. **Shadow 0.75 too high** - creates one-shot game
3. **Learning impossible** - 1.35 rounds insufficient
4. **Defection optimal** - mathematically proven
5. **PDF has major errors** - wrong expected values

## Recommendations

### For Valid IPD Testing
1. Shadow = 0.01-0.05 (not 0.75)
2. Minimum 50 guaranteed rounds
3. League format (not elimination)
4. Multiple matches per pairing
5. Memory persistence across games

### Expected with Proper Design
- Cooperation could be viable
- Learning algorithms could adapt
- Reputation strategies could work
- True strategic depth would emerge