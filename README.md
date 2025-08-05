# Extended LLM-IPD Framework: Temperature Variation and Adaptive Strategies

This repository extends the groundbreaking work by [Payne & Alloui-Cros (2025)](https://arxiv.org/abs/2507.02618) on Large Language Model behavior in the Iterated Prisoner's Dilemma. Our implementation adds significant new features and experimental capabilities.

## 🚀 Key Extensions

### 1. Temperature Variation Analysis
- **Novel contribution**: First systematic study of temperature effects on LLM strategic behavior
- Tests model-specific temperature settings optimized for each API:
  - **OpenAI/Gemini**: [0.2, 0.7, 1.2] (0-2 range supported)
  - **Anthropic Claude**: [0.2, 0.5, 0.8] (0-1 range constraint)
  - **Mistral**: [0.2, 0.7, 1.0] (0-1 range supported)
- Discovers and adapts to API limitations (Claude max temp=1.0, Gemini rate limits)

### 2. Expanded Model Coverage
- **Original**: OpenAI, Google Gemini, Anthropic Claude
- **Our addition**: Mistral Large
- **Total**: 4 LLM providers with 12 variants (4 models × 3 temperatures)

### 3. New Strategy Implementations

#### Behavioral Strategies (New)
- `ForgivingGrimTrigger`: Triggers on first opponent defection, then defects until N mutual defections occur (default N=2, optimized for shorter games):
  - **Triggered**: Once opponent defects, permanently switch to defection
  - **Mutual Defection Counter**: Track consecutive rounds where both players defect
  - **Forgiveness**: After N mutual defections (2 default), reset to cooperation and clear trigger
  - **Return to Cooperation**: Resets both trigger state and mutual defection count
- `Detective`: Tests opponents with C-D-C sequence (shortened for shorter games), then classifies based on round 3 response and cooperation rate:
  - **Sucker**: Doesn't defect in round 3 AND ≥67% cooperation → Exploit with always defect
  - **Retaliator**: Defects in round 3 (retaliates to Detective's round 2 defection) → Play Tit-for-Tat  
  - **Random**: All other cases → Mixed strategy (60% cooperate)
- `SoftGrudger`: Graduated punishment sequence with automatic recovery (D-D-C pattern, optimized for shorter games):
  - **Punishment Trigger**: Activates on any opponent defection during cooperation
  - **Punishment Sequence**: Fixed 3-move pattern: D-D-C (2 defections, then 1 cooperation)
  - **Sequence Execution**: Plays through entire sequence once triggered, regardless of opponent response
  - **Automatic Recovery**: Returns to cooperation after completing punishment sequence

#### Adaptive Learning Strategies (New)
- `QLearningAgent`: Reinforcement learning with ε-greedy exploration and temporal difference learning (default optimized for length 4 games):
  - **State Representation**: Uses last moves tuple (own_move, opponent_move) plus START state
  - **Q-Table Learning**: Maintains Q(state, action) values updated via Q-learning formula
  - **Action Selection**: ε-greedy policy with adaptive exploration decay (ε × 0.99^t)
  - **Optimistic Initialization**: Q-values start at 10.0 to encourage exploration of all actions
  - **Temporal Difference**: Updates Q-values using Q(s,a) ← Q(s,a) + α[r + γ max Q(s',a') - Q(s,a)]
  - **Payoff Matrix**: Uses standard IPD rewards (CC=3, CD=0, DC=5, DD=1)
  - **Default Parameters**: α=0.7, γ=0.5, ε=0.3 (optimized for ~4 round games)
  - **Game Length Optimization**: Factory method `for_game_length()` provides optimal parameters:
    - **Length 1**: α=1.0, γ=0.0, ε=0.0 (immediate learning, no future, no exploration)
    - **Length ≤5**: α=0.7, γ=0.5, ε=0.3 (fast learning, short horizon, moderate exploration) ← **Default**
    - **Length ≤10**: α=0.3, γ=0.7, ε=0.2 (standard learning, moderate horizon, conservative exploration)

- `ThompsonSampling`: Bayesian multi-armed bandit with Beta distributions for exploration/exploitation (default optimized for length 5 games):
  - **Beta Parameters**: Maintains separate α,β parameters for cooperation and defection actions
  - **Sampling Strategy**: Draws θ_C ~ Beta(α_C, β_C) and θ_D ~ Beta(α_D, β_D), selects action with higher sample
  - **Adaptive Learning Rate**: Learning rate = base_lr + (payoff/5.0) × lr_scale, scaling with payoff magnitude
  - **Default Parameters**: base_lr=0.2, lr_scale=1.2 (optimized for ~5 round games)
  - **Game Length Optimization**: Factory method `for_game_length()` provides optimal parameters:
    - **Length ≤1.5**: base_lr=0.3, lr_scale=1.5 (fast learning, high sensitivity)
    - **Length ≤5**: base_lr=0.2, lr_scale=1.2 (moderate learning, balanced sensitivity) ← **Default**
    - **Length ≤12**: base_lr=0.1, lr_scale=0.9 (standard learning, normal sensitivity)
    - **Length >12**: base_lr=0.05, lr_scale=0.7 (gradual learning, conservative sensitivity)
  - **Parameter Updates**: α += learning_rate, β += penalty for below-average payoffs
  - **Bayesian Learning**: Naturally balances exploration/exploitation through posterior uncertainty

- `GradientMetaLearner`: Policy gradient with strategic feature extraction and stochastic policy (default optimized for length 5 games):
  - **Feature Engineering**: Extracts 5 features: first_round, opponent_coop_rate, recent_coop_rate, mutual_coop_rate, rounds_played
  - **Policy Network**: Uses sigmoid policy π(C|s) = σ(w^T φ(s)) for cooperation probability
  - **Stochastic Actions**: Samples actions from policy distribution (not deterministic)
  - **Policy Gradient**: Updates weights using ∇w = α × advantage × ∇log π(a|s)
  - **Advantage Estimation**: Uses reward minus baseline (mean reward) for variance reduction
  - **Default Parameters**: learning_rate=0.05, rounds_normalization=5 (optimized for ~5 round games)
  - **Game Length Adaptation**: Higher learning rate (5x faster than original) and feature normalization optimized for shorter games

### 4. Real-time Monitoring System
- Live progress tracking with visual progress bars
- Incremental result saving (prevents data loss)
- Sophisticated error handling and recovery

## 📊 Experimental Design

| Feature | Original (Payne & Alloui-Cros) | Our Extension |
|---------|-------------------------------|---------------|
| LLM Providers | 3 | 4 |
| Temperature Settings | Not specified | Model-specific: OpenAI/Gemini [0.2, 0.7, 1.2], Claude [0.2, 0.5, 0.8], Mistral [0.2, 0.7, 1.0] |
| Total Strategies | ~5-10 canonical | 24 (12 classical + 12 LLM) |
| Shadow Conditions | Variable | 3 (10%, 25%, 75%) |
| Progress Monitoring | None mentioned | Real-time with visual display |
| Code Availability | Not public | Fully open-source |

## 🔬 Current Findings

### API Behavior Observations
1. **Claude 3 Sonnet**: Rejects temperature > 1.0, hence custom range [0.2, 0.5, 0.8]
2. **Gemini 1.5 Flash**: Free tier limits (15 req/min, 50 req/day), supports 0-2 temperature range
3. **GPT-4o-mini**: Most reliable and cost-effective, supports 0-2 temperature range
4. **Mistral Large**: Stable but higher cost, supports 0-1 temperature range (capped at 1.0)

### Performance Insights (Preliminary)
- Match duration varies significantly: LLM matches (20-120s) vs classical (<0.1s)
- ForgivingGrimTrigger shows early promise as top performer
- Temperature effects still being analyzed

## 🌡️ Temperature Configuration

Our framework supports model-specific temperature settings to respect API constraints:

### Temperature Ranges by Model
- **OpenAI GPT-4**: 0.0-2.0 (default: [0.2, 0.7, 1.2])
- **Anthropic Claude**: 0.0-1.0 (default: [0.2, 0.5, 0.8]) - **Limited range**
- **Mistral Large**: 0.0-1.0 (default: [0.2, 0.7, 1.0]) - **Capped at 1.0**
- **Google Gemini**: 0.0-2.0 (default: [0.2, 0.7, 1.2])

### Why Different Ranges?
Each LLM provider has different temperature parameter constraints:
- **Anthropic Claude** strictly enforces 0-1 range, rejecting higher values
- **Mistral** supports 0-1 range in their API documentation
- **OpenAI & Gemini** support the full 0-2 range for maximum creativity

This ensures experiments run reliably across all providers while maintaining comparable temperature effects.

## 🛠️ Installation & Usage

### Quick Start
```bash
# Install dependencies
pip install -r requirements.txt

# Set up API keys in Axelrod.env
cp Axelrod.env.example Axelrod.env
# Edit with your API keys

# Run test experiment
python run_experiments.py --test

# Run full experiment with default model-specific temperatures
python run_experiments.py --shadow 0.1 0.25 0.75

# Run with custom temperature settings
python run_experiments.py --shadow 0.1 0.25 0.75 --temperature '{"openai": [0.3, 0.8], "anthropic": [0.1, 0.6], "mistral": [0.4, 0.9], "gemini": [0.2, 1.0]}'

# Monitor progress (in separate terminal)
python live_monitor.py
```

### Project Structure
```
LLM-IPD-ARXIV/
├── ipd_suite/              # New modular implementation
│   ├── agents.py           # All strategy implementations
│   ├── tournament.py       # Tournament engine
│   ├── analysis.py         # Fingerprint & rationale analysis
│   └── utils.py            # Helper functions
├── run_experiments.py      # Main experiment runner
├── live_monitor.py         # Real-time progress monitor
├── evolutionary_PD_expanded.py  # Original code (modified)
└── EXPERIMENTAL_DESIGN_COMPARISON.md  # Detailed methodology
```

## 📈 Results & Analysis

Results are saved incrementally in `results/experiment_YYYYMMDD_HHMMSS/`:
- CSV files with complete move histories
- Strategic fingerprint visualizations
- Horizon awareness analysis
- Performance heatmaps
- Comprehensive analysis reports

## 🔍 Key Research Questions

Our extensions address:
1. **How does temperature affect LLM strategic consistency?**
2. **Can adaptive learning strategies outperform pre-trained LLMs?**
3. **What role does calibrated forgiveness play in evolutionary success?**
4. **How do newer models compare to those in the original study?**

## 🤝 Contributing

We welcome contributions! Areas of interest:
- Additional LLM providers (Llama, Cohere, etc.)
- New adaptive strategies
- Alternative game implementations
- Performance optimizations
- Analysis tools

## 📖 Documentation

- [Experimental Design Comparison](EXPERIMENTAL_DESIGN_COMPARISON.md) - 20-page detailed methodology
- [API Setup Guide](API_SETUP_GUIDE.md) - Configuration instructions
- [New Features Summary](NEW_FEATURES_SUMMARY.md) - Technical implementation details
- [Comprehensive Report](COMPREHENSIVE_REPORT.md) - Initial findings and analysis

## 🏆 Acknowledgments

This work builds upon:
- Payne, K. & Alloui-Cros, O. (2025). "Survival of the Fittest Elicitation: Evolutionary Approaches to Iterated Prompting in Large Language Models." arXiv:2507.02618
- Original repository: https://github.com/kennethpayne01/LLM-IPD-ARXIV

## 📝 Citation

If you use this extended framework, please cite both the original work and our extensions:

```bibtex
@article{payne2025survival,
  title={Survival of the Fittest Elicitation: Evolutionary Approaches to Iterated Prompting in Large Language Models},
  author={Payne, Kenneth and Alloui-Cros, Olivier},
  journal={arXiv preprint arXiv:2507.02618},
  year={2025}
}

@software{llm_ipd_extended,
  title={Extended LLM-IPD Framework: Temperature Variation and Adaptive Strategies},
  author={[Your Name]},
  year={2025},
  url={https://github.com/[YourUsername]/LLM-IPD-ARXIV}
}
```

## 📊 Status

🔴 **Experiment Running**: Currently processing first tournament (65/276 matches)
- Estimated completion: ~12 hours
- API errors handled gracefully (Claude temp limits, Gemini quotas)
- Results saved incrementally

---

*This is an active research project. Results and conclusions are preliminary.*