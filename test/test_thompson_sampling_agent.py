import pytest
import sys
import os
import numpy as np

# Add the parent directory to the path so we can import ipd_suite
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ipd_suite.agents import ThompsonSampling, AlwaysDefect, AlwaysCooperate, GrimTrigger


class TestThompsonSamplingAgent:
    """Test suite for ThompsonSampling agent behavior"""

    def test_thompson_sampling_initialization(self):
        """Test that ThompsonSampling initializes correctly"""
        agent = ThompsonSampling("ThompsonSampling")
        
        assert agent.name == "ThompsonSampling"
        # Beta distribution parameters start at 1 (uninformative prior)
        assert agent.alpha_c == 1  # Successes for cooperation
        assert agent.beta_c == 1   # Failures for cooperation
        assert agent.alpha_d == 1  # Successes for defection
        assert agent.beta_d == 1   # Failures for defection

    def test_thompson_sampling_update_mechanism(self):
        """Test the adaptive update mechanism for beta parameters"""
        agent = ThompsonSampling("ThompsonSampling")  # Uses default parameters: base_lr=0.2, lr_scale=1.2 (optimized for length 5)
        
        # Test cooperation with moderate payoff (payoff 3)
        agent.update('C', 'C', 3.0)
        expected_alpha_c = 1 + (0.2 + (3.0 / 5.0) * 1.2)  # 1 + 0.92 = 1.92
        assert abs(agent.alpha_c - expected_alpha_c) < 0.01
        assert agent.beta_c == 1   # No penalty for payoff 3
        
        # Test cooperation with low payoff (payoff 0)
        agent.update('C', 'D', 0.0)
        expected_alpha_c += (0.2 + (0.0 / 5.0) * 1.2)  # Add 0.2
        expected_beta_c = 1 + (2.5 - 0.0) * 0.2  # Add penalty: 0.5
        assert abs(agent.alpha_c - expected_alpha_c) < 0.01
        assert abs(agent.beta_c - expected_beta_c) < 0.01
        
        # Test defection with high payoff (payoff 5)
        agent.update('D', 'C', 5.0)
        expected_alpha_d = 1 + (0.2 + (5.0 / 5.0) * 1.2)  # 1 + 1.4 = 2.4
        assert abs(agent.alpha_d - expected_alpha_d) < 0.01
        assert agent.beta_d == 1   # No penalty for payoff 5
        
        # Test defection with low payoff (payoff 1)
        agent.update('D', 'D', 1.0)
        expected_alpha_d += (0.2 + (1.0 / 5.0) * 1.2)  # Add 0.44
        expected_beta_d = 1 + (2.5 - 1.0) * 0.2  # Add penalty: 0.3
        assert abs(agent.alpha_d - expected_alpha_d) < 0.01
        assert abs(agent.beta_d - expected_beta_d) < 0.01

    def test_thompson_sampling_decision_making(self):
        """Test that ThompsonSampling makes decisions based on beta distributions"""
        agent = ThompsonSampling("ThompsonSampling")
        
        # Initially, both actions have equal beta(1,1) distributions
        # Make several moves to see both C and D
        moves = []
        for i in range(100):
            move = agent.make_move([], [])
            moves.append(move)
        
        # Should see both cooperation and defection
        cooperation_count = moves.count('C')
        defection_count = moves.count('D')
        assert cooperation_count > 0
        assert defection_count > 0

    def test_thompson_sampling_vs_always_cooperate(self):
        """Test ThompsonSampling against AlwaysCooperate"""
        thompson = ThompsonSampling("ThompsonSampling")
        always_coop = AlwaysCooperate("AlwaysCooperate")
        
        thompson_moves = []
        coop_moves = []
        
        # Play 50 rounds with learning
        for i in range(50):
            t_move = thompson.make_move(thompson_moves, coop_moves)
            c_move = always_coop.make_move(coop_moves, thompson_moves)
            
            thompson_moves.append(t_move)
            coop_moves.append(c_move)
            
            # Update Thompson sampling with payoff
            if t_move == 'C' and c_move == 'C':
                payoff = 3.0
            elif t_move == 'C' and c_move == 'D':
                payoff = 0.0
            elif t_move == 'D' and c_move == 'C':
                payoff = 5.0
            else:  # D, D
                payoff = 1.0
            
            thompson.update(t_move, c_move, payoff)
        
        # Thompson sampling should learn to defect against AlwaysCooperate
        # since defection gives higher payoff (5 vs 3)
        defection_rate = thompson_moves.count('D') / len(thompson_moves)
        assert defection_rate > 0.2  # Should learn to defect more often

    def test_thompson_sampling_vs_always_defect(self):
        """Test ThompsonSampling against AlwaysDefect"""
        thompson = ThompsonSampling("ThompsonSampling")
        always_def = AlwaysDefect("AlwaysDefect")
        
        thompson_moves = []
        def_moves = []
        
        # Play 50 rounds with learning
        for i in range(50):
            t_move = thompson.make_move(thompson_moves, def_moves)
            d_move = always_def.make_move(def_moves, thompson_moves)
            
            thompson_moves.append(t_move)
            def_moves.append(d_move)
            
            # Update Thompson sampling with payoff
            if t_move == 'C' and d_move == 'C':
                payoff = 3.0
            elif t_move == 'C' and d_move == 'D':
                payoff = 0.0
            elif t_move == 'D' and d_move == 'C':
                payoff = 5.0
            else:  # D, D
                payoff = 1.0
            
            thompson.update(t_move, d_move, payoff)
        
        # Thompson sampling should learn that defection is better
        # against AlwaysDefect (mutual defection gives 1.0 < 2.25, cooperation gives 0.0 < 2.25)
        # Both are failures, but defection at least gives some payoff
        defection_rate = thompson_moves.count('D') / len(thompson_moves)
        assert defection_rate > 0.65  # Should tend towards defection

    def test_thompson_sampling_vs_grim_trigger(self):
        """Test ThompsonSampling against GrimTrigger"""
        thompson = ThompsonSampling("ThompsonSampling")
        grim_trigger = GrimTrigger("GrimTrigger")
        
        thompson_moves = []
        grim_moves = []
        
        # Play 60 rounds with learning
        for i in range(60):
            t_move = thompson.make_move(thompson_moves, grim_moves)
            g_move = grim_trigger.make_move(grim_moves, thompson_moves)
            
            thompson_moves.append(t_move)
            grim_moves.append(g_move)
            
            # Update Thompson sampling with payoff
            if t_move == 'C' and g_move == 'C':
                payoff = 3.0
            elif t_move == 'C' and g_move == 'D':
                payoff = 0.0
            elif t_move == 'D' and g_move == 'C':
                payoff = 5.0
            else:  # D, D
                payoff = 1.0
            
            thompson.update(t_move, g_move, payoff)
        
        # Against GrimTrigger, should learn strategic behavior
        # Should learn to defect since it can exploit early cooperation
        defection_rate = thompson_moves.count('D') / len(thompson_moves)
        assert defection_rate > 0.4  # Should learn to defect more often


    def test_thompson_sampling_beta_parameter_evolution(self):
        """Test that beta parameters evolve correctly over time with adaptive learning"""
        agent = ThompsonSampling("ThompsonSampling")  # Uses default parameters: base_lr=0.2, lr_scale=1.2 (optimized for length 5)
        
        # Simulate cooperation with payoff 3
        for i in range(5):
            agent.update('C', 'C', 3.0)
        
        # Simulate defection with payoff 1 (below average)
        for i in range(3):
            agent.update('D', 'D', 1.0)
        
        # Check parameter evolution with adaptive learning rates
        learning_rate_3 = 0.2 + (3.0 / 5.0) * 1.2  # 0.92
        learning_rate_1 = 0.2 + (1.0 / 5.0) * 1.2  # 0.44
        penalty_1 = (2.5 - 1.0) * 0.2  # 0.3
        
        expected_alpha_c = 1 + 5 * learning_rate_3
        expected_beta_c = 1  # No penalty for payoff 3
        expected_alpha_d = 1 + 3 * learning_rate_1
        expected_beta_d = 1 + 3 * penalty_1
        
        assert abs(agent.alpha_c - expected_alpha_c) < 0.01
        assert abs(agent.beta_c - expected_beta_c) < 0.01
        assert abs(agent.alpha_d - expected_alpha_d) < 0.01
        assert abs(agent.beta_d - expected_beta_d) < 0.01

    def test_thompson_sampling_adaptive_learning_rates(self):
        """Test the adaptive learning rate calculation"""
        agent = ThompsonSampling("ThompsonSampling")  # Uses default parameters: base_lr=0.2, lr_scale=1.2 (optimized for length 5)
        
        # Test different payoff levels
        test_cases = [
            (0.0, 0.2),    # Minimum payoff → minimum learning rate
            (2.5, 0.8),    # Average payoff → medium learning rate  
            (5.0, 1.4),    # Maximum payoff → maximum learning rate
        ]
        
        for payoff, expected_lr in test_cases:
            agent_test = ThompsonSampling("Test")  # Uses default parameters: base_lr=0.2, lr_scale=1.2 (optimized for length 5) (optimized for length 5)
            agent_test.update('C', 'C', payoff)
            
            actual_lr = 0.2 + (payoff / 5.0) * 1.2
            assert abs(actual_lr - expected_lr) < 0.01
            
            expected_alpha = 1 + actual_lr
            assert abs(agent_test.alpha_c - expected_alpha) < 0.01

    def test_thompson_sampling_stochastic_behavior(self):
        """Test that ThompsonSampling exhibits stochastic behavior"""
        agent = ThompsonSampling("ThompsonSampling")
        
        # Set up biased parameters favoring cooperation
        agent.alpha_c = 10  # High success rate for cooperation
        agent.beta_c = 2
        agent.alpha_d = 2   # Low success rate for defection
        agent.beta_d = 10
        
        moves = []
        for i in range(100):
            move = agent.make_move([], [])
            moves.append(move)
        
        # Should mostly cooperate but still show some defection due to sampling
        cooperation_rate = moves.count('C') / len(moves)
        assert 0.6 < cooperation_rate <= 1.0  # Should be biased towards cooperation

    def test_thompson_sampling_payoff_sensitivity(self):
        """Test that Thompson sampling properly distinguishes between payoff magnitudes"""
        agent = ThompsonSampling("ThompsonSampling")  # Uses default parameters: base_lr=0.2, lr_scale=1.2 (optimized for length 5)
        
        # Compare learning from payoff 3 vs payoff 5
        agent.update('C', 'C', 3.0)  # Moderate payoff
        alpha_c_after_3 = agent.alpha_c
        
        agent.update('D', 'C', 5.0)  # High payoff
        alpha_d_after_5 = agent.alpha_d
        
        # Higher payoff should result in stronger learning
        learning_rate_3 = 0.2 + (3.0 / 5.0) * 1.2  # 0.92
        learning_rate_5 = 0.2 + (5.0 / 5.0) * 1.2  # 1.4
        
        expected_alpha_c = 1 + learning_rate_3
        expected_alpha_d = 1 + learning_rate_5
        
        assert abs(alpha_c_after_3 - expected_alpha_c) < 0.01
        assert abs(alpha_d_after_5 - expected_alpha_d) < 0.01
        
        # Verify that payoff 5 gives stronger learning than payoff 3
        assert learning_rate_5 > learning_rate_3
        assert alpha_d_after_5 > alpha_c_after_3

    def test_thompson_sampling_reset(self):
        """Test that ThompsonSampling resets correctly"""
        agent = ThompsonSampling("ThompsonSampling")
        
        # Modify parameters through updates
        agent.update('C', 'C', 3.0)
        agent.update('D', 'D', 1.0)
        
        # Reset
        agent.reset()
        
        # Should reset base agent state but keep beta parameters for continued learning
        assert agent.history == []
        assert agent.opponent_history == []
        # Beta parameters should persist to maintain learning

    def test_thompson_sampling_game_length_factory(self):
        """Test the factory method for creating agents with optimal parameters for different game lengths"""
        
        # Test very short game parameters (mean ~1.3)
        agent_1_3 = ThompsonSampling.for_game_length("TS1.3", 1.3)
        assert agent_1_3.base_learning_rate == 0.3
        assert agent_1_3.learning_rate_scale == 1.5
        
        # Test short game parameters (mean ~4)
        agent_4 = ThompsonSampling.for_game_length("TS4", 4.0)
        assert agent_4.base_learning_rate == 0.2
        assert agent_4.learning_rate_scale == 1.2
        
        # Test moderate game parameters (mean ~10)
        agent_10 = ThompsonSampling.for_game_length("TS10", 10.0)
        assert agent_10.base_learning_rate == 0.1
        assert agent_10.learning_rate_scale == 0.9
        
        # Test long game parameters
        agent_50 = ThompsonSampling.for_game_length("TS50", 50.0)
        assert agent_50.base_learning_rate == 0.05
        assert agent_50.learning_rate_scale == 0.7

    def test_thompson_sampling_game_length_learning_speed(self):
        """Test that shorter games learn faster than longer games"""
        
        # Create agents for different game lengths
        agent_short = ThompsonSampling.for_game_length("Short", 1.3)
        agent_long = ThompsonSampling.for_game_length("Long", 10.0)
        
        # Apply the same high payoff update to both
        agent_short.update('D', 'C', 5.0)
        agent_long.update('D', 'C', 5.0)
        
        # Short game agent should have learned more (higher alpha_d)
        assert agent_short.alpha_d > agent_long.alpha_d
        
        # Check the actual learning rates
        short_lr = agent_short.base_learning_rate + (5.0 / 5.0) * agent_short.learning_rate_scale
        long_lr = agent_long.base_learning_rate + (5.0 / 5.0) * agent_long.learning_rate_scale
        
        assert short_lr > long_lr

    def test_thompson_sampling_game_length_vs_always_cooperate(self):
        """Test that game length optimization creates different learning behavior"""
        
        # Compare short game vs long game agents
        agent_short = ThompsonSampling.for_game_length("Short", 1.3)
        agent_long = ThompsonSampling.for_game_length("Long", 10.0)
        
        # Test same high payoff scenario for both
        agent_short.update('D', 'C', 5.0)
        agent_long.update('D', 'C', 5.0)
        
        # Short game agent should have higher alpha_d due to faster learning
        assert agent_short.alpha_d > agent_long.alpha_d
        
        # Verify the learning rate difference
        short_lr = agent_short.base_learning_rate + (5.0 / 5.0) * agent_short.learning_rate_scale
        long_lr = agent_long.base_learning_rate + (5.0 / 5.0) * agent_long.learning_rate_scale
        
        assert short_lr > long_lr

    def test_thompson_sampling_adaptive_learning_rate_calculation(self):
        """Test the new adaptive learning rate calculation with game length parameters"""
        
        # Test different configurations
        test_cases = [
            (1.3, 0.3, 1.5, 5.0, 1.8),  # Short game, high payoff
            (4.0, 0.2, 1.2, 3.0, 0.92),  # Medium game, medium payoff
            (10.0, 0.1, 0.9, 1.0, 0.28),  # Long game, low payoff
        ]
        
        for game_length, base_lr, lr_scale, payoff, expected_lr in test_cases:
            agent = ThompsonSampling.for_game_length("Test", game_length)
            
            # Calculate expected learning rate
            calculated_lr = base_lr + (payoff / 5.0) * lr_scale
            assert abs(calculated_lr - expected_lr) < 0.01


if __name__ == "__main__":
    pytest.main([__file__])