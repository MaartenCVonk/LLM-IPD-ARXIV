"""
Utility functions for IPD experiments
"""

import os
from typing import List, Tuple, Dict
from dotenv import load_dotenv
import json
import time
from datetime import datetime


def load_env_vars(env_path: str = None) -> Dict[str, str]:
    """
    Load environment variables from .env file
    Specifically looks for axelrod.env or Axelrod.env
    """
    if env_path is None:
        # Try to find axelrod.env in current or parent directory
        possible_paths = [
            '.env',
            '.env', 
            '../.env',
            '../.env',
            os.path.join(os.path.dirname(__file__), '..', '.env'),
            os.path.join(os.path.dirname(__file__), '..', '.env')
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                env_path = path
                break
    
    if env_path and os.path.exists(env_path):
        load_dotenv(env_path)
        print(f"Loaded environment from: {env_path}")
    else:
        print("Warning: No axelrod.env file found, using system environment variables")
    
    # Extract API keys
    api_keys = {
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY'),
        'GOOGLE_API_KEY': os.getenv('GOOGLE_API_KEY'),
        'MISTRAL_API_KEY': os.getenv('MISTRAL_API_KEY')
    }
    
    # Check which APIs are available
    available_apis = []
    for key, value in api_keys.items():
        if value:
            api_name = key.replace('_API_KEY', '')
            available_apis.append(api_name)
            print(f"✓ {api_name} API key found")
        else:
            print(f"✗ {key} not found")
    
    return api_keys


def format_history(own_history: List[str], opponent_history: List[str]) -> str:
    """Format move history for display"""
    if not own_history:
        return "No moves yet"
    
    pairs = []
    for i, (own, opp) in enumerate(zip(own_history, opponent_history)):
        pairs.append(f"Round {i+1}: You={own}, Opponent={opp}")
    
    return "\n".join(pairs)


def calculate_payoff(move1: str, move2: str) -> Tuple[int, int]:
    """Calculate payoffs for a single round"""
    payoff_matrix = {
        ('C', 'C'): (3, 3),
        ('C', 'D'): (0, 5),
        ('D', 'C'): (5, 0),
        ('D', 'D'): (1, 1)
    }
    return payoff_matrix[(move1, move2)]


def estimate_api_costs(n_agents: Dict[str, int], avg_rounds: int = 20, 
                      n_matches_per_agent: int = 10) -> Dict[str, float]:
    """
    Estimate API costs for running experiments
    
    Args:
        n_agents: Dictionary mapping API type to number of agents
        avg_rounds: Average rounds per match
        n_matches_per_agent: Number of matches each agent plays
    
    Returns:
        Dictionary of estimated costs by API
    """
    # Cost per 1M tokens (input/output)
    api_costs = {
        'GPT4': (0.01, 0.03),      # GPT-4 
        'GPT4_MINI': (0.00015, 0.0006),  # GPT-4o-mini
        'CLAUDE_SONNET': (0.003, 0.015),  # Claude 3 Sonnet
        'CLAUDE_HAIKU': (0.00025, 0.00125),  # Claude 3 Haiku
        'MISTRAL_LARGE': (0.002, 0.006),  # Mistral Large
        'GEMINI_FLASH': (0.000075, 0.0003)  # Gemini 1.5 Flash
    }
    
    # Estimate tokens per call
    avg_prompt_tokens = 300  # Base prompt + history
    avg_completion_tokens = 150  # Response
    tokens_per_round = avg_prompt_tokens + avg_completion_tokens
    
    total_costs = {}
    
    for api_type, n in n_agents.items():
        if api_type.upper() in api_costs:
            input_cost, output_cost = api_costs[api_type.upper()]
            
            total_rounds = n * n_matches_per_agent * avg_rounds
            total_input_tokens = total_rounds * avg_prompt_tokens
            total_output_tokens = total_rounds * avg_completion_tokens
            
            cost = (total_input_tokens * input_cost + 
                   total_output_tokens * output_cost) / 1_000_000
            
            total_costs[api_type] = round(cost, 2)
    
    return total_costs


def create_experiment_config(shadow_conditions: List[float],
                           temperature_settings: Dict[str, List[float]],
                           llm_models: Dict[str, str]) -> Dict:
    """
    Create configuration for experiments
    
    Args:
        shadow_conditions: List of termination probabilities
        temperature_settings: Dict mapping model type to list of temperature values
        llm_models: Dict mapping model type to specific model name
    
    Returns:
        Configuration dictionary
    """
    config = {
        'timestamp': datetime.now().isoformat(),
        'shadow_conditions': shadow_conditions,
        'temperature_settings': temperature_settings,
        'llm_models': llm_models,
        'classical_strategies': [
            'TitForTat', 'AlwaysCooperate', 'AlwaysDefect', 
            'Random', 'GrimTrigger', 'Pavlov'
        ],
        'behavioral_strategies': [
            'ForgivingGrimTrigger', 'Detective', 'SoftGrudger'
        ],
        'adaptive_strategies': [
            'QLearning', 'ThompsonSampling', 'GradientMetaLearner'
        ]
    }
    
    return config


def save_experiment_metadata(config: Dict, filepath: str):
    """Save experiment configuration to JSON file"""
    with open(filepath, 'w') as f:
        json.dump(config, f, indent=2)
    print(f"Experiment configuration saved to: {filepath}")


def create_progress_file(filepath: str = 'experiment_progress.json'):
    """Initialize progress tracking file"""
    progress = {
        'start_time': datetime.now().isoformat(),
        'total_conditions': 0,
        'completed_conditions': 0,
        'current_condition': None,
        'total_matches': 0,
        'completed_matches': 0,
        'estimated_time_remaining': None,
        'errors': []
    }
    
    with open(filepath, 'w') as f:
        json.dump(progress, f, indent=2)
    
    return filepath


def update_progress(filepath: str, updates: Dict):
    """Update progress tracking file"""
    try:
        with open(filepath, 'r') as f:
            progress = json.load(f)
        
        progress.update(updates)
        progress['last_update'] = datetime.now().isoformat()
        
        # Estimate time remaining
        if progress['completed_matches'] > 0 and progress['total_matches'] > 0:
            elapsed = time.time() - datetime.fromisoformat(progress['start_time']).timestamp()
            rate = progress['completed_matches'] / elapsed
            remaining_matches = progress['total_matches'] - progress['completed_matches']
            eta_seconds = remaining_matches / rate if rate > 0 else 0
            progress['estimated_time_remaining'] = f"{int(eta_seconds/60)} minutes"
        
        with open(filepath, 'w') as f:
            json.dump(progress, f, indent=2)
            
    except Exception as e:
        print(f"Error updating progress: {e}")


def validate_api_keys(required_apis: List[str]) -> bool:
    """Validate that required API keys are present"""
    api_keys = load_env_vars()
    
    missing = []
    for api in required_apis:
        key_name = f"{api.upper()}_API_KEY"
        if not api_keys.get(key_name):
            missing.append(api)
    
    if missing:
        print(f"\nERROR: Missing API keys for: {', '.join(missing)}")
        print("Please add these to your axelrod.env file")
        return False
    
    return True


class Timer:
    """Context manager for timing code execution"""
    
    def __init__(self, name: str = "Operation"):
        self.name = name
        self.start = None
        
    def __enter__(self):
        self.start = time.time()
        return self
        
    def __exit__(self, *args):
        elapsed = time.time() - self.start
        print(f"{self.name} took {elapsed:.2f} seconds")
        
    def elapsed(self) -> float:
        if self.start:
            return time.time() - self.start
        return 0.0