# LLM Provider Comparison - Complete Analysis Across All Experiments

**Based on 5,670 Total Matches Across Three Shadow Values**

## 🔥 CRITICAL DISCOVERY: Google's Complete Transformation in True IPD

### The Cooperation Reversal by Match Length
| Provider | 1 Round | 2-5 Rounds | 6-10 Rounds | 25-49 Rounds | **50+ Rounds** |
|----------|---------|------------|-------------|--------------|----------------|
| Google   | 100%*   | 83.9%      | 80.4%       | 91.1%        | **100.0%**     |
| OpenAI   | 100%*   | 87.0%      | 83.8%       | 86.7%        | **99.6%**      |
| Anthropic| 100%*   | 90.6%      | 84.4%       | 88.1%        | **95.5%**      |
| Mistral  | 94.9%   | 95.8%      | 93.9%       | 95.1%        | **95.4%**      |

*Single-round rates can be misleading due to small samples

**Key Insight**: Google achieves PERFECT COOPERATION in true IPD (50+ rounds), completely reversing its "ruthless" reputation from short games. This reveals sophisticated game-theoretic understanding: defect when rational (short games), cooperate when rational (long games).

### True IPD Statistics (Only 0.7% of Shadow 0.10 Matches)
- **Total matches reaching 50+ rounds**: 13 out of 1,890 (0.7%)
- **Google in true IPD**: 100% cooperation, 176 avg score
- **OpenAI in true IPD**: 99.6% cooperation, 173.5 avg score
- **Anthropic in true IPD**: 95.5% cooperation, 156.3 avg score
- **Mistral in true IPD**: 95.4% cooperation, 61.7 avg score (still lowest)

## 🔥 THE RANKING REVERSAL: How Persistent Reputation Changes Everything

### Current Rankings (With Fatal Flaws)
1. **Google** 🥇 - Wins by exploiting before memory wipes
2. **OpenAI** 🥈 - Mixed strategy survives phases
3. **Mistral** 💀 - Dies Phase 3 (cooperation "fatal")
4. **Anthropic** 💀 - Dies Phase 4 (ethics "fatal")

### Possible Rankings (With Persistent Reputation)
1. **Mistral** ❓ - 88% cooperation → Could build trust → Might thrive
2. **Anthropic** ❓ - Ethical consistency → Could form reliable alliances
3. **OpenAI** ❓ - Inconsistency → Reputation volatility
4. **Google** ❓ - Early defection → Might create trust deficit OR adapt

**The Untested Possibility**: Our 0.7% true IPD data shows ALL providers converge on 95-100% cooperation in long games. With persistent reputation:
- Mistral's early cooperation MIGHT become an asset (like EU's strategy)
- Google's sophistication MIGHT lead to adaptive cooperation
- We simply don't know - the tournament design prevented testing this
- Real world examples (EU, Switzerland) suggest consistent cooperation CAN work

## Provider Rankings Across All Shadow Values (Current Flawed Tournament)

### 1. Google Gemini 🥇 (Benefits from Fatal Flaws)
**Performance**: Best overall in flawed design
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