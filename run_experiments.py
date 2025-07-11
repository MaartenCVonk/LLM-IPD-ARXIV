#!/usr/bin/env python3
"""
Main experiment runner for IPD research
Implements all experiments from Payne & Alloui-Cros (2025) plus extensions
"""

import os
import sys
import argparse
from datetime import datetime
from typing import List, Dict
import json

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ipd_suite import (
    # Classical strategies
    TitForTat, AlwaysCooperate, AlwaysDefect, Random,
    GrimTrigger, Pavlov,
    
    # Behavioral strategies  
    ForgivingGrimTrigger, Detective, SoftGrudger,
    
    # Adaptive strategies
    QLearningAgent, ThompsonSampling, GradientMetaLearner,
    
    # LLM agents
    GPT4Agent, ClaudeAgent, MistralAgent, GeminiAgent,
    
    # Tournament and analysis
    Tournament, LLMShowdown,
    generate_comprehensive_report
)

from ipd_suite.utils import (
    load_env_vars, validate_api_keys, create_experiment_config,
    save_experiment_metadata, estimate_api_costs, Timer,
    create_progress_file, update_progress
)


def create_agents(api_keys: Dict[str, str], 
                 temperature_settings: List[float],
                 termination_prob: float,
                 include_classical: bool = True) -> List:
    """Create all agent instances for experiments"""
    agents = []
    
    # Classical strategies (always include some for baseline)
    if include_classical:
        agents.extend([
            TitForTat("TitForTat"),
            AlwaysCooperate("AlwaysCooperate"),
            AlwaysDefect("AlwaysDefect"),
            Random("Random"),
            GrimTrigger("GrimTrigger"),
            Pavlov("Pavlov"),
            ForgivingGrimTrigger("ForgivingGrimTrigger"),
            Detective("Detective"),
            SoftGrudger("SoftGrudger"),
            QLearningAgent("QLearning"),
            ThompsonSampling("ThompsonSampling"),
            GradientMetaLearner("GradientMetaLearner")
        ])
    
    # LLM agents with temperature variations
    for temp in temperature_settings:
        temp_suffix = f"_T{str(temp).replace('.', '')}"
        
        # GPT-4 agents
        if api_keys.get('OPENAI_API_KEY'):
            agents.append(
                GPT4Agent(f"GPT4{temp_suffix}", 
                         api_keys['OPENAI_API_KEY'],
                         model="gpt-4o-mini",
                         temperature=temp,
                         termination_prob=termination_prob)
            )
        
        # Claude agents
        if api_keys.get('ANTHROPIC_API_KEY'):
            agents.append(
                ClaudeAgent(f"Claude3Sonnet{temp_suffix}",
                           api_keys['ANTHROPIC_API_KEY'],
                           model="claude-3-sonnet-20240229",
                           temperature=temp,
                           termination_prob=termination_prob)
            )
        
        # Mistral agents
        if api_keys.get('MISTRAL_API_KEY'):
            agents.append(
                MistralAgent(f"MistralLarge{temp_suffix}",
                            api_keys['MISTRAL_API_KEY'],
                            model="mistral-large-latest",
                            temperature=temp,
                            termination_prob=termination_prob)
            )
        
        # Gemini agents
        if api_keys.get('GOOGLE_API_KEY'):
            agents.append(
                GeminiAgent(f"Gemini25Flash{temp_suffix}",
                           api_keys['GOOGLE_API_KEY'],
                           model="gemini-1.5-flash",
                           temperature=temp,
                           termination_prob=termination_prob)
            )
    
    print(f"Created {len(agents)} agents")
    return agents


def run_main_experiments(shadow_conditions: List[float] = [0.1, 0.25, 0.75],
                        temperature_settings: List[float] = [0.2, 0.7, 1.2],
                        n_tournaments: int = 5,
                        output_dir: str = "results"):
    """Run the main experimental suite"""
    print("="*60)
    print("IPD EXPERIMENT RUNNER")
    print("Based on Payne & Alloui-Cros (2025)")
    print("="*60)
    
    # Load API keys
    api_keys = load_env_vars()
    
    # Check which APIs are available
    available_apis = [k.replace('_API_KEY', '') for k, v in api_keys.items() if v]
    if not available_apis:
        print("ERROR: No API keys found! Please set up axelrod.env")
        return
    
    print(f"\nAvailable APIs: {', '.join(available_apis)}")
    
    # Estimate costs
    n_llm_agents = len(available_apis) * len(temperature_settings)
    n_total_agents = n_llm_agents + 12  # 12 classical/behavioral/adaptive
    n_matches = n_total_agents * (n_total_agents - 1) // 2
    
    print(f"\nExperiment scale:")
    print(f"- Shadow conditions: {shadow_conditions}")
    print(f"- Temperature settings: {temperature_settings}")
    print(f"- Total agents: {n_total_agents}")
    print(f"- Matches per tournament: {n_matches}")
    print(f"- Tournaments per condition: {n_tournaments}")
    
    # Cost estimation
    avg_rounds = 1 / shadow_conditions[0]  # Expected rounds for first condition
    api_counts = {api: len(temperature_settings) for api in available_apis}
    costs = estimate_api_costs(api_counts, int(avg_rounds), n_matches)
    
    total_cost = sum(costs.values()) * len(shadow_conditions) * n_tournaments
    print(f"\nEstimated total cost: ${total_cost:.2f}")
    
    # Auto-confirm for non-interactive mode or if AUTO_CONFIRM is set
    import sys
    if not sys.stdin.isatty() or os.environ.get('AUTO_CONFIRM') == 'yes':
        print("\nAuto-confirming experiment start")
    else:
        response = input("\nProceed with experiments? (y/n): ")
        if response.lower() != 'y':
            print("Experiments cancelled.")
            return
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    experiment_dir = os.path.join(output_dir, f"experiment_{timestamp}")
    os.makedirs(experiment_dir, exist_ok=True)
    
    # Save experiment configuration
    config = create_experiment_config(shadow_conditions, temperature_settings, 
                                     {api: "default" for api in available_apis})
    save_experiment_metadata(config, os.path.join(experiment_dir, "config.json"))
    
    # Create progress file
    progress_file = create_progress_file(os.path.join(experiment_dir, "progress.json"))
    update_progress(progress_file, {
        'total_conditions': len(shadow_conditions),
        'total_matches': n_matches * len(shadow_conditions) * n_tournaments
    })
    
    # Run experiments for each shadow condition
    all_results = {}
    
    for i, shadow in enumerate(shadow_conditions):
        print(f"\n{'='*60}")
        print(f"SHADOW CONDITION: {shadow*100}% termination probability")
        print(f"{'='*60}")
        
        update_progress(progress_file, {
            'current_condition': f"shadow_{int(shadow*100)}",
            'completed_conditions': i
        })
        
        # Create agents for this condition
        agents = create_agents(api_keys, temperature_settings, shadow, 
                             include_classical=True)
        
        # Run tournaments
        tournament = Tournament(agents, termination_prob=shadow, verbose=True)
        
        with Timer(f"Shadow {shadow*100}% tournaments"):
            results = []
            for t in range(n_tournaments):
                print(f"\nTournament {t+1}/{n_tournaments}")
                result = tournament.run_tournament()
                
                # Save individual tournament results
                result.save_to_csv(
                    os.path.join(experiment_dir, 
                               f"tournament_shadow{int(shadow*100)}_run{t+1}.csv")
                )
                results.append(result)
                
                # Update progress
                completed_matches = (i * n_tournaments + t + 1) * n_matches
                update_progress(progress_file, {
                    'completed_matches': completed_matches
                })
                
                # Print intermediate results
                print("\nTop 5 performers:")
                summary = result.get_summary_stats()
                for idx, row in summary.head().iterrows():
                    print(f"{idx+1}. {row['agent']}: {row['avg_score_per_move']:.3f}")
        
        all_results[f"shadow_{int(shadow*100)}"] = results
    
    # Run LLM Showdown
    print(f"\n{'='*60}")
    print("LLM SHOWDOWN")
    print(f"{'='*60}")
    
    llm_agents = [a for a in agents if any(x in a.name for x in ['GPT', 'Claude', 'Mistral', 'Gemini'])]
    
    if len(llm_agents) >= 2:
        showdown = LLMShowdown(llm_agents, shadow_conditions, 
                              rounds_per_condition=3, verbose=True)
        showdown_results = showdown.run()
        
        # Merge showdown results
        for condition, results in showdown_results.items():
            if condition in all_results:
                all_results[condition].extend(results)
            else:
                all_results[condition] = results
    
    # Generate comprehensive report
    print(f"\n{'='*60}")
    print("GENERATING ANALYSIS REPORT")
    print(f"{'='*60}")
    
    with Timer("Analysis generation"):
        summary_df = generate_comprehensive_report(all_results, experiment_dir)
    
    # Print final summary
    print("\n" + "="*60)
    print("EXPERIMENT COMPLETE")
    print("="*60)
    print(f"\nResults saved to: {experiment_dir}")
    print("\nOverall Performance Rankings:")
    
    overall_avg = summary_df.groupby('agent')['avg_score'].mean().sort_values(ascending=False)
    for i, (agent, score) in enumerate(overall_avg.head(10).items(), 1):
        print(f"{i}. {agent}: {score:.3f} points/move")
    
    # Calculate total API usage
    total_api_calls = 0
    total_tokens = 0
    for agent in agents:
        if hasattr(agent, 'api_calls'):
            total_api_calls += agent.api_calls
            total_tokens += agent.total_tokens
    
    print(f"\nAPI Usage:")
    print(f"- Total API calls: {total_api_calls}")
    print(f"- Total tokens: {total_tokens:,}")
    
    update_progress(progress_file, {
        'completed_conditions': len(shadow_conditions),
        'completed_matches': n_matches * len(shadow_conditions) * n_tournaments,
        'status': 'complete'
    })


def run_test_experiment():
    """Run a small test experiment to verify setup"""
    print("Running test experiment...")
    
    api_keys = load_env_vars()
    
    # Create minimal agent set
    agents = [
        TitForTat("TitForTat"),
        Random("Random"),
        ForgivingGrimTrigger("ForgivingGrimTrigger")
    ]
    
    # Add one LLM agent if available
    if api_keys.get('OPENAI_API_KEY'):
        agents.append(
            GPT4Agent("GPT4_Test", api_keys['OPENAI_API_KEY'],
                     temperature=0.7, termination_prob=0.5)
        )
    
    # Run small tournament
    tournament = Tournament(agents, termination_prob=0.5, max_rounds=10)
    result = tournament.run_tournament()
    
    # Print results
    print("\nTest Results:")
    summary = result.get_summary_stats()
    print(summary)
    
    print("\nTest complete! Setup verified.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run IPD experiments")
    parser.add_argument("--test", action="store_true", 
                       help="Run test experiment to verify setup")
    parser.add_argument("--shadow", type=float, nargs="+", 
                       default=[0.1, 0.25, 0.75],
                       help="Shadow conditions (termination probabilities)")
    parser.add_argument("--temperature", type=float, nargs="+",
                       default=[0.2, 0.7, 1.2],
                       help="Temperature settings for LLMs")
    parser.add_argument("--tournaments", type=int, default=5,
                       help="Number of tournaments per condition")
    parser.add_argument("--output", type=str, default="results",
                       help="Output directory for results")
    
    args = parser.parse_args()
    
    if args.test:
        run_test_experiment()
    else:
        run_main_experiments(
            shadow_conditions=args.shadow,
            temperature_settings=args.temperature,
            n_tournaments=args.tournaments,
            output_dir=args.output
        )