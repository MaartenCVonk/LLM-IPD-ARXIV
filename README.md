# LLM Strategic Behavior in Iterated Prisoner's Dilemma

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive framework for analyzing strategic behavior of Large Language Models (LLMs) in the Iterated Prisoner's Dilemma, based on Payne & Alloui-Cros (2025).

## Features

- **Multi-LLM Support**: OpenAI GPT models, Anthropic Claude, Google Gemini, Mistral AI
- **Evolutionary Tournaments**: Population-based selection across multiple phases
- **High Concurrency**: Support for up to 378 concurrent matches for maximum performance
- **Memory Mechanisms**: Anonymous memory and opponent tracking systems
- **Claude Code Integration**: Local Claude Code SDK for faster responses (experimental)
- **Comprehensive Analysis**: Strategic fingerprints, rationale analysis, and visualization

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/LLM-IPD-ARXIV2.git
cd LLM-IPD-ARXIV2

# Set up virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### API Configuration

Create a `.env` file with your API keys:

```env
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
GOOGLE_API_KEY=your_google_key_here
MISTRAL_API_KEY=your_mistral_key_here
```

### Basic Usage

```bash
# Run evolutionary experiment with maximum concurrency
python run_experiments.py --evolutionary --shadow 0.25 --max-concurrent 378 --phases 3

# Run with Claude Code SDK for faster Claude responses (requires setup)
python run_experiments.py --evolutionary --shadow 0.25 --use-claude-code --max-concurrent 378

# Standard tournament mode
python run_experiments.py --shadow 0.1 0.25 0.75 --tournaments 5

# Test mode
python run_experiments.py --test-evolutionary
```

## Experiment Configuration

### LLM Models Used

| Provider | Models | Temperatures |
|----------|--------|--------------|
| **OpenAI** | `gpt-5-mini`, `gpt-5-nano`, `gpt-4.1-mini` | 1.0 (fixed) |
| **Anthropic** | `claude-sonnet-4-20250514` | 0.2, 0.5, 0.8 |
| **Mistral** | `mistral-medium-2508` | 0.2, 0.7, 1.2 |
| **Google** | `gemini-2.0-flash` | 0.2, 0.7, 1.2 |

### Classical Strategies

- **Canonical**: TitForTat, GrimTrigger, WinStayLoseShift, etc.
- **Adaptive**: Q-Learning, Thompson Sampling, Gradient Meta-Learner
- **Behavioral**: ForgivingGrimTrigger, Detective, SoftGrudger

## Performance Optimization

### Maximum Concurrency

The framework supports up to **378 concurrent matches** (total possible pairwise matches for 28 agents):

```bash
# Maximum speed - all matches run simultaneously
python run_experiments.py --evolutionary --max-concurrent 378
```

### Response Time Analysis

Based on testing with representative queries:

| Provider | Response Time | Processing Speed | Status |
|----------|---------------|------------------|---------|
| **Gemini** | 2-3 seconds | 83 tokens/sec | ✅ Fast |
| **Claude (API)** | 2-3 seconds | ~80 tokens/sec | ✅ Fast |
| **Mistral** | 2-4 seconds | ~70 tokens/sec | ✅ Fast |
| **OpenAI** | 24+ seconds | 67 tokens/sec | ⚠️ Slow |

**Note**: OpenAI models currently show significantly slower response times and may be the bottleneck in mixed experiments.

## Claude Code Integration

### Overview

The framework includes experimental support for the Claude Code SDK, which provides:
- **Local connection** to your Claude Code instance
- **No API costs** for Claude agents
- **Potentially faster responses** than external API calls
- **No rate limits**

### Setup Requirements

1. **Claude Code CLI Installation**:
   ```bash
   npm install -g @anthropic-ai/claude-code
   ```

2. **Verify Installation**:
   ```bash
   claude --version
   # Should output: 1.0.115 (Claude Code)
   ```

3. **Usage**:
   ```bash
   python run_experiments.py --use-claude-code --evolutionary
   ```

### Current Status

| Component | Status | Notes |
|-----------|--------|-------|
| **SDK Installation** | ✅ Complete | `pip install claude-code-sdk` |
| **Agent Creation** | ✅ Working | `ClaudeCodeAgent` class implemented |
| **Argument Parsing** | ✅ Working | `--use-claude-code` flag available |
| **Error Handling** | ✅ Robust | Clear error messages and fallbacks |
| **API Calls** | ⚠️ Issues | Connection timeouts in WSL environment |

### Known Issues

#### Connection Timeout in WSL
```
Fatal error in message reader: Command failed with exit code 1
```

**Cause**: The Claude Code SDK appears to have connectivity issues when running in WSL (Windows Subsystem for Linux) environments.

**Current Workarounds**:
1. **Use regular Anthropic API** (omit `--use-claude-code` flag)
2. **Run experiments from Windows PowerShell** instead of WSL
3. **Debug Claude Code CLI connectivity**:
   ```bash
   # Test if Claude Code CLI responds
   claude --version

   # Try reinstalling
   npm uninstall -g @anthropic-ai/claude-code
   npm install -g @anthropic-ai/claude-code
   ```

#### Implementation Details

The Claude Code integration was implemented with:

- **Deferred Import**: SDK import happens on first API call to avoid blocking initialization
- **Graceful Fallback**: Clear error messages when Claude Code is unavailable
- **Async Handling**: Proper async/sync bridge for existing codebase
- **Agent Compatibility**: Seamless integration with existing agent recreation logic

**Development Log**:
1. ✅ Researched Claude Code SDK capabilities
2. ✅ Implemented `ClaudeCodeAgent` class with async support
3. ✅ Added `--use-claude-code` command line argument
4. ✅ Updated agent creation logic to handle both API and non-API agents
5. ✅ Implemented error handling and availability testing
6. ✅ Fixed agent recreation in evolutionary phases
7. ⚠️ Encountered WSL connectivity issues during testing

## Command Line Reference

### Basic Arguments

```bash
python run_experiments.py [OPTIONS]

Options:
  --shadow FLOAT [FLOAT ...]     Termination probabilities (default: 0.1 0.25 0.75)
  --evolutionary                 Use evolutionary mode
  --phases INT                   Number of evolutionary phases (default: 5)
  --tournaments INT              Number of tournaments per condition (default: 5)
  --max-concurrent INT           Maximum concurrent matches (default: 50, max: 378)
  --use-claude-code             Use Claude Code SDK for Claude agents
  --yes, -y                     Auto-confirm all prompts
  --resume EXPERIMENT_DIR       Resume from checkpoint
  --enable-opponent-tracking    Enable cross-phase opponent memory
```

### Example Commands

```bash
# Quick test with high concurrency
python run_experiments.py --evolutionary --shadow 0.25 --phases 1 --max-concurrent 200

# Full experiment with Claude Code
python run_experiments.py --use-claude-code --evolutionary --phases 5 --max-concurrent 378

# Resume interrupted experiment
python run_experiments.py --resume results/experiment_20250916_171728

# Standard tournament with specific conditions
python run_experiments.py --shadow 0.1 0.5 0.9 --tournaments 3
```

## Results and Analysis

### Output Structure

```
results/experiment_YYYYMMDD_HHMMSS/
├── config.json                              # Experiment configuration
├── evolutionary_shadowXX_phaseN.csv         # Phase results
├── strategic_footprints/                    # Strategic analysis data
│   ├── strategic_footprint_data_*.csv
│   └── extended_strategic_footprint_data_*.csv
├── progress.json                             # Experiment progress
└── checkpoint_shadowXX_phaseN.json          # Resume checkpoints
```

### Analysis Tools

```bash
# Generate comprehensive analysis
python -c "from ipd_suite.analysis import generate_comprehensive_report; generate_comprehensive_report('results/experiment_dir')"

# Create visualizations
python analysis_scripts/population_evolution_plots.py
python analysis_scripts/strategic_footprint_visualizer.py
```

## Development

### Testing

```bash
# Test individual LLM providers
python test_openAI_standalone.py
python test_gemini_standalone.py
python test_mistral_standalone.py

# Test Claude Code integration
python test_claude_code_integration.py

# Test match history functionality
python test_match_history.py
```

### Architecture

- **`ipd_suite/agents.py`**: Agent implementations (classical, adaptive, LLM)
- **`ipd_suite/tournament.py`**: Tournament engine with async support
- **`ipd_suite/analysis.py`**: Strategic analysis and fingerprinting
- **`run_experiments.py`**: Main experiment runner
- **`analysis_scripts/`**: Visualization and reporting tools

## Citation

If you use this framework in your research, please cite:

```bibtex
@article{payne2025strategic,
  title={Strategic Behavior of Large Language Models in the Iterated Prisoner's Dilemma},
  author={Payne, [First Name] and Alloui-Cros, [First Name]},
  journal={[Journal Name]},
  year={2025}
}
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Troubleshooting

### Common Issues

1. **API Key Errors**: Ensure all required API keys are set in `.env`
2. **Memory Issues**: Reduce `--max-concurrent` value if encountering memory problems
3. **Timeout Errors**: Some LLM providers may be slower; adjust timeout values in code
4. **Claude Code Issues**: Use regular Anthropic API if Claude Code SDK has connectivity problems

### Performance Tips

1. **Use maximum concurrency**: `--max-concurrent 378` for fastest execution
2. **Skip slow providers**: Configure temperature settings to exclude problematic APIs
3. **Use SSD storage**: Large result files benefit from fast disk I/O
4. **Monitor memory usage**: Each concurrent match uses memory; adjust accordingly

### Getting Help

- **Issues**: Open an issue on GitHub
- **Discussions**: Use GitHub Discussions for questions
- **Documentation**: Check the code comments for detailed implementation notes

---

**Note**: This implementation prioritizes research reproducibility and performance optimization for large-scale LLM strategic behavior analysis.