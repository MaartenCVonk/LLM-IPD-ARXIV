
# Multi-Tournament Cost Analysis

## Overview

This document presents a detailed cost analysis of three simulated tournaments involving **28 agents** (12 commercial LLMs and 16 free agents), executed over **5 full phases**. Each phase operates under a **round-robin format**, where every agent plays every other agent once. This yields \(\binom{28}{2} = 378\) matches per phase and **1,890 matches per tournament**.

Each tournament differs in the number of **expected rounds per match** due to varying task complexity:

- **Tournament 1**: 10 rounds per match  
- **Tournament 2**: 4 rounds per match  
- **Tournament 3**: 1.33 rounds per match

Costs are analysed under two distinct agent participation scenarios:

---

## Agent Types and Cost Structure

| Model Type       | Cost per Round (USD) |
|------------------|----------------------|
| Claude Opus 4    | $0.02536             |
| Gemini Pro 2.5   | $0.00726             |
| GPT O3           | $0.00673             |
| Mistral Large    | $0.00204             |
| Free Agents      | $0.00000             |

---

## Scenario A: Base (Static Agent Composition)

In the base scenario, each of the 12 LLM agents (3 per model) plays against every other agent in all 5 phases, resulting in:

- **135 matches per LLM agent per tournament** (27 per phase × 5 phases)  
- API calls per model: \(3 \times 135 \times \text{rounds per match}\)

### Base Scenario Cost Summary

| Tournament        | Total Cost (USD) |
|------------------|------------------|
| Tournament 1 (10%) | $167.63          |
| Tournament 2 (25%) | $67.06           |
| Tournament 3 (75%) | $22.27           |
| **Total**          | **$256.96**      |

This scenario assumes that agent populations remain constant across all phases and that no selection or replacement occurs during tournament evolution.

---

## Scenario B: Evolving Agent Composition

In this dynamic scenario, agent populations change after each phase to reflect evolutionary success. Claude Opus 4, being the most costly, becomes increasingly dominant:

### Claude Opus 4 Representation by Phase

| Phase | Agents |
|-------|--------|
| 1     | 3      |
| 2     | 6      |
| 3     | 9      |
| 4     | 12     |
| 5     | 15     |

Other models are gradually reduced, e.g., Mistral Large is phased out by Phase 4.

Each agent still plays 27 matches per phase, but total API calls per model now depend on evolving representation.

### Evolving Scenario Cost Summary

| Tournament        | Total Cost (USD) |
|------------------|------------------|
| Tournament 1 (10%) | $357.19          |
| Tournament 2 (25%) | $142.88          |
| Tournament 3 (75%) | $47.51           |
| **Total**          | **$547.58**      |

This reflects an upper-bound estimate where high-cost agents are selected more frequently over time due to superior performance, increasing the cumulative API cost.

---

## Conclusion

The total API expenditure varies significantly depending on whether the agent composition remains static or evolves:

| Scenario        | Total Cost (USD) |
|----------------|------------------|
| Base (Static)  | $256.96          |
| Evolving       | $547.58          |

The evolving scenario incurs **over twice the cost** of the static scenario, emphasising the financial impact of agent selection dynamics in evolutionary tournament structures.
