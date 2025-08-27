# Mathematical Errors in the PDF

## Critical Error: Expected Round Calculations

### What the PDF Claims (Page 2)
> "shadow probabilities of 0.10, 0.25, and 0.75 tested in separate conditions. These correspond to expected round lengths of approximately 1.1, 1.3, and 4.0 moves per match, respectively."

### The Actual Mathematics

The expected number of rounds in a geometric distribution is:
```
E[rounds] = 1 / (termination_probability)
```

### Correct Calculations

| Shadow (Termination) | PDF Claims | Correct Value | Actual Data |
|---------------------|------------|---------------|-------------|
| 0.10 | 1.1 rounds | **10.0 rounds** | Not tested |
| 0.25 | 1.3 rounds | **4.0 rounds** | Not tested |
| 0.75 | 4.0 rounds | **1.33 rounds** | 1.35 rounds ✓ |

### The Error
The PDF appears to have **inverted the formula**, possibly calculating:
- `termination_probability / 1` instead of `1 / termination_probability`

Or confused shadow (continuation probability) with termination probability without adjusting the formula.

## Impact of This Error

### What Was Actually Tested
- **Shadow 0.75** = 75% chance to end = ~1.35 rounds average
- This is essentially a **one-shot game** with 74% of matches ending immediately

### What They Thought They Were Testing  
- **4.0 rounds average** would require shadow = 0.25 (not 0.75)
- This would allow for actual iteration and strategy development

## Verification from Actual Data

### Our Analysis Shows
```python
# Phase 1 Statistics:
Total Matches: 378
Total Rounds: 512
Average: 512/378 = 1.35 rounds

# Theoretical:
Expected = 1/0.75 = 1.33 rounds

# Match: 1.35 ≈ 1.33 ✓
```

### Distribution Verification
```
Theoretical (Shadow=0.75):
- P(1 round) = 0.75 = 75%
- P(2 rounds) = 0.25 × 0.75 = 18.75%
- P(3 rounds) = 0.25² × 0.75 = 4.69%

Actual Data:
- P(1 round) = 74.5% ✓
- P(2 rounds) = 18.7% ✓
- P(3 rounds) = 5.0% ✓
```

Perfect match with theoretical, confirming shadow = 0.75 and average = 1.35 rounds.

## Implications of the Error

### What This Means for Results

#### If They Wanted 4.0 Rounds Average:
- Should have used **shadow = 0.25** (25% termination)
- Would have allowed:
  - Reputation building
  - Learning algorithms to adapt
  - Multiple interactions for reciprocity
  - Actual test of iterated strategies

#### What They Actually Got (1.35 Rounds):
- **74% one-shot games**
- No time for learning
- No reputation effects
- First-move strategy dominates
- Essentially testing single-round Prisoner's Dilemma

### Why Defection Dominated

With correct understanding of 1.35 rounds average:

**Expected Payoff Analysis:**
```
Cooperate First:
- 74% chance: One round only
  - vs C: Get 3 points
  - vs D: Get 0 points
  - Expected (if 50/50): 1.5 points

Defect First:
- 74% chance: One round only
  - vs C: Get 5 points
  - vs D: Get 1 point
  - Expected (if 50/50): 3.0 points

Defection gives 2× expected value!
```

## Other Potential Errors

### Sample Size Claims
- PDF mentions 1,890 matches per tournament
- This is correct (378 matches × 5 phases)
- But with only 1.35 rounds average, total interactions are minimal

### Strategy Analysis
- PDF likely interpreted results thinking games were longer
- Conclusions about "strategic intelligence" are questionable
- What was measured: Opening move preference
- What wasn't measured: Actual strategic adaptation

## Correct Tournament Design

### For Testing Iteration (as seemingly intended):

| Goal | Shadow | Expected Rounds |
|------|--------|-----------------|
| Very short games | 0.75-0.90 | 1.1-1.3 rounds |
| Short games | 0.50 | 2.0 rounds |
| Medium games | 0.25 | 4.0 rounds |
| Long games | 0.10 | 10.0 rounds |
| Very long games | 0.01-0.05 | 20-100 rounds |

### Recommendation
For meaningful IPD testing: **shadow = 0.01-0.05** (20-100 rounds expected)

## Conclusion

This mathematical error fundamentally undermines the tournament's validity for testing iterated game strategies. Instead of testing strategic intelligence in repeated interactions, the tournament actually tested who understood that with 75% termination probability, defection is optimal in what is essentially a one-shot game.

The results are valid for what was actually tested (one-shot dominant strategies), but not for what was apparently intended (iterated strategic intelligence).