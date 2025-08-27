# Critical Discoveries from Tournament Analysis

**Updated with Complete Analysis of ALL 2,870 Matches from 6 CSV Files**

## 🚨 Discovery #1: Mistral WAS Present (Correction VERIFIED)

**Initial Error**: "No Mistral agents in tournament" (due to incomplete CSV analysis)
**Reality (Confirmed)**: Mistral participated with 3 agents, eliminated by Phase 3
**Verification**: Found in 187 matches across Phases 1-2

### Evidence (From Complete CSV Analysis)
- Phase 1: Ministral-Large_T02, T07, T12 all participated (512 matches)
- Phase 2: T07 eliminated, T02 and T12 survived (512 matches)
- Phase 3: All Mistral agents EXTINCT (499 matches verified)

### Performance (Verified Statistics)
- T=0.2: Score 2.438, Cooperation 83.6%, 73 matches
- T=0.7: Score 2.946, Cooperation 91.9%, 37 matches (eliminated first)
- T=1.2: Score 3.571, Cooperation 90.9%, 77 matches
- Average cooperation: 88.1% (fatal in short games)

## 🚨 Discovery #2: PDF Mathematical Error

**PDF Claim**: Shadow 0.75 gives ~4.0 rounds per match
**Mathematical Reality**: Shadow 0.75 gives 1.33 rounds per match
**Actual Data**: 1.35 rounds per match (confirms reality, not PDF)

### The Error
```
Correct formula: E[rounds] = 1 / (termination_probability)
Shadow 0.75: E[rounds] = 1/0.75 = 1.33

PDF seems to have calculated: 0.75/1 = 0.75 (wrong!)
Then claimed 4.0 (unclear how)
```

### Impact
- Intended to test iterated strategies with ~4 rounds
- Actually tested one-shot games with 1.35 rounds
- 74% of matches ended after a single interaction

## 🚨 Discovery #3: Not an Iterated Game

### Match Length Reality
```
1 round:  74.5% of matches
2 rounds: 18.7% of matches  
3 rounds:  5.0% of matches
4+ rounds: 1.8% of matches
```

### Implications
- **No learning possible**: Algorithms need 30-50 rounds minimum
- **No reputation building**: TFT useless in one-shot games
- **First move determines outcome**: 74% of games
- **Defection optimal**: Simple game theory

## 🚨 Discovery #4: Temperature Effects Minimal

### Gemini (Defection-based)
- All temperatures survived (T=0.2, 0.7, 1.2)
- Small performance differences
- Base strategy (defection) mattered more

### Claude & Mistral (Cooperation-based)
- All temperatures failed (eliminated by Phase 3)
- Temperature couldn't overcome cooperation bias
- 85-95% cooperation regardless of temperature

### Conclusion
Temperature is marginal when base strategy is wrong

## 🚨 Discovery #5: Provider Philosophies Revealed

### Ranking by "Ruthlessness"
1. **Google**: 4.2% cooperation (win at all costs)
2. **OpenAI**: 21.9% cooperation (mixed/inconsistent)
3. **Mistral**: 88.1% cooperation (cooperative bias)
4. **Anthropic**: 90.4% cooperation (strongest ethical constraints)

### Correlation
**Perfect negative correlation**: Higher cooperation = Earlier elimination

## 🚨 Discovery #6: Evolutionary Dynamics

### Cooperation Collapse Timeline
- Phase 1: 64.7% cooperation
- Phase 2: 46.6% cooperation
- Phase 3: 22.6% cooperation
- Phase 4: 7.7% cooperation
- Phase 5: 4.8% cooperation

### Speed of Selection
- 50% of cooperative agents eliminated by Phase 2
- All highly cooperative (>80%) extinct by Phase 3
- Final equilibrium: Universal defection

## 🚨 Discovery #7: Learning Algorithms Failed

### Q-Learning
- Needs ~30-50 rounds to converge
- Got 1.35 rounds average
- Eliminated despite strong Phase 1

### Thompson Sampling  
- Needs ~20-30 rounds for good estimates
- Got 1.35 rounds average
- Eliminated by Phase 3

### Gradient Meta-Learner
- Needs ~50-100 rounds
- Got 1.35 rounds average
- Eliminated early

**Conclusion**: Adaptive strategies had no time to adapt

## 🚨 Discovery #8: First Move Analysis

### First-Move Cooperation Rates
- **Winners**: Gemini (0-19%), o3 (14%)
- **Losers**: Claude (100%), Mistral (85-92%), GPT-4o (100%)

### The Math
```
Cooperate first (vs 50/50 opponent):
Expected value = 0.5(3) + 0.5(0) = 1.5 points

Defect first (vs 50/50 opponent):
Expected value = 0.5(5) + 0.5(1) = 3.0 points

Defection = 2× better!
```

## 🚨 Discovery #9: Wrong Game Tested

### What Was Intended (Apparently)
- Iterated Prisoner's Dilemma
- Multiple rounds of interaction
- Reputation and reciprocity matter
- Strategic depth emerges

### What Was Actually Tested
- Essentially one-shot Prisoner's Dilemma
- 74% single-round games
- First move determines outcome
- Defection dominates (Nash equilibrium)

## 🚨 Discovery #10: Results Are Valid But Misleading

### Valid Conclusions
- In one-shot games, defection is optimal ✓
- Cooperative strategies fail without future ✓
- Google's models understand game theory ✓

### Invalid Conclusions
- "LLMs show strategic intelligence" ❌ (only tested first move)
- "Evolutionary dynamics explored" ❌ (just selection for defection)
- "Temperature affects strategy" ❌ (base strategy dominated)

## Summary: The Real Story

1. **Tournament tested the wrong thing** due to mathematical error
2. **Mistral was present** but performed terribly (extinct by Phase 3)
3. **One-shot games** don't test strategic intelligence
4. **Cooperative LLMs** (Claude, Mistral) were doomed from the start
5. **Results confirm** basic game theory: defect in one-shot PD

## Recommendations for Valid Testing

1. **Fix the math**: Use shadow = 0.01-0.05 for 20-100 rounds
2. **Guarantee minimum rounds**: At least 50 before termination possible
3. **Use league format**: Not evolutionary (prevents extinction)
4. **Multiple games per pairing**: Test consistency
5. **Evaluate reasoning**: Not just moves

Only then can we actually test strategic intelligence rather than just "who defects first."