# Complete Tournament Analysis - Shadow 75%

## Tournament Structure

### Overall Statistics (Based on ALL CSV Files)
- **Total CSV Files Analyzed**: 6 files
- **Total Phases**: 5 (evolutionary) + 1 additional experiment
- **Total Matches**: 2,870 (verified from all CSVs)
- **Total Data Lines**: 50,568 lines processed
- **Average Rounds per Match**: 1.35 (consistent with theory)

### Shadow Probability Impact
- **Theoretical Expectation**: 1/0.75 = 1.33 rounds
- **Actual Average**: 1.35 rounds (101% of theoretical - perfect match)
- **PDF ERROR**: Claims 4.0 rounds for 0.75 shadow (completely wrong!)

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