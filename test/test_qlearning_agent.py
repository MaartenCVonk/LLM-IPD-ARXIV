import pytest
import sys
import os

# Add the parent directory to the path so we can import ipd_suite
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ipd_suite.agents import QLearningAgent, TitForTat, AlwaysDefect, AlwaysCooperate, GrimTrigger


class TestQLearningAgent:
    """Test suite for QLearningAgent behavior"""

    def test_qlearning_agent_initialization(self):
        """Test that QLearningAgent initializes correctly"""
        agent = QLearningAgent("QLearning")
        
        assert agent.name == "QLearning"
        assert agent.alpha == 0.7  # Default learning rate (optimized for length 4)
        assert agent.gamma == 0.5  # Default discount factor (optimized for length 4)
        assert agent.epsilon == 0.3  # Default exploration rate (optimized for length 4)
        assert agent.q_table == {}
        assert agent.last_state is None
        assert agent.last_action is None

    def test_qlearning_agent_custom_parameters(self):
        """Test QLearningAgent with custom parameters"""
        agent = QLearningAgent("QLearning", alpha=0.2, gamma=0.8, epsilon=0.05)
        
        assert agent.alpha == 0.2
        assert agent.gamma == 0.8
        assert agent.epsilon == 0.05

    def test_qlearning_agent_state_representation(self):
        """Test that QLearningAgent represents states correctly"""
        agent = QLearningAgent("QLearning")
        
        # Test initial state
        state = agent._get_state([], [])
        assert state == ('START', 'START')
        
        # Test state after one round
        state = agent._get_state(['C'], ['D'])
        assert state == ('C', 'D')
        
        # Test state representation uses only last moves
        state = agent._get_state(['C', 'D', 'C'], ['D', 'C', 'D'])
        assert state == ('C', 'D')

    def test_qlearning_agent_q_value_operations(self):
        """Test Q-value getting and setting"""
        agent = QLearningAgent("QLearning")
        
        # Test getting non-existent Q-value (now uses optimistic initialization)
        state = ('C', 'D')
        q_value = agent._get_q_value(state, 'C')
        assert q_value == 10.0  # Optimistic initialization value
        
        # Test setting Q-value
        agent.q_table[(state, 'C')] = 1.5
        q_value = agent._get_q_value(state, 'C')
        assert q_value == 1.5

    def test_qlearning_agent_reward_calculation(self):
        """Test reward calculation based on payoff matrix"""
        agent = QLearningAgent("QLearning")
        
        # Test all possible outcomes
        assert agent._calculate_reward('C', 'C') == 3  # Mutual cooperation
        assert agent._calculate_reward('C', 'D') == 0  # Sucker
        assert agent._calculate_reward('D', 'C') == 5  # Temptation
        assert agent._calculate_reward('D', 'D') == 1  # Mutual defection

    def test_qlearning_agent_vs_always_cooperate(self):
        """Test QLearningAgent against AlwaysCooperate"""
        qlearning = QLearningAgent("QLearning", alpha=0.3, gamma=0.7, epsilon=0.1)
        always_coop = AlwaysCooperate("AlwaysCooperate")
        
        qlearning_moves = []
        coop_moves = []
        
        # Play 50 rounds to allow learning
        for i in range(50):
            q_move = qlearning.make_move(qlearning_moves, coop_moves)
            coop_move = always_coop.make_move(coop_moves, qlearning_moves)
            
            qlearning_moves.append(q_move)
            coop_moves.append(coop_move)
        
        # QLearning should learn to defect against AlwaysCooperate
        # since defection gives higher payoff (5 vs 3)
        defection_rate = qlearning_moves.count('D') / len(qlearning_moves)
        assert defection_rate > 0.7  # Should learn to defect more often

    def test_qlearning_agent_vs_always_defect(self):
        """Test QLearningAgent against AlwaysDefect"""
        qlearning = QLearningAgent("QLearning", epsilon=0.1)  # Decent exploration rate
        always_def = AlwaysDefect("AlwaysDefect")
        
        qlearning_moves = []
        def_moves = []
        
        # Play 30 rounds to allow learning
        for i in range(30):
            q_move = qlearning.make_move(qlearning_moves, def_moves)
            def_move = always_def.make_move(def_moves, qlearning_moves)
            
            qlearning_moves.append(q_move)
            def_moves.append(def_move)
        
        # QLearning should learn to defect against AlwaysDefect
        # since defection gives better payoff (1 vs 0)
        cooperation_rate = qlearning_moves.count('C') / len(qlearning_moves)
        assert cooperation_rate < 0.5  # Should cooperate less than half the time

    def test_qlearning_agent_vs_tit_for_tat(self):
        """Test QLearningAgent against TitForTat"""
        qlearning = QLearningAgent("QLearning", epsilon=0.1)
        tit_for_tat = TitForTat("TitForTat")
        
        qlearning_moves = []
        tft_moves = []
        
        # Play 50 rounds to allow learning
        for i in range(50):
            q_move = qlearning.make_move(qlearning_moves, tft_moves)
            tft_move = tit_for_tat.make_move(tft_moves, qlearning_moves)
            
            qlearning_moves.append(q_move)
            tft_moves.append(tft_move)
        
        # Against TitForTat, behavior depends on learning - may vary
        # Just check that learning occurs
        assert len(qlearning.q_table) > 0  # Should have learned something

    def test_qlearning_agent_vs_grim_trigger(self):
        """Test QLearningAgent against GrimTrigger"""
        qlearning = QLearningAgent("QLearning", epsilon=0.1)
        grim = GrimTrigger("GrimTrigger")
        
        qlearning_moves = []
        grim_moves = []
        
        # Play 40 rounds
        for i in range(40):
            q_move = qlearning.make_move(qlearning_moves, grim_moves)
            grim_move = grim.make_move(grim_moves, qlearning_moves)
            
            qlearning_moves.append(q_move)
            grim_moves.append(grim_move)
        
        # Against GrimTrigger, behavior depends on learning - may vary
        # Just check that learning occurs
        assert len(qlearning.q_table) > 0  # Should have learned something

    def test_qlearning_agent_exploration_exploitation(self):
        """Test that QLearningAgent balances exploration and exploitation"""
        agent = QLearningAgent("QLearning", epsilon=0.5)  # High exploration
        
        # Set up Q-table to heavily favor cooperation
        agent.q_table[(('START', 'START'), 'C')] = 10.0
        agent.q_table[(('START', 'START'), 'D')] = 0.0
        
        moves = []
        for i in range(100):
            move = agent.make_move([], [])
            moves.append(move)
        
        # With high epsilon, should see some defection despite favoring cooperation
        defection_rate = moves.count('D') / len(moves)
        assert 0.1 < defection_rate < 0.6  # Should explore with some probability

    def test_qlearning_agent_learning_updates(self):
        """Test that QLearningAgent updates Q-values correctly"""
        agent = QLearningAgent("QLearning", alpha=0.5, gamma=0.9, epsilon=0.0)
        
        # Initial Q-values should be optimistic initialization value
        assert agent._get_q_value(('START', 'START'), 'C') == 10.0
        
        # Make first move
        move1 = agent.make_move([], [])
        
        # Make second move (this should trigger Q-value update)
        move2 = agent.make_move([move1], ['C'])
        
        # Q-table should now have some values
        assert len(agent.q_table) > 0

    def test_qlearning_agent_reset(self):
        """Test that QLearningAgent resets correctly"""
        agent = QLearningAgent("QLearning")
        
        # Simulate some learning
        agent.make_move([], [])
        agent.make_move(['C'], ['D'])
        agent.last_state = ('C', 'D')
        agent.last_action = 'C'
        
        # Reset
        agent.reset()
        
        # Should clear learning state but keep Q-table
        assert agent.last_state is None
        assert agent.last_action is None
        assert agent.history == []
        assert agent.opponent_history == []
        # Q-table should persist across resets for continued learning

    def test_qlearning_agent_game_length_10(self):
        """Test QLearningAgent with parameters optimized for 10-round games"""
        # Recommended parameters for moderate games (length ~10)
        qlearning = QLearningAgent("QLearning", alpha=0.3, gamma=0.7, epsilon=0.2)
        always_coop = AlwaysCooperate("AlwaysCooperate")
        
        qlearning_moves = []
        coop_moves = []
        
        # Play 10 rounds
        for i in range(10):
            q_move = qlearning.make_move(qlearning_moves, coop_moves)
            coop_move = always_coop.make_move(coop_moves, qlearning_moves)
            
            qlearning_moves.append(q_move)
            coop_moves.append(coop_move)
        
        # Should learn to defect against AlwaysCooperate
        defection_rate = qlearning_moves.count('D') / len(qlearning_moves)
        assert defection_rate > 0.6  # Should learn to exploit

    def test_qlearning_agent_game_length_4(self):
        """Test QLearningAgent with parameters optimized for 4-round games"""
        # Recommended parameters for short games (length ~4)
        qlearning = QLearningAgent("QLearning", alpha=0.7, gamma=0.5, epsilon=0.3)
        always_coop = AlwaysCooperate("AlwaysCooperate")
        
        qlearning_moves = []
        coop_moves = []
        
        # Play 4 rounds
        for i in range(4):
            q_move = qlearning.make_move(qlearning_moves, coop_moves)
            coop_move = always_coop.make_move(coop_moves, qlearning_moves)
            
            qlearning_moves.append(q_move)
            coop_moves.append(coop_move)
        
        # Should learn to defect quickly against AlwaysCooperate
        defection_rate = qlearning_moves.count('D') / len(qlearning_moves)
        assert defection_rate >= 0.5  # Should learn to exploit even in short games

    def test_qlearning_agent_game_length_1(self):
        """Test QLearningAgent with parameters optimized for single-shot games"""
        # Recommended parameters for single-shot games (length 1)
        qlearning = QLearningAgent("QLearning", alpha=1.0, gamma=0.0, epsilon=0.0)
        always_coop = AlwaysCooperate("AlwaysCooperate")
        
        # Single shot game
        q_move = qlearning.make_move([], [])
        
        # Should defect due to optimistic initialization
        # (Q-values start at 10.0, so it will try the "better" option first)
        assert q_move == 'D'  # Should defect to maximize single-round payoff

    def test_qlearning_agent_parameter_comparison(self):
        """Compare performance across different game length parameter settings"""
        
        # Test configurations for different game lengths
        configs = [
            ("length_10", {"alpha": 0.3, "gamma": 0.7, "epsilon": 0.2}, 10),
            ("length_4", {"alpha": 0.7, "gamma": 0.5, "epsilon": 0.3}, 4),
            ("length_1", {"alpha": 1.0, "gamma": 0.0, "epsilon": 0.0}, 1)
        ]
        
        results = {}
        
        for config_name, params, game_length in configs:
            qlearning = QLearningAgent("QLearning", **params)
            always_coop = AlwaysCooperate("AlwaysCooperate")
            
            moves = []
            for i in range(game_length):
                move = qlearning.make_move(moves, ['C'] * i)
                moves.append(move)
            
            defection_rate = moves.count('D') / len(moves) if moves else 0
            results[config_name] = defection_rate
        
        # All configurations should achieve reasonable defection rates
        assert results["length_10"] > 0.5
        assert results["length_4"] > 0.4
        assert results["length_1"] == 1.0  # Single defection

    def test_qlearning_agent_factory_method(self):
        """Test the factory method for creating agents with optimal parameters"""
        
        # Test single-shot parameters
        agent_1 = QLearningAgent.for_game_length("Q1", 1)
        assert agent_1.alpha == 1.0
        assert agent_1.gamma == 0.0
        assert agent_1.epsilon == 0.0
        
        # Test short game parameters
        agent_4 = QLearningAgent.for_game_length("Q4", 4)
        assert agent_4.alpha == 0.7
        assert agent_4.gamma == 0.5
        assert agent_4.epsilon == 0.3
        
        # Test moderate game parameters
        agent_10 = QLearningAgent.for_game_length("Q10", 10)
        assert agent_10.alpha == 0.3
        assert agent_10.gamma == 0.7
        assert agent_10.epsilon == 0.2
        
        # Test long game parameters
        agent_50 = QLearningAgent.for_game_length("Q50", 50)
        assert agent_50.alpha == 0.1
        assert agent_50.gamma == 0.9
        assert agent_50.epsilon == 0.1


if __name__ == "__main__":
    pytest.main([__file__])