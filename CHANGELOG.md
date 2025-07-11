# Changelog

All notable changes and extensions to the original LLM-IPD-ARXIV repository are documented here.

## [Extended] - 2025-07-11

### Added
- **Temperature Variation Study**: Systematic testing of LLM behavior at temperatures 0.2, 0.7, and 1.2
- **Mistral Large Integration**: Added support for Mistral AI's latest model
- **New Behavioral Strategies**:
  - `ForgivingGrimTrigger`: Implements calibrated forgiveness after mutual defections
  - `Detective`: Tests opponents before choosing exploitation or cooperation
  - `SoftGrudger`: Graduated punishment with recovery mechanism
- **Adaptive Learning Strategies**:
  - `QLearningAgent`: Reinforcement learning with state-action values
  - `ThompsonSampling`: Bayesian approach to exploration/exploitation
  - `GradientMetaLearner`: Policy gradient with feature extraction
- **Real-time Monitoring**:
  - `live_monitor.py`: Visual progress tracking with ETA
  - `simple_monitor.py`: Lightweight status checking
  - `quick_status.py`: One-line progress snapshots
- **Modular Architecture**:
  - `ipd_suite/` package with clean separation of concerns
  - Comprehensive error handling for API limitations
  - Incremental result saving to prevent data loss

### Changed
- Restructured codebase into modular `ipd_suite` package
- Enhanced tournament engine with progress bars and better logging
- Improved API error handling (Claude temp limits, Gemini rate limits)
- Extended analysis pipeline with temperature effect tracking

### Discovered
- Claude API limitation: Maximum temperature = 1.0
- Gemini free tier limits: 15 requests/minute, 50 requests/day
- Significant performance variation based on opponent type (LLM matches: 20-120s vs classical: <0.1s)

### Documentation
- Created comprehensive 20-page methodology comparison
- Added detailed API setup guides
- Documented all new features and implementation details
- Created visual progress monitoring system

## [Original] - 2025

### Initial Implementation (Payne & Alloui-Cros)
- Basic IPD tournament framework
- Support for OpenAI, Google Gemini, and Anthropic Claude
- Canonical strategy implementations
- Strategic fingerprint analysis
- Rationale collection from LLMs