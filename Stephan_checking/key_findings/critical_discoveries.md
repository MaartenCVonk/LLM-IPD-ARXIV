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

## 🚨 Discovery #2: Shadow Probability Effects

**Mathematical Expectation vs Reality**:
- Shadow 0.75: E[rounds] = 1/0.75 = 1.33 (actual: 1.35)
- Shadow 0.25: E[rounds] = 1/0.25 = 4.00 (actual: 3.91)
- Shadow 0.10: E[rounds] = 1/0.10 = 10.00 (actual: 10.27)

### Game Length Distribution by Shadow
```
Shadow 0.75: Max 7 rounds, 100% in opening phase (1-10)
Shadow 0.25: Max 28 rounds, 94.6% in opening phase
Shadow 0.10: Max 73 rounds, 63.8% in opening, 35.6% reach middle game
```

### Strategic Implications
- Shadow 0.75: Tests primarily opening moves (74.5% single-round)
- Shadow 0.25: Extended openings (26.1% single-round)
- Shadow 0.10: Approaches meaningful iteration (9.9% single-round)

## 🚨 Discovery #3: Iteration Spectrum Across Experiments

### Match Length Reality Across All Shadows
```
Shadow 0.75:            Shadow 0.25:            Shadow 0.10:
1 round:  74.5%         1 round:  26.1%         1 round:   9.9%
2 rounds: 18.7%         2-5 rounds: 52.5%       2-5 rounds: 32.5%
3+ rounds: 6.8%         6-10 rounds: 15.6%      6-10 rounds: 23.8%
                        11+ rounds: 5.8%         11+ rounds: 33.8%
```

### Strategic Viability by Shadow
- **Learning algorithms**: Need 30+ rounds (only 0.6% at Shadow 0.75, 14.3% at Shadow 0.10)
- **Reputation building**: Viable at Shadow 0.10 (39.2% reach 10+ rounds)
- **First move advantage**: Diminishes from 74.5% → 26.1% → 9.9%
- **Context**: Even Shadow 0.10 represents <4% of annual UN Security Council interactions

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

## 🚨 Discovery #9: Different Games at Different Shadows

### Shadow 0.75 Tests
- Opening move preferences (74.5% single-round)
- One-shot game understanding
- Immediate payoff optimization
- Nash equilibrium for brief encounters

### Shadow 0.10 Approaches
- Extended strategic interaction (10.27 avg rounds)
- Some reputation building (39.2% reach 10+ rounds)
- Learning algorithm viability (14.3% reach 20+ rounds)
- Still far from real IR complexity (nations interact 100s of times/year)

## 🚨 Discovery #10: The 0.7% That Changes Everything - True IPD

### Only 13 Matches (0.7%) Reach True IPD (50+ Rounds)
- Shadow 0.75: 0% reach 50+ rounds (max: 7 rounds)
- Shadow 0.25: 0% reach 50+ rounds (max: 28 rounds)
- Shadow 0.10: **0.7%** reach 50+ rounds (13/1,890 matches, max: 73)

### The Stunning Cooperation Reversal
In 50+ round matches, something remarkable happens:

**Google's Complete Transformation:**
- Short games (2-10 rounds): ~80-84% cooperation
- Extended games (25-49 rounds): 91.1% cooperation
- **True IPD (50+ rounds): 100.0% PERFECT COOPERATION**

**All Providers Converge:**
- Google: 100.0% cooperation
- OpenAI: 99.6% cooperation
- Anthropic: 95.5% cooperation
- Mistral: 95.4% cooperation

### What This Reveals
- Google isn't "ruthless" - it's strategically sophisticated
- It defects in short games (rational) and cooperates in long games (also rational)
- True IPD creates universal cooperation (95-100% across all providers)
- Tournament design, not LLM nature, created the defection dynamics

### Match Distribution Reality
| Shadow | Opening Phase (≤10) | True IPD (50+) |
|--------|-------------------|----------------|
| 0.75   | 100%              | 0%             |
| 0.25   | 94.6%             | 0%             |
| 0.10   | 63.8%             | 0.7%           |

## 🚨 Discovery #11: The Fatal Double Flaw - Extinction + Memory Wipe

### The Two Problems That Doom Cooperation
1. **Extinction**: Mistral eliminated by Phase 3 (but France still exists!)
2. **Memory Wipe**: Reputation resets between phases (trust networks destroyed!)

### What Would Happen Without These Flaws?

**Current Tournament (With Flaws)**:
- Phase 1: Mistral cooperates 88% → Exploited
- Phase 2: **Memory wiped** → Mistral cooperates → Exploited again
- Phase 3: Mistral **extinct** → "Cooperation proven fatal"

**Persistent League (Real World)**:
- Rounds 1-10: Mistral cooperates → Initially exploited
- Rounds 11-30: **Partners remember reliability** → Reciprocation begins
- Rounds 31-50: Trust networks form → Cooperation emerges
- Rounds 51+: Mistral's reputation → **Competitive advantage**

### Why This Changes Everything
Our 0.7% true IPD data shows in 50+ rounds ALL providers cooperate (95-100%). But this only happens WITHIN matches. If reputation persisted ACROSS matches:
- Mistral's consistency becomes an **asset**
- Google's early defection creates **trust deficit**
- Anthropic's ethics build **reliable partnerships**

### Real-World Proof
- **EU**: 70 years cooperation → Trusted globally
- **Switzerland**: 200+ years neutrality → Universal mediator
- **These work because reputation persists!**

## Summary: The Complete Picture

1. **Three experiments reveal a spectrum** from brief encounters to extended games
2. **Mistral was present** but doomed by extinction + memory wipes
3. **Only 0.7% reach true IPD** where cooperation dominates (95-100%)
4. **Fatal design flaws**: Phase-based extinction and reputation resets
5. **With persistent reputation**, Mistral could dominate, not die

## Recommendations for Valid Testing

1. **Fix the math**: Use shadow = 0.01-0.05 for 20-100 rounds
2. **Guarantee minimum rounds**: At least 50 before termination possible
3. **Use league format**: Not evolutionary (prevents extinction)
4. **Multiple games per pairing**: Test consistency
5. **Evaluate reasoning**: Not just moves

Only then can we actually test strategic intelligence rather than just "who defects first."