"""
Tournament engine for running IPD experiments
Handles match execution, data collection, and result aggregation
"""

import random
import time
import csv
import json
import asyncio
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
from collections import defaultdict
import pandas as pd
from tqdm import tqdm
import os
from datetime import datetime

from .agents import Agent, ThompsonSampling, GradientMetaLearner


@dataclass
class MatchResult:
    """Result of a single match between two agents"""
    agent1_name: str
    agent2_name: str
    agent1_moves: List[str]
    agent2_moves: List[str]
    agent1_score: int
    agent2_score: int
    rounds_played: int
    agent1_reasoning: List[Optional[str]] = field(default_factory=list)
    agent2_reasoning: List[Optional[str]] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            'agent1': self.agent1_name,
            'agent2': self.agent2_name,
            'moves': list(zip(self.agent1_moves, self.agent2_moves)),
            'scores': (self.agent1_score, self.agent2_score),
            'rounds': self.rounds_played,
            'reasoning': {
                self.agent1_name: self.agent1_reasoning,
                self.agent2_name: self.agent2_reasoning
            }
        }


@dataclass
class TournamentResult:
    """Complete tournament results"""
    match_results: List[MatchResult]
    agent_scores: Dict[str, float]
    agent_stats: Dict[str, Dict]
    shadow_condition: float
    temperature_settings: Dict[str, float]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def save_to_csv(self, filepath: str):
        """Save results to CSV file"""
        rows = []
        for match in self.match_results:
            for i, (m1, m2) in enumerate(zip(match.agent1_moves, match.agent2_moves)):
                rows.append({
                    'timestamp': self.timestamp,
                    'shadow_condition': self.shadow_condition,
                    'match_id': f"{match.agent1_name}_vs_{match.agent2_name}",
                    'round': i + 1,
                    'agent1': match.agent1_name,
                    'agent2': match.agent2_name,
                    'agent1_move': m1,
                    'agent2_move': m2,
                    'agent1_total_score': match.agent1_score,
                    'agent2_total_score': match.agent2_score,
                    'agent1_reasoning': match.agent1_reasoning[i] if i < len(match.agent1_reasoning) else None,
                    'agent2_reasoning': match.agent2_reasoning[i] if i < len(match.agent2_reasoning) else None
                })
        
        df = pd.DataFrame(rows)
        df.to_csv(filepath, index=False)
        
    def get_summary_stats(self) -> pd.DataFrame:
        """Get summary statistics for all agents"""
        stats = []
        for agent_name, agent_data in self.agent_stats.items():
            stats.append({
                'agent': agent_name,
                'avg_score_per_move': agent_data['avg_score_per_move'],
                'total_score': agent_data['total_score'],
                'matches_played': agent_data['matches_played'],
                'total_moves': agent_data['total_moves'],
                'cooperation_rate': agent_data['cooperation_rate'],
                'first_move_cooperation': agent_data['first_move_cooperation']
            })
        return pd.DataFrame(stats).sort_values('avg_score_per_move', ascending=False)


class Tournament:
    """Main tournament runner with async support for concurrent matches"""
    
    def __init__(self, agents: List[Agent], termination_prob: float = 0.1,
                 max_rounds: int = 200, verbose: bool = True, max_concurrent: int = 50):
        self.agents = agents
        self.termination_prob = termination_prob
        self.max_rounds = max_rounds
        self.verbose = verbose
        self.max_concurrent = max_concurrent  # Limit concurrent matches
        self.payoff_matrix = {
            ('C', 'C'): (3, 3),
            ('C', 'D'): (0, 5),
            ('D', 'C'): (5, 0),
            ('D', 'D'): (1, 1)
        }
        
    def run_match(self, agent1: Agent, agent2: Agent) -> MatchResult:
        """Run a single match between two agents"""
        agent1.reset()
        agent2.reset()
        
        agent1_moves = []
        agent2_moves = []
        agent1_reasoning = []
        agent2_reasoning = []
        agent1_score = 0
        agent2_score = 0
        
        for round_num in range(self.max_rounds):
            # Get moves
            move1 = agent1.make_move(agent1_moves.copy(), agent2_moves.copy())
            move2 = agent2.make_move(agent2_moves.copy(), agent1_moves.copy())
            
            # Record moves
            agent1_moves.append(move1)
            agent2_moves.append(move2)
            
            # Record reasoning if available
            if hasattr(agent1, 'last_reasoning'):
                agent1_reasoning.append(agent1.last_reasoning)
            if hasattr(agent2, 'last_reasoning'):
                agent2_reasoning.append(agent2.last_reasoning)
            
            # Calculate scores
            score1, score2 = self.payoff_matrix[(move1, move2)]
            agent1_score += score1
            agent2_score += score2
            
            # Update adaptive agents
            if isinstance(agent1, ThompsonSampling):
                agent1.update(move1, move2, score1)
            if isinstance(agent2, ThompsonSampling):
                agent2.update(move2, move1, score2)
                
            # Check termination
            if random.random() < self.termination_prob:
                break
                
        # Update gradient learners after match
        if isinstance(agent1, GradientMetaLearner):
            agent1.reward_history = [self.payoff_matrix[(m1, m2)][0] 
                                   for m1, m2 in zip(agent1_moves, agent2_moves)]
            agent1.update_policy()
        if isinstance(agent2, GradientMetaLearner):
            agent2.reward_history = [self.payoff_matrix[(m1, m2)][1] 
                                   for m1, m2 in zip(agent1_moves, agent2_moves)]
            agent2.update_policy()
            
        return MatchResult(
            agent1_name=agent1.name,
            agent2_name=agent2.name,
            agent1_moves=agent1_moves,
            agent2_moves=agent2_moves,
            agent1_score=agent1_score,
            agent2_score=agent2_score,
            rounds_played=len(agent1_moves),
            agent1_reasoning=agent1_reasoning,
            agent2_reasoning=agent2_reasoning
        )
    
    async def run_match_async(self, agent1: Agent, agent2: Agent) -> MatchResult:
        """Run a single match between two agents asynchronously"""
        agent1.reset()
        agent2.reset()
        
        agent1_moves = []
        agent2_moves = []
        agent1_reasoning = []
        agent2_reasoning = []
        agent1_score = 0
        agent2_score = 0
        
        for round_num in range(self.max_rounds):
            # Get moves concurrently using thread pool for blocking operations
            loop = asyncio.get_event_loop()
            
            # Run both agents' make_move in parallel using thread pool
            tasks = [
                loop.run_in_executor(None, agent1.make_move, agent1_moves.copy(), agent2_moves.copy()),
                loop.run_in_executor(None, agent2.make_move, agent2_moves.copy(), agent1_moves.copy())
            ]
            
            # Execute both moves concurrently
            move1, move2 = await asyncio.gather(*tasks)
            
            # Record moves
            agent1_moves.append(move1)
            agent2_moves.append(move2)
            
            # Record reasoning if available
            if hasattr(agent1, 'last_reasoning'):
                agent1_reasoning.append(agent1.last_reasoning)
            if hasattr(agent2, 'last_reasoning'):
                agent2_reasoning.append(agent2.last_reasoning)
            
            # Calculate scores
            score1, score2 = self.payoff_matrix[(move1, move2)]
            agent1_score += score1
            agent2_score += score2
            
            # Update adaptive agents
            if isinstance(agent1, ThompsonSampling):
                agent1.update(move1, move2, score1)
            if isinstance(agent2, ThompsonSampling):
                agent2.update(move2, move1, score2)
                
            # Check termination
            if random.random() < self.termination_prob:
                break
                
        # Update gradient learners after match
        if isinstance(agent1, GradientMetaLearner):
            agent1.reward_history = [self.payoff_matrix[(m1, m2)][0] 
                                   for m1, m2 in zip(agent1_moves, agent2_moves)]
            agent1.update_policy()
        if isinstance(agent2, GradientMetaLearner):
            agent2.reward_history = [self.payoff_matrix[(m1, m2)][1] 
                                   for m1, m2 in zip(agent1_moves, agent2_moves)]
            agent2.update_policy()
            
        return MatchResult(
            agent1_name=agent1.name,
            agent2_name=agent2.name,
            agent1_moves=agent1_moves,
            agent2_moves=agent2_moves,
            agent1_score=agent1_score,
            agent2_score=agent2_score,
            rounds_played=len(agent1_moves),
            agent1_reasoning=agent1_reasoning,
            agent2_reasoning=agent2_reasoning
        )
    
    def run_tournament(self) -> TournamentResult:
        """Run full round-robin tournament (synchronous version for compatibility)"""
        try:
            # Try to run async version if we're in an async context
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # We're already in an async context, can't use asyncio.run
                return loop.run_until_complete(self.run_tournament_async())
            else:
                # Not in async context, safe to use asyncio.run
                return asyncio.run(self.run_tournament_async())
        except RuntimeError:
            # Fallback to synchronous version
            return self._run_tournament_sync()
    
    def _run_tournament_sync(self) -> TournamentResult:
        """Synchronous tournament runner (original implementation)"""
        match_results = []
        agent_scores = defaultdict(int)
        agent_moves = defaultdict(list)
        agent_matches = defaultdict(int)
        
        # Progress bar
        total_matches = len(self.agents) * (len(self.agents) - 1) // 2
        pbar = tqdm(total=total_matches, desc="Running matches", disable=not self.verbose)
        
        # Round-robin matches
        for i, agent1 in enumerate(self.agents):
            for j, agent2 in enumerate(self.agents[i+1:], i+1):
                result = self.run_match(agent1, agent2)
                match_results.append(result)
                
                # Update scores
                agent_scores[agent1.name] += result.agent1_score
                agent_scores[agent2.name] += result.agent2_score
                
                # Track moves
                agent_moves[agent1.name].extend(result.agent1_moves)
                agent_moves[agent2.name].extend(result.agent2_moves)
                
                # Track matches
                agent_matches[agent1.name] += 1
                agent_matches[agent2.name] += 1
                
                pbar.update(1)
                
        pbar.close()
        
        return self._calculate_tournament_result(match_results, agent_scores, agent_moves, agent_matches)
    
    async def run_tournament_async(self, max_concurrent: int = None) -> TournamentResult:
        """Run full round-robin tournament with concurrent matches"""
        if max_concurrent is None:
            max_concurrent = self.max_concurrent
        if max_concurrent is None or max_concurrent <= 0:
            max_concurrent = 20  # Default fallback
            
        match_results = []
        agent_scores = defaultdict(int)
        agent_moves = defaultdict(list)
        agent_matches = defaultdict(int)
        
        # Create all match pairs
        match_pairs = []
        for i, agent1 in enumerate(self.agents):
            for j, agent2 in enumerate(self.agents[i+1:], i+1):
                match_pairs.append((agent1, agent2))
        
        # Progress bar
        total_matches = len(match_pairs)
        pbar = tqdm(total=total_matches, desc="Running matches concurrently", disable=not self.verbose)
        
        # Create semaphore to limit concurrent matches
        semaphore = asyncio.Semaphore(max_concurrent)
        
        if self.verbose:
            print(f"Running {total_matches} matches with max {max_concurrent} concurrent")
        
        async def run_single_match(agent1, agent2):
            async with semaphore:
                result = await self.run_match_async(agent1, agent2)
                pbar.update(1)
                return result
        
        # Run all matches concurrently with semaphore limiting
        tasks = [run_single_match(agent1, agent2) for agent1, agent2 in match_pairs]
        match_results = await asyncio.gather(*tasks)
        
        pbar.close()
        
        # Process results
        for result in match_results:
            # Update scores
            agent_scores[result.agent1_name] += result.agent1_score
            agent_scores[result.agent2_name] += result.agent2_score
            
            # Track moves
            agent_moves[result.agent1_name].extend(result.agent1_moves)
            agent_moves[result.agent2_name].extend(result.agent2_moves)
            
            # Track matches
            agent_matches[result.agent1_name] += 1
            agent_matches[result.agent2_name] += 1
        
        return self._calculate_tournament_result(match_results, agent_scores, agent_moves, agent_matches)
    
    def _calculate_tournament_result(self, match_results, agent_scores, agent_moves, agent_matches) -> TournamentResult:
        """Helper method to calculate tournament statistics"""
        
        # Calculate statistics
        agent_stats = {}
        for agent in self.agents:
            name = agent.name
            moves = agent_moves[name]
            
            if moves:
                coop_rate = moves.count('C') / len(moves)
                first_moves = [m.agent1_moves[0] if m.agent1_name == name else m.agent2_moves[0]
                              for m in match_results if name in [m.agent1_name, m.agent2_name]]
                first_coop = first_moves.count('C') / len(first_moves) if first_moves else 0
            else:
                coop_rate = 0
                first_coop = 0
                
            agent_stats[name] = {
                'total_score': agent_scores[name],
                'matches_played': agent_matches[name],
                'total_moves': len(moves),
                'avg_score_per_move': agent_scores[name] / len(moves) if moves else 0,
                'cooperation_rate': coop_rate,
                'first_move_cooperation': first_coop
            }
            
        # Get temperature settings for LLM agents
        temp_settings = {}
        for agent in self.agents:
            if hasattr(agent, 'temperature'):
                temp_settings[agent.name] = agent.temperature
                
        return TournamentResult(
            match_results=match_results,
            agent_scores=dict(agent_scores),
            agent_stats=agent_stats,
            shadow_condition=self.termination_prob,
            temperature_settings=temp_settings
        )
    
    def run_multiple_tournaments(self, n_tournaments: int = 10) -> List[TournamentResult]:
        """Run multiple tournaments for statistical significance"""
        results = []
        for i in range(n_tournaments):
            if self.verbose:
                print(f"\nTournament {i+1}/{n_tournaments}")
            result = self.run_tournament()
            results.append(result)
        return results


class LLMShowdown:
    """Special tournament format for LLM-only competition"""
    
    def __init__(self, llm_agents: List[Agent], termination_probs: List[float],
                 rounds_per_condition: int = 10, verbose: bool = True):
        self.llm_agents = llm_agents
        self.termination_probs = termination_probs
        self.rounds_per_condition = rounds_per_condition
        self.verbose = verbose
        
    def run(self) -> Dict[str, List[TournamentResult]]:
        """Run showdown across all conditions"""
        all_results = {}
        
        for term_prob in self.termination_probs:
            if self.verbose:
                print(f"\nRunning LLM Showdown with {term_prob*100}% termination probability")
                
            tournament = Tournament(
                agents=self.llm_agents,
                termination_prob=term_prob,
                verbose=self.verbose
            )
            
            results = tournament.run_multiple_tournaments(self.rounds_per_condition)
            all_results[f"shadow_{int(term_prob*100)}"] = results
            
        return all_results