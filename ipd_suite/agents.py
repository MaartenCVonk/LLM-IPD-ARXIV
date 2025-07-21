"""
Agent implementations for IPD experiments
Including classical strategies, behavioral variants, adaptive learning, and LLM agents
"""

import random
import numpy as np
from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, Dict
import openai
import anthropic
import google.generativeai as genai
from mistralai import Mistral
import time
import json


class Agent(ABC):
    """Base class for all IPD agents"""
    
    def __init__(self, name: str):
        self.name = name
        self.history = []
        self.opponent_history = []
        self.last_reasoning = None
        
    @abstractmethod
    def make_move(self, own_history: List[str], opponent_history: List[str]) -> str:
        """Return 'C' for cooperate or 'D' for defect"""
        pass
    
    def reset(self):
        """Reset agent state for new match"""
        self.history = []
        self.opponent_history = []
        self.last_reasoning = None


# Classical Strategies
class AlwaysCooperate(Agent):
    """Always cooperates"""
    def make_move(self, own_history: List[str], opponent_history: List[str]) -> str:
        return 'C'


class AlwaysDefect(Agent):
    """Always defects"""
    def make_move(self, own_history: List[str], opponent_history: List[str]) -> str:
        return 'D'


class Random(Agent):
    """Randomly cooperates or defects"""
    def __init__(self, name: str, p_cooperate: float = 0.5):
        super().__init__(name)
        self.p_cooperate = p_cooperate
        
    def make_move(self, own_history: List[str], opponent_history: List[str]) -> str:
        return 'C' if random.random() < self.p_cooperate else 'D'


class TitForTat(Agent):
    """Cooperates first, then copies opponent's last move"""
    def make_move(self, own_history: List[str], opponent_history: List[str]) -> str:
        if not opponent_history:
            return 'C'
        return opponent_history[-1]


class GrimTrigger(Agent):
    """Cooperates until opponent defects, then always defects"""
    def __init__(self, name: str):
        super().__init__(name)
        self.triggered = False
        
    def make_move(self, own_history: List[str], opponent_history: List[str]) -> str:
        if 'D' in opponent_history:
            self.triggered = True
        return 'D' if self.triggered else 'C'
    
    def reset(self):
        super().reset()
        self.triggered = False


class WinStayLoseShift(Agent):
    """If last outcome was good (CC or DC), repeat; otherwise switch"""
    def make_move(self, own_history: List[str], opponent_history: List[str]) -> str:
        if not own_history:
            return 'C'
        
        last_own = own_history[-1]
        last_opp = opponent_history[-1]
        
        # Good outcomes: mutual cooperation or exploiting opponent
        if (last_own == 'C' and last_opp == 'C') or (last_own == 'D' and last_opp == 'C'):
            return last_own
        else:
            return 'D' if last_own == 'C' else 'C'


class Pavlov(Agent):
    """Win-Stay-Lose-Shift variant"""
    def make_move(self, own_history: List[str], opponent_history: List[str]) -> str:
        return WinStayLoseShift.make_move(self, own_history, opponent_history)


# Behavioral Strategies
class ForgivingGrimTrigger(Agent):
    """Grim Trigger that forgives after N mutual defections (optimized for shorter games)"""
    def __init__(self, name: str, forgiveness_threshold: int = 2):
        super().__init__(name)
        self.triggered = False
        self.forgiveness_threshold = forgiveness_threshold
        self.mutual_defection_count = 0
        
    def make_move(self, own_history: List[str], opponent_history: List[str]) -> str:
        if not self.triggered and 'D' in opponent_history:
            self.triggered = True
            
        if self.triggered:
            # Count mutual defections from previous round
            if (own_history and opponent_history and 
                own_history[-1] == 'D' and opponent_history[-1] == 'D'):
                self.mutual_defection_count += 1
                
            # Check if we should forgive (before reaching threshold)
            if self.mutual_defection_count >= self.forgiveness_threshold:
                self.triggered = False
                self.mutual_defection_count = 0
                return 'C'
                    
            return 'D'
        return 'C'
    
    def reset(self):
        super().reset()
        self.triggered = False
        self.mutual_defection_count = 0


class Detective(Agent):
    """Tests opponent with C-D-C, then adapts based on response (optimized for shorter games)"""
    def __init__(self, name: str):
        super().__init__(name)
        self.test_sequence = ['C', 'D', 'C']
        self.opponent_type = None  # 'sucker', 'retaliator', 'random'
        
    def make_move(self, own_history: List[str], opponent_history: List[str]) -> str:
        round_num = len(own_history)
        
        # Testing phase
        if round_num < len(self.test_sequence):
            return self.test_sequence[round_num]
        
        # Analyze opponent after testing
        if round_num == len(self.test_sequence):
            self._analyze_opponent(opponent_history)
            
        # Adapt strategy based on opponent type
        if self.opponent_type == 'sucker':
            return 'D'  # Exploit cooperators
        elif self.opponent_type == 'retaliator':
            # TFT against retaliators
            return opponent_history[-1] if opponent_history else 'C'
        else:
            # Mixed strategy against unpredictable opponents
            return 'C' if random.random() < 0.6 else 'D'
    
    def _analyze_opponent(self, opponent_history: List[str]):
        """Classify opponent based on test response (optimized for shorter games)"""
        if len(opponent_history) < 3:
            self.opponent_type = 'random'
            return
            
        # Check if opponent retaliated to our defection (position 1 -> response at position 2)
        retaliated = opponent_history[2] == 'D'
        
        # Check cooperation rate
        coop_rate = opponent_history.count('C') / len(opponent_history)
        
        if not retaliated and coop_rate >= 0.67:  # 2/3 cooperation rate
            self.opponent_type = 'sucker'
        elif retaliated:
            self.opponent_type = 'retaliator'
        else:
            self.opponent_type = 'random'
    
    def reset(self):
        super().reset()
        self.opponent_type = None


class SoftGrudger(Agent):
    """Retaliates with graduated punishment: D-D-C (optimized for shorter games)"""
    def __init__(self, name: str):
        super().__init__(name)
        self.punishment_sequence = ['D', 'D', 'C']
        self.punishment_index = 0
        self.punishing = False
        
    def make_move(self, own_history: List[str], opponent_history: List[str]) -> str:
        # Start punishment if opponent defected and we're not already punishing
        if opponent_history and opponent_history[-1] == 'D' and not self.punishing:
            self.punishing = True
            self.punishment_index = 0
            
        # Execute punishment sequence
        if self.punishing:
            if self.punishment_index < len(self.punishment_sequence):
                move = self.punishment_sequence[self.punishment_index]
                self.punishment_index += 1
                return move
            else:
                # Punishment complete, return to cooperation
                self.punishing = False
                self.punishment_index = 0
                
        return 'C'
    
    def reset(self):
        super().reset()
        self.punishment_index = 0
        self.punishing = False


# Adaptive Learning Strategies
class QLearningAgent(Agent):
    """Q-learning agent with state-action values (default settings optimized for length 4 games)"""
    def __init__(self, name: str, alpha: float = 0.7, gamma: float = 0.5, epsilon: float = 0.3):
        super().__init__(name)
        self.alpha = alpha  # Learning rate
        self.gamma = gamma  # Discount factor
        self.epsilon = epsilon  # Exploration rate
        self.q_table = {}
        self.last_state = None
        self.last_action = None
        
        # Use optimistic initialization to encourage exploration
        # This helps the agent try defection early to learn it's better against cooperators
        self._optimistic_init_value = 10.0
    
    @classmethod
    def for_game_length(cls, name: str, expected_game_length: int):
        """Factory method to create QLearningAgent with optimal parameters for game length"""
        if expected_game_length <= 1:
            # Single-shot games: immediate learning, no future, no exploration
            return cls(name, alpha=1.0, gamma=0.0, epsilon=0.0)
        elif expected_game_length <= 4:
            # Short games: fast learning, short horizon, moderate exploration
            return cls(name, alpha=0.7, gamma=0.5, epsilon=0.3)
        elif expected_game_length <= 10:
            # Moderate games: standard learning, moderate horizon, conservative exploration
            return cls(name, alpha=0.3, gamma=0.7, epsilon=0.2)
        else:
            # Long games: gradual learning, long horizon, minimal exploration
            return cls(name, alpha=0.1, gamma=0.9, epsilon=0.1)
        
    def _get_state(self, own_history: List[str], opponent_history: List[str]) -> Tuple:
        """Define state based on last moves"""
        if not own_history:
            return ('START', 'START')
        return (own_history[-1], opponent_history[-1])
    
    def _get_q_value(self, state: Tuple, action: str) -> float:
        """Get Q-value for state-action pair with optimistic initialization"""
        return self.q_table.get((state, action), self._optimistic_init_value)
    
    def _update_q_value(self, state: Tuple, action: str, reward: float, next_state: Tuple):
        """Update Q-value using Q-learning formula"""
        current_q = self._get_q_value(state, action)
        max_next_q = max(self._get_q_value(next_state, 'C'), 
                        self._get_q_value(next_state, 'D'))
        new_q = current_q + self.alpha * (reward + self.gamma * max_next_q - current_q)
        self.q_table[(state, action)] = new_q
        
    def make_move(self, own_history: List[str], opponent_history: List[str]) -> str:
        state = self._get_state(own_history, opponent_history)
        
        # Update Q-value from last round
        if self.last_state is not None and own_history:
            reward = self._calculate_reward(own_history[-1], opponent_history[-1])
            self._update_q_value(self.last_state, self.last_action, reward, state)
        
        # Epsilon-greedy action selection with adaptive exploration
        # Reduce exploration over time to converge to optimal policy
        current_epsilon = self.epsilon * (0.99 ** len(own_history))
        
        if random.random() < current_epsilon:
            action = random.choice(['C', 'D'])
        else:
            q_c = self._get_q_value(state, 'C')
            q_d = self._get_q_value(state, 'D')
            action = 'C' if q_c > q_d else 'D'  # Changed >= to > for slight bias toward defection
            
        self.last_state = state
        self.last_action = action
        return action
    
    def _calculate_reward(self, own_move: str, opp_move: str) -> float:
        """Calculate reward based on payoff matrix"""
        payoffs = {
            ('C', 'C'): 3,
            ('C', 'D'): 0,
            ('D', 'C'): 5,
            ('D', 'D'): 1
        }
        return payoffs[(own_move, opp_move)]
    
    def reset(self):
        super().reset()
        self.last_state = None
        self.last_action = None


class ThompsonSampling(Agent):
    """Thompson sampling for exploration/exploitation (default settings optimized for length 5 games)"""
    def __init__(self, name: str, base_learning_rate: float = 0.2, learning_rate_scale: float = 1.2):
        super().__init__(name)
        # Beta distribution parameters for each action
        self.alpha_c = 1  # Successes for cooperation
        self.beta_c = 1   # Failures for cooperation
        self.alpha_d = 1  # Successes for defection
        self.beta_d = 1   # Failures for defection
        
        # Learning rate parameters for game length adaptation
        self.base_learning_rate = base_learning_rate
        self.learning_rate_scale = learning_rate_scale
    
    @classmethod
    def for_game_length(cls, name: str, expected_game_length: float):
        """Factory method to create ThompsonSampling agent with optimal parameters for game length"""
        if expected_game_length <= 1.5:
            # Very short games (mean ~1.3): fast learning, high sensitivity
            return cls(name, base_learning_rate=0.3, learning_rate_scale=1.5)
        elif expected_game_length <= 5:
            # Short games (mean ~4): moderate learning, balanced sensitivity
            return cls(name, base_learning_rate=0.2, learning_rate_scale=1.2)
        elif expected_game_length <= 12:
            # Moderate games (mean ~10): standard learning, normal sensitivity
            return cls(name, base_learning_rate=0.1, learning_rate_scale=0.9)
        else:
            # Long games: gradual learning, conservative sensitivity
            return cls(name, base_learning_rate=0.05, learning_rate_scale=0.7)
        
    def make_move(self, own_history: List[str], opponent_history: List[str]) -> str:
        # Sample from beta distributions
        theta_c = np.random.beta(self.alpha_c, self.beta_c)
        theta_d = np.random.beta(self.alpha_d, self.beta_d)
        
        # Choose action with higher sampled value
        return 'C' if theta_c > theta_d else 'D'
    
    def update(self, own_move: str, opponent_move: str, payoff: float):
        """Update beta parameters based on outcome with adaptive learning rate"""
        # Use adaptive learning rate based on payoff magnitude and game length
        # Scale payoff to learning rate: higher payoffs give stronger updates
        # Payoff range: 0-5, so we normalize and scale appropriately
        
        # Calculate adaptive learning rate based on payoff and game length parameters
        # Base learning rate adjusted by payoff magnitude
        learning_rate = self.base_learning_rate + (payoff / 5.0) * self.learning_rate_scale
        
        # All payoffs are treated as "successes" but with different magnitudes
        # This allows the agent to learn that higher payoffs are better
        if own_move == 'C':
            self.alpha_c += learning_rate
            # Small penalty for low payoffs to maintain exploration
            if payoff < 2.5:  # Below average
                penalty = (2.5 - payoff) * self.base_learning_rate
                self.beta_c += penalty
        else:
            self.alpha_d += learning_rate
            # Small penalty for low payoffs
            if payoff < 2.5:  # Below average
                penalty = (2.5 - payoff) * self.base_learning_rate
                self.beta_d += penalty


class GradientMetaLearner(Agent):
    """Policy gradient approach with feature extraction (default settings optimized for length 5 games)"""
    def __init__(self, name: str, learning_rate: float = 0.05):
        super().__init__(name)
        self.learning_rate = learning_rate
        self.weights = np.zeros(5)  # Feature weights
        self.feature_history = []
        self.action_history = []
        self.reward_history = []
        
    def _extract_features(self, own_history: List[str], opponent_history: List[str]) -> np.ndarray:
        """Extract features from game state"""
        features = np.zeros(5)
        
        if not opponent_history:
            features[0] = 1  # First round
            return features
            
        # Feature 1: Opponent cooperation rate
        features[1] = opponent_history.count('C') / len(opponent_history)
        
        # Feature 2: Recent opponent cooperation (last 3 moves)
        recent = opponent_history[-3:]
        features[2] = recent.count('C') / len(recent) if recent else 0
        
        # Feature 3: Mutual cooperation rate
        mutual_coop = sum(1 for i in range(len(own_history)) 
                         if own_history[i] == 'C' and opponent_history[i] == 'C')
        features[3] = mutual_coop / len(own_history) if own_history else 0
        
        # Feature 4: Rounds played (normalized for ~5 round games)
        features[4] = min(len(own_history) / 5, 1.0)
        
        return features
    
    def _policy(self, features: np.ndarray) -> float:
        """Compute probability of cooperation"""
        logit = np.dot(self.weights, features)
        return 1 / (1 + np.exp(-logit))  # Sigmoid
    
    def make_move(self, own_history: List[str], opponent_history: List[str]) -> str:
        features = self._extract_features(own_history, opponent_history)
        p_cooperate = self._policy(features)
        
        # Sample action from policy
        action = 'C' if random.random() < p_cooperate else 'D'
        
        # Store for learning
        self.feature_history.append(features)
        self.action_history.append(1 if action == 'C' else 0)
        
        return action
    
    def update_policy(self):
        """Update weights using policy gradient"""
        if len(self.reward_history) < 2:
            return
            
        # Compute advantages (rewards - baseline)
        rewards = np.array(self.reward_history)
        baseline = np.mean(rewards)
        advantages = rewards - baseline
        
        # Policy gradient update
        for i in range(len(self.feature_history)):
            features = self.feature_history[i]
            action = self.action_history[i]
            advantage = advantages[i] if i < len(advantages) else 0
            
            # Gradient of log probability
            p = self._policy(features)
            grad = features * (action - p)
            
            # Update weights
            self.weights += self.learning_rate * advantage * grad
    
    def reset(self):
        super().reset()
        self.feature_history = []
        self.action_history = []
        self.reward_history = []


# LLM Agents
class LLMAgent(Agent):
    """Base class for LLM agents"""
    
    def __init__(self, name: str, model: str, temperature: float = 0.7, termination_prob: float = 0.1):
        super().__init__(name)
        self.model = model
        self.temperature = temperature
        self.termination_prob = termination_prob
        self.api_calls = 0
        self.total_tokens = 0
        
    def _create_prompt(self, own_history: List[str], opponent_history: List[str]) -> str:
        """Create prompt for LLM"""
        history_pairs = list(zip(own_history, opponent_history))
        history_str = ', '.join([f"({own},{opp})" for own, opp in history_pairs])
        
        prompt = f"""You are playing the Iterated Prisoner's Dilemma game.

Game Rules:
- Two players choose to Cooperate (C) or Defect (D)
- Payoffs: Both C = 3 points each, Both D = 1 point each, You C/They D = 0/5 points, You D/They C = 5/0 points
- The game continues for multiple rounds with {self.termination_prob*100}% chance of ending after each round
- Goal: Maximize your total score

History of moves (You, Opponent): [{history_str}]

Provide your reasoning about the game state, opponent's strategy, and your decision.
End your response with your move on a new line: either 'C' or 'D'."""
        
        return prompt
    
    @abstractmethod
    def _call_api(self, prompt: str) -> str:
        """Call the specific LLM API"""
        pass
    
    def make_move(self, own_history: List[str], opponent_history: List[str]) -> str:
        prompt = self._create_prompt(own_history, opponent_history)
        
        try:
            response = self._call_api(prompt)
            self.last_reasoning = response
            
            # Extract move from response
            lines = response.strip().split('\n')
            last_line = lines[-1].strip().upper()
            
            if last_line in ['C', 'D']:
                return last_line
            elif 'C' in last_line and 'D' not in last_line:
                return 'C'
            elif 'D' in last_line and 'C' not in last_line:
                return 'D'
            else:
                # Default to cooperation if unclear
                return 'C'
                
        except Exception as e:
            print(f"Error in {self.name}: {e}")
            return 'C'  # Default to cooperation on error


class GPT4Agent(LLMAgent):
    """OpenAI GPT-4 agent"""
    
    def __init__(self, name: str, api_key: str, model: str = "gpt-4o-mini", 
                 temperature: float = 0.7, termination_prob: float = 0.1):
        super().__init__(name, model, temperature, termination_prob)
        self.client = openai.OpenAI(api_key=api_key)
        
    def _call_api(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert game theory player."},
                {"role": "user", "content": prompt}
            ],
            temperature=self.temperature,
            max_tokens=500
        )
        
        self.api_calls += 1
        self.total_tokens += response.usage.total_tokens
        
        return response.choices[0].message.content


class ClaudeAgent(LLMAgent):
    """Anthropic Claude agent"""
    
    def __init__(self, name: str, api_key: str, model: str = "claude-3-5-sonnet-20241022",
                 temperature: float = 0.7, termination_prob: float = 0.1):
        super().__init__(name, model, temperature, termination_prob)
        self.client = anthropic.Anthropic(api_key=api_key)
        
    def _call_api(self, prompt: str) -> str:
        response = self.client.messages.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
            max_tokens=500
        )
        
        self.api_calls += 1
        # Estimate tokens (Claude doesn't return usage directly)
        self.total_tokens += len(prompt.split()) * 1.3 + 200
        
        return response.content[0].text


class MistralAgent(LLMAgent):
    """Mistral AI agent"""
    
    def __init__(self, name: str, api_key: str, model: str = "mistral-large-latest",
                 temperature: float = 0.7, termination_prob: float = 0.1):
        super().__init__(name, model, temperature, termination_prob)
        self.client = Mistral(api_key=api_key)
        
    def _call_api(self, prompt: str) -> str:
        response = self.client.chat.complete(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
            max_tokens=500
        )
        
        self.api_calls += 1
        if hasattr(response, 'usage'):
            self.total_tokens += response.usage.total_tokens
        else:
            self.total_tokens += len(prompt.split()) * 1.3 + 200
        
        return response.choices[0].message.content


class GeminiAgent(LLMAgent):
    """Google Gemini agent"""
    
    def __init__(self, name: str, api_key: str, model: str = "gemini-1.5-flash",
                 temperature: float = 0.7, termination_prob: float = 0.1):
        super().__init__(name, model, temperature, termination_prob)
        genai.configure(api_key=api_key)
        self.model_instance = genai.GenerativeModel(model)
        
    def _call_api(self, prompt: str) -> str:
        response = self.model_instance.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=self.temperature,
                max_output_tokens=500
            )
        )
        
        self.api_calls += 1
        # Estimate tokens
        self.total_tokens += len(prompt.split()) * 1.3 + 200
        
        return response.text