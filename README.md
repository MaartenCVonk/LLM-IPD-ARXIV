# Extended LLM-IPD Framework: Temperature Variation and Adaptive Strategies

This repository extends the groundbreaking work by [Payne & Alloui-Cros (2025)](https://arxiv.org/abs/2507.02618) on Large Language Model behavior in the Iterated Prisoner's Dilemma. Our implementation adds significant new features and experimental capabilities.

## 🚀 Key Extensions

### 1. Temperature Variation Analysis
- **Novel contribution**: First systematic study of temperature effects on LLM strategic behavior
- Tests 3 temperature settings (0.2, 0.7, 1.2) across all LLM models
- Discovers API limitations (Claude max temp=1.0, Gemini rate limits)

### 2. Expanded Model Coverage
- **Original**: OpenAI, Google Gemini, Anthropic Claude
- **Our addition**: Mistral Large
- **Total**: 4 LLM providers with 12 variants (4 models × 3 temperatures)

### 3. New Strategy Implementations

#### Behavioral Strategies (New)
- `ForgivingGrimTrigger`: Forgives after N mutual defections
- `Detective`: Tests opponents with C-D-C-C sequence then adapts
- `SoftGrudger`: Graduated punishment with recovery

#### Adaptive Learning Strategies (New)
- `QLearningAgent`: Reinforcement learning with ε-greedy exploration
- `ThompsonSampling`: Bayesian exploration/exploitation
- `GradientMetaLearner`: Policy gradient with feature extraction

### 4. Real-time Monitoring System
- Live progress tracking with visual progress bars
- Incremental result saving (prevents data loss)
- Sophisticated error handling and recovery

## 📊 Experimental Design

| Feature | Original (Payne & Alloui-Cros) | Our Extension |
|---------|-------------------------------|---------------|
| LLM Providers | 3 | 4 |
| Temperature Settings | Not specified | 3 (0.2, 0.7, 1.2) |
| Total Strategies | ~5-10 canonical | 24 (12 classical + 12 LLM) |
| Shadow Conditions | Variable | 3 (10%, 25%, 75%) |
| Progress Monitoring | None mentioned | Real-time with visual display |
| Code Availability | Not public | Fully open-source |

## 🔬 Current Findings

### API Behavior Observations
1. **Claude 3 Sonnet**: Rejects temperature > 1.0 (defaults to cooperation)
2. **Gemini 1.5 Flash**: Free tier limits (15 req/min, 50 req/day)
3. **GPT-4o-mini**: Most reliable and cost-effective
4. **Mistral Large**: Stable but higher cost

### Performance Insights (Preliminary)
- Match duration varies significantly: LLM matches (20-120s) vs classical (<0.1s)
- ForgivingGrimTrigger shows early promise as top performer
- Temperature effects still being analyzed

## 🛠️ Installation & Usage

### Prerequisites
- Python 3.8+
- API keys for LLM providers (OpenAI, Anthropic, Mistral, Google)

### Quick Start
```bash
# Clone the repository
git clone https://github.com/sdspieg/LLM-IPD-ARXIV.git
cd LLM-IPD-ARXIV

# Install dependencies
pip install -r requirements.txt

# Set up API keys
cp Axelrod.env.example Axelrod.env
# Edit Axelrod.env with your API keys

# Run test experiment
python run_experiments.py --test

# Run full experiment
python run_experiments.py --shadow 0.1 0.25 0.75 --temperature 0.2 0.7 1.2

# Monitor progress (in separate terminal)
python live_monitor.py
```

### Project Structure
```
LLM-IPD-ARXIV/
├── ipd_suite/                      # New modular implementation
│   ├── agents.py                   # All strategy implementations
│   ├── tournament.py               # Tournament engine
│   ├── analysis.py                 # Fingerprint & rationale analysis
│   └── utils.py                    # Helper functions
├── run_experiments.py              # Main experiment runner
├── live_monitor.py                 # Real-time progress monitor
├── EXPERIMENTAL_DESIGN_COMPARISON.md  # Detailed methodology (20 pages)
└── results/                        # Experiment results (auto-generated)
```

## 📈 Results & Analysis

Results are saved incrementally in `results/experiment_YYYYMMDD_HHMMSS/`:
- CSV files with complete move histories and LLM reasoning
- Strategic fingerprint visualizations
- Horizon awareness analysis  
- Performance heatmaps
- Comprehensive analysis reports

### Sample Results Dashboard
```
============================================================
IPD EXPERIMENT LIVE MONITOR
============================================================

Experiment: shadow_10
Status: Running
Elapsed: 1h 13m

OVERALL PROGRESS:
Completed: 0/1656 total matches (0.0%)
[░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░]

CURRENT TOURNAMENT:
Progress: 113/276 matches (40.9%)
[████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░]

TIME ESTIMATES:
Current tournament ETA: 1h 47m
Full experiment ETA: 18h 23m

Speed: 0.09 matches/min
```

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

Please read our [Contributing Guidelines](CONTRIBUTING.md) before submitting PRs.

## 📖 Documentation

- [Experimental Design Comparison](EXPERIMENTAL_DESIGN_COMPARISON.md) - Detailed methodology
- [API Setup Guide](API_SETUP_GUIDE.md) - Configuration instructions
- [New Features Summary](NEW_FEATURES_SUMMARY.md) - Technical implementation details
- [Comprehensive Report](COMPREHENSIVE_REPORT.md) - Initial findings and analysis

## 🏆 Acknowledgments

This work builds upon:
- Payne, K. & Alloui-Cros, O. (2025). "Survival of the Fittest Elicitation: Evolutionary Approaches to Iterated Prompting." arXiv:2507.02618
- Original repository: https://github.com/kennethpayne01/LLM-IPD-ARXIV

Special thanks to the authors for their pioneering work in LLM game theory.

## 📝 Citation

If you use this extended framework, please cite both the original work and our extensions:

```bibtex
@article{payne2025survival,
  title={Survival of the Fittest Elicitation: Evolutionary Approaches to Iterated Prompting},
  author={Payne, Kenneth and Alloui-Cros, Olivier},
  journal={arXiv preprint arXiv:2507.02618},
  year={2025}
}

@software{llm_ipd_extended_2025,
  title={Extended LLM-IPD Framework: Temperature Variation and Adaptive Strategies},
  author={De Spiegeleire, Stephan},
  year={2025},
  url={https://github.com/sdspieg/LLM-IPD-ARXIV},
  note={ORCID: 0000-0002-8878-5812}
}
```

## 📊 Status

🔴 **Experiment Running**
- Currently processing tournament 1 of 6
- Progress: 117/276 matches (42.4%)
- Estimated completion: ~18h 13m
- API errors handled gracefully (Claude temp limits, Gemini quotas)
- Results saved incrementally

*Last updated: 2025-07-11 02:56:13 UTC*
---

*This is an active research project. Results and conclusions are preliminary.*

## License

This project maintains the same license as the original work. See [LICENSE](LICENSE) for details.