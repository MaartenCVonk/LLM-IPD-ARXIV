# Experimental Design and Implementation: Extending Payne & Alloui-Cros (2025)
## A Comprehensive Analysis of LLM Strategic Behavior in the Iterated Prisoner's Dilemma

### Table of Contents
1. [Executive Summary](#executive-summary)
2. [Background and Motivation](#background-and-motivation)
3. [Original Research Design (Payne & Alloui-Cros 2025)](#original-research-design)
4. [Our Extended Implementation](#our-extended-implementation)
5. [Key Methodological Enhancements](#key-methodological-enhancements)
6. [Technical Architecture](#technical-architecture)
7. [Experimental Parameters](#experimental-parameters)
8. [Data Collection and Analysis Framework](#data-collection-and-analysis)
9. [Current Status and Preliminary Observations](#current-status)
10. [Expected Contributions](#expected-contributions)

---

## 1. Executive Summary

This document details our comprehensive implementation and extension of the groundbreaking research by Payne & Alloui-Cros (2025) on Large Language Model (LLM) behavior in the Iterated Prisoner's Dilemma (IPD). While the original study established the first evolutionary IPD tournaments featuring LLMs, our implementation significantly expands the scope through:

- **Broader Model Coverage**: Testing 4 LLM providers (OpenAI, Anthropic, Mistral, Google) versus the original 3
- **Temperature Variation Analysis**: Systematic exploration of temperature effects (0.2, 0.7, 1.2) on strategic behavior
- **Enhanced Strategy Library**: 12 classical/behavioral/adaptive strategies versus canonical strategies only
- **Real-time Monitoring**: Live progress tracking and incremental result saving
- **Open Framework**: Fully documented, modular codebase for reproducibility and extension

Our experiment is currently running, processing 1,656 total matches across three shadow conditions, with sophisticated error handling for API limitations and automatic recovery mechanisms.

---

## 2. Background and Motivation

### 2.1 The Significance of IPD in AI Research

The Iterated Prisoner's Dilemma represents a fundamental paradigm for understanding cooperation, competition, and strategic decision-making. As Payne & Alloui-Cros note, it serves as a bridge between "classic game theory with machine psychology," providing insights into how AI systems might behave in multi-agent environments.

### 2.2 Why Study LLM Strategic Behavior?

As LLMs increasingly interact with humans and other AI systems in real-world applications, understanding their strategic tendencies becomes crucial for:
- Predicting behavior in competitive markets
- Designing robust multi-agent systems
- Ensuring aligned AI behavior in cooperative scenarios
- Understanding emergent properties of AI decision-making

### 2.3 Research Gap Addressed

While Payne & Alloui-Cros established the foundational framework, several questions remained unexplored:
1. How does temperature affect LLM strategic behavior?
2. Can adaptive learning strategies outperform both classical strategies and LLMs?
3. How do newer models (Mistral, updated Claude/GPT versions) compare?
4. What role does forgiveness play in evolutionary success against LLMs?

---

## 3. Original Research Design (Payne & Alloui-Cros 2025)

### 3.1 Core Methodology

The original study implemented:
- **Evolutionary tournaments** pitting canonical strategies against LLM agents
- **Variable termination probability** to study the "shadow of the future"
- **Strategic fingerprint analysis** examining P(C|state) for different game states
- **Rationale analysis** of ~32,000 prose explanations

### 3.2 Models Tested

1. **OpenAI models** (specific versions not detailed in abstract)
2. **Google Gemini** models
3. **Anthropic Claude** models

### 3.3 Key Findings

The study revealed distinct strategic personalities:
- **Gemini**: "Strategically ruthless" - more exploitative behavior
- **OpenAI**: "Highly cooperative" - strong cooperation bias
- **Claude**: "Most forgiving reciprocator" - balanced approach with forgiveness

### 3.4 Limitations of Original Design

Based on the abstract, potential limitations include:
- No systematic temperature variation study
- Limited to canonical strategies (likely TFT, ALLD, ALLC, etc.)
- No adaptive/learning strategies tested
- No cross-model version comparisons

---

## 4. Our Extended Implementation

### 4.1 Expanded Model Coverage

We test 4 LLM providers with specific model versions:

```python
LLM_MODELS = {
    "OpenAI": "gpt-4o-mini",        # Cost-effective, latest architecture
    "Anthropic": "claude-3-sonnet-20240229",  # Balanced performance
    "Mistral": "mistral-large-latest",        # New addition
    "Google": "gemini-1.5-flash"              # Fast, efficient
}
```

### 4.2 Temperature Variation Study

A key innovation is systematic temperature testing:
- **T=0.2**: Near-deterministic, strategic focus
- **T=0.7**: Balanced exploration/exploitation
- **T=1.2**: High creativity, more exploration

This creates 12 LLM variants (4 models × 3 temperatures), allowing us to study:
- Consistency vs. adaptability trade-offs
- Strategic diversity within models
- Temperature's effect on cooperation rates

### 4.3 Comprehensive Strategy Library

Beyond canonical strategies, we implement:

#### Classical Strategies (6)
- Tit-for-Tat (TFT)
- Always Cooperate (ALLC)
- Always Defect (ALLD)
- Random
- Grim Trigger
- Pavlov (Win-Stay-Lose-Shift)

#### Behavioral Strategies (3) - Novel Additions
- **Forgiving Grim Trigger**: Forgives after N mutual defections
- **Detective**: Tests opponents then adapts strategy
- **Soft Grudger**: Graduated punishment with recovery

#### Adaptive Learning Strategies (3) - Novel Additions
- **Q-Learning Agent**: Reinforcement learning with ε-greedy exploration
- **Thompson Sampling**: Bayesian exploration/exploitation
- **Gradient Meta-Learner**: Policy gradient with feature extraction

### 4.4 Shadow Conditions

We test three termination probabilities:
- **10%**: Long shadow (expect ~10 rounds)
- **25%**: Medium shadow (expect ~4 rounds)  
- **75%**: Short shadow (expect ~1.3 rounds)

This allows analysis of:
- Horizon effects on cooperation
- Strategic adaptation to game length
- LLM reasoning about termination probability

---

## 5. Key Methodological Enhancements

### 5.1 Real-time Progress Monitoring

Unlike batch processing, our system provides:
```python
# Live monitoring with visual progress bars
Current tournament: 35/276 matches (12.7%)
[████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░]

Speed: 0.42 matches/min
ETA for tournament: 9h 32m
```

### 5.2 Incremental Result Saving

Results are saved after each tournament to prevent data loss:
- CSV files with complete move histories
- JSON metadata with configuration
- Reasoning traces for all LLM decisions

### 5.3 Error Handling and Recovery

Robust handling of API limitations:
```python
# Observed issues and solutions:
1. Claude temperature > 1.0 → Defaults to cooperation
2. Gemini rate limits → Defaults to cooperation  
3. API timeouts → Retry with exponential backoff
```

### 5.4 Modular Architecture

Clean separation of concerns:
```
ipd_suite/
├── agents.py       # All strategy implementations
├── tournament.py   # Tournament engine
├── analysis.py     # Fingerprint & rationale analysis
└── utils.py        # Helper functions
```

---

## 6. Technical Architecture

### 6.1 Agent Base Class Design

```python
class Agent(ABC):
    def __init__(self, name: str):
        self.name = name
        self.history = []
        self.opponent_history = []
        self.last_reasoning = None
        
    @abstractmethod
    def make_move(self, own_history: List[str], 
                  opponent_history: List[str]) -> str:
        """Return 'C' or 'D'"""
        pass
```

### 6.2 LLM Agent Implementation

Key features:
- Structured prompting with game rules
- History formatting as tuples
- Reasoning extraction and storage
- Token counting for cost tracking

### 6.3 Tournament Engine

Implements:
- Round-robin matching
- Stochastic termination
- Parallel match execution capability
- Comprehensive data logging

### 6.4 Analysis Pipeline

Strategic fingerprint calculation:
```python
def calculate_strategic_fingerprint(matches, agent_name):
    # Calculate P(C|CC), P(C|CD), P(C|DC), P(C|DD)
    # Following Payne & Alloui-Cros methodology
```

---

## 7. Experimental Parameters

### 7.1 Scale Comparison

| Parameter | Payne & Alloui-Cros | Our Implementation |
|-----------|--------------------|--------------------|
| LLM Providers | 3 | 4 |
| Temperature Settings | Not specified | 3 (0.2, 0.7, 1.2) |
| Total Strategies | ~5-10 (canonical) | 24 (12 classical + 12 LLM) |
| Shadow Conditions | Variable | 3 (10%, 25%, 75%) |
| Matches per Tournament | Not specified | 276 |
| Tournaments per Condition | Not specified | 2 |
| Total Matches | Not specified | 1,656 |

### 7.2 Cost Analysis

Estimated costs per tournament:
- GPT-4o-mini: ~$0.50
- Claude-3-Sonnet: ~$10.00  
- Mistral-Large: ~$15.00
- Gemini-1.5-Flash: ~$0.00 (free tier)

Total estimated cost: <$50 for complete experiment

### 7.3 Time Requirements

Based on current execution:
- Average match duration: ~15-30 seconds (with LLMs)
- Tournament completion: ~2-3 hours
- Full experiment: ~12-18 hours

---

## 8. Data Collection and Analysis Framework

### 8.1 Data Hierarchy

```
results/experiment_YYYYMMDD_HHMMSS/
├── config.json                    # Experiment configuration
├── progress.json                  # Real-time progress tracking
├── tournament_shadow10_run1.csv   # Raw match data
├── tournament_shadow10_run2.csv
├── fingerprints_shadow_10.png     # Strategic fingerprints
├── horizon_awareness.csv          # Rationale analysis
├── performance_heatmap.png        # Cross-condition results
└── analysis_report.txt            # Summary statistics
```

### 8.2 Metrics Collected

#### Performance Metrics
- Average score per move
- Total score per agent
- Survival rates (for future evolutionary implementation)
- Head-to-head win rates

#### Behavioral Metrics  
- Cooperation rate (overall and first-move)
- Strategic fingerprints: P(C|state)
- Defection response patterns
- Forgiveness indices

#### LLM-Specific Metrics
- Reasoning length and complexity
- Horizon awareness (mentions of game ending)
- Opponent modeling sophistication
- Strategy naming/recognition

### 8.3 Analysis Techniques

1. **Strategic Fingerprinting**: Following Payne & Alloui-Cros, calculate P(C|CC), P(C|CD), P(C|DC), P(C|DD)

2. **Temperature Effect Analysis**: Compare behavioral consistency across temperature settings

3. **Rationale Mining**: NLP analysis of reasoning patterns:
   - TF-IDF for common strategic terms
   - Horizon awareness quantification
   - Opponent modeling detection

4. **Evolutionary Dynamics**: Track performance across conditions

---

## 9. Current Status and Preliminary Observations

### 9.1 Execution Status
As of the latest monitoring:
- Progress: 35/276 matches (12.7%) in first tournament
- Shadow condition: 10% termination probability
- Estimated completion: ~12 hours remaining

### 9.2 Observed Issues

1. **Claude Temperature Limitation**: 
   - Claude API rejects temperature > 1.0
   - T=1.2 agents default to cooperation
   - Impact: Reduced variation in Claude strategies

2. **Gemini Rate Limiting**:
   - Free tier: 15 requests/minute
   - Causes cooperative defaults during rate limit
   - Impact: Potential bias toward cooperation

3. **Performance Variation**:
   - LLM matches: 20-60 seconds
   - Classical matches: <0.1 seconds
   - Adaptive strategy matches: ~1 second

### 9.3 Early Patterns

From partial results:
- High API reliability for OpenAI and Mistral
- Anthropic's temperature constraints affect experimental design
- Google's rate limits require careful pacing
- Classical strategies execute extremely quickly

---

## 10. Expected Contributions

### 10.1 Scientific Contributions

1. **Temperature's Role in Strategic Behavior**: First systematic study of how temperature affects LLM decision-making in game theory

2. **Adaptive vs. LLM Performance**: Direct comparison between learning algorithms and pre-trained language models

3. **Forgiveness Mechanisms**: Testing whether calibrated forgiveness (ForgivingGrimTrigger) outperforms pure reciprocity

4. **Model Comparison Update**: Performance analysis of newer model versions since original study

### 10.2 Methodological Contributions

1. **Open-Source Framework**: Complete codebase for reproducing and extending LLM game theory experiments

2. **Real-time Monitoring Tools**: Infrastructure for long-running experiments with live progress tracking

3. **Modular Design**: Easy addition of new strategies, models, or game variants

4. **Cost-Effective Testing**: Demonstration of meaningful research with minimal API costs

### 10.3 Practical Applications

Results will inform:
- Multi-agent AI system design
- LLM deployment in competitive environments
- Cooperation mechanism design
- AI safety through behavioral prediction

### 10.4 Future Research Directions

Our framework enables:
1. **Expanded Model Testing**: GPT-4-turbo, Claude-3-Opus, Llama variants
2. **Alternative Games**: Chicken, Stag Hunt, Public Goods
3. **Network Tournaments**: Spatial/graph-based interactions
4. **Human-AI Tournaments**: Mixed human-LLM populations
5. **Prompt Engineering Studies**: Optimal prompts for cooperation/competition

---

## Conclusion

This implementation significantly extends the pioneering work of Payne & Alloui-Cros (2025) by introducing temperature variation analysis, adaptive learning strategies, and a comprehensive open-source framework. While the original study established that LLMs exhibit distinct strategic personalities, our work investigates the parameters that influence these behaviors and tests them against a broader range of opponents.

The experiment currently running will provide valuable data on:
- How temperature affects strategic consistency
- Whether learning algorithms can outperform LLMs
- The role of forgiveness in evolutionary success
- Updated strategic profiles for newer model versions

By making our framework open and modular, we aim to accelerate research at the intersection of game theory and machine psychology, contributing to our understanding of AI behavior in strategic interactions.

---

## Appendix: Live Monitoring Output

Current experiment status (example):
```
============================================================
IPD EXPERIMENT LIVE MONITOR
============================================================

Experiment: shadow_10
Status: Running
Elapsed: 12m 37s

OVERALL PROGRESS:
Completed: 0/1656 total matches (0.0%)
[░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░]

CURRENT TOURNAMENT:
Progress: 35/276 matches (12.7%)
[██████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░]

TIME ESTIMATES:
Current tournament ETA: 2h 14m
Full experiment ETA: 14h 29m

Speed: 0.18 matches/min
```

This real-time feedback ensures experimental integrity and allows for early detection of issues, demonstrating our commitment to rigorous, transparent research methodology.