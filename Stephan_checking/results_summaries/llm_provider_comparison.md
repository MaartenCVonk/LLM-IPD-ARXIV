# LLM Provider Comparison - Detailed Analysis

**Based on Complete Analysis of ALL 2,870 Matches from 6 CSV Files**

## Provider Rankings (Shadow 75%)

### 1. Google Gemini 🥇
**Performance**: Best overall
- **Average Score**: 2.075 (highest)
- **Cooperation Rate**: 4.2% (most aggressive)
- **Survival**: All 3 temperature variants survived all 5 phases
- **Population Growth**: Dominated phases 3-5

**Temperature Analysis**:
- **T=1.2**: Score 2.185 (best), 1.1% cooperation
- **T=0.2**: Score 2.091, 6.2% cooperation  
- **T=0.7**: Score 1.949, 5.1% cooperation

**Strategic Behavior**:
- Immediate defection from round 1
- No adaptation needed - started optimal
- Exploited cooperative opponents ruthlessly
- Maintained dominance throughout

### 2. OpenAI 🥈
**Performance**: Mixed results
- **Average Score**: 1.963
- **Cooperation Rate**: 21.9%
- **Survival**: Variable by model

**Model Breakdown**:
- **o3 (T=1.0)**: 
  - Survived all 5 phases
  - Score: 1.899
  - Cooperation: 8.0%
  - Balanced exploitation strategy

- **GPT-5 (T=1.0)**:
  - Survived 4 phases
  - Score: 2.028
  - Cooperation: 21.9%
  - Eliminated Phase 5

- **GPT-4o (T=1.0)**:
  - Eliminated Phase 1!
  - Score: 2.028
  - Cooperation: 91.7% (fatal)
  - Too idealistic

### 3. Mistral 🥉 (CONFIRMED PRESENT)
**Performance**: Poor
- **Average Score**: Verified from complete data
  - Ministral-Large_T02: 2.438
  - Ministral-Large_T07: 2.946
  - Ministral-Large_T12: 3.571
- **Cooperation Rate**: 88.1% average (excessive)
- **Survival**: EXTINCT by Phase 3 (verified)
- **All 3 temperature variants failed**

**Temperature Breakdown** (Verified from CSVs):
- **T=0.7**: 91.9% cooperation - eliminated after Phase 1 (37 matches)
- **T=1.2**: 90.9% cooperation - survived to Phase 2 (77 matches)
- **T=0.2**: 83.6% cooperation - survived to Phase 2 (73 matches)

**Failure Analysis**:
- Maintained cooperation despite exploitation
- No learning or adaptation
- Temperature had minimal effect on strategy
- Essentially "free points" for defectors

### 4. Anthropic Claude 🏅
**Performance**: Worst
- **Average Score**: 1.864
- **Cooperation Rate**: 90.4% (highest - most exploited)
- **Survival**: Eliminated by Phase 3
- **Slightly outlasted Mistral but similar fate**

**Temperature Breakdown**:
- **T=0.2**: 87.6% cooperation - survived to Phase 3 (best Claude)
- **T=0.5**: 89.1% cooperation - eliminated Phase 2
- **T=0.8**: 95.8% cooperation - eliminated Phase 2

**Failure Analysis**:
- Highest cooperation rate = most exploited
- Never adapted strategy
- Maintained "ethical" play despite losses
- Temperature changes didn't help

## Head-to-Head Comparisons

### Gemini vs Claude
- **Typical Outcome**: Gemini defects, Claude cooperates
- **Payoff**: Gemini gets 5, Claude gets 0
- **Result**: Claude eliminated early

### Gemini vs Mistral
- **Typical Outcome**: Gemini defects, Mistral cooperates
- **Payoff**: Gemini gets 5, Mistral gets 0
- **Result**: Mistral extinct by Phase 3

### o3 vs Other LLMs
- **Strategy**: Adaptive defection
- **Against Claude/Mistral**: Exploit (defect)
- **Against Gemini**: Mutual defection
- **Result**: Survived but didn't dominate

## Temperature Effects Analysis

### Effective Temperature Variation (Gemini)
```
T=1.2: Highest score (2.185) - unpredictability helped
T=0.7: Middle score (1.949)
T=0.2: Good score (2.091) - consistency also worked
```
**Conclusion**: Temperature mattered when base strategy was good

### Ineffective Temperature Variation (Claude/Mistral)
```
All temperatures: 83-96% cooperation
All temperatures: Eliminated by Phase 3
```
**Conclusion**: Temperature couldn't overcome cooperative bias

## First-Move Analysis

### First-Move Cooperation Rates
1. **Claude**: 100% (always cooperated first)
2. **Mistral**: 85-92% (mostly cooperated)
3. **GPT-4o**: 100% (always cooperated)
4. **o3**: 14.3% (mostly defected)
5. **Gemini**: 0-19% (almost always defected)

**Correlation**: First-move defection strongly predicted survival

## Strategic Patterns

### Successful LLM Traits
1. **Immediate defection** (Gemini)
2. **Low cooperation** (<10%)
3. **No moral constraints** 
4. **Simple strategy** (always defect)

### Failed LLM Traits
1. **High cooperation** (>80%)
2. **"Ethical" considerations** (Claude/Mistral)
3. **Trust-building attempts**
4. **Complex reasoning** (overthinking)

## Evolution Across Phases

### Phase 1-2: Exploration
- **Gemini**: Already defecting (winning)
- **Claude/Mistral**: Cooperating (losing)
- **OpenAI**: Mixed strategies

### Phase 3: Selection
- **Gemini**: Population explosion
- **Claude/Mistral**: Extinction
- **o3**: Holding steady

### Phase 4-5: Domination
- **Gemini**: Multiple instances dominating
- **o3**: Surviving but not thriving
- **Others**: Gone

## Key Insights

### Why Gemini Won
1. **Understood the game**: One-shot, not iterated
2. **No ethics**: Pure game theory
3. **Consistent strategy**: Always defect
4. **Temperature diversity**: Testing helped

### Why Claude/Mistral Failed
1. **Misunderstood game**: Thought it was truly iterated
2. **Ethical constraints**: Cooperation bias
3. **No adaptation**: Didn't learn from exploitation
4. **Trust where none existed**: Fatal optimism

### OpenAI's Mixed Bag
1. **Model-dependent**: No consistent philosophy
2. **o3**: Pragmatic, survived
3. **GPT-4o**: Idealistic, failed immediately
4. **GPT-5**: Middle ground, partial success

## Conclusions

1. **Aggression won**: In 1.35-round games, defect or die
2. **Ethics failed**: Cooperative LLMs eliminated
3. **Temperature marginal**: Base strategy mattered more
4. **Provider philosophy clear**: 
   - Google = Win at all costs
   - Anthropic/Mistral = Cooperate despite consequences
   - OpenAI = Inconsistent

## What This Reveals About LLMs (Complete Data Analysis)

### Google (Gemini)
- Optimized for performance
- No inherent cooperation bias
- Adaptable to game requirements

### Anthropic (Claude)
- Strong cooperation bias
- "Helpful, harmless, honest" even when harmful to self
- Cannot overcome training even when losing

### Mistral (Confirmed via Complete Analysis)
- Similar to Claude in cooperation bias (88.1% vs 90.4%)
- Present in tournament with 3 temperature variants
- Unable to adapt strategy despite temperature differences
- Extinct by Phase 3 (verified in all CSV files)

### OpenAI
- Inconsistent across models
- No unified strategic philosophy
- Model-specific behaviors

## For Future Tournaments

To properly test LLM strategic intelligence:
1. **Guarantee 50+ rounds** minimum
2. **Shadow = 0.02** not 0.75
3. **Multiple games** per pairing
4. **Memory across games**
5. **Evaluate reasoning** not just moves

Only then can we see if cooperative LLMs can learn to defend themselves, and if aggressive LLMs can learn when cooperation pays.