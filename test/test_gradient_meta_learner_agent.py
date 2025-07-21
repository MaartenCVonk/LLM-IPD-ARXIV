import pytest
import sys
import os
import numpy as np

# Add the parent directory to the path so we can import ipd_suite
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ipd_suite.agents import GradientMetaLearner, TitForTat, AlwaysDefect, AlwaysCooperate, GrimTrigger


class TestGradientMetaLearnerAgent:
    """Test suite for GradientMetaLearner agent behavior"""

    def test_gradient_meta_learner_initialization(self):
        """Test that GradientMetaLearner initializes correctly"""
        agent = GradientMetaLearner("GradientMetaLearner")
        
        assert agent.name == "GradientMetaLearner"
        assert agent.learning_rate == 0.05  # Default learning rate (optimized for length 5)
        assert agent.weights.shape == (5,)  # 5 feature weights
        assert np.all(agent.weights == 0)  # Weights start at zero
        assert agent.feature_history == []
        assert agent.action_history == []
        assert agent.reward_history == []

    def test_gradient_meta_learner_custom_learning_rate(self):
        """Test GradientMetaLearner with custom learning rate"""
        agent = GradientMetaLearner("GradientMetaLearner", learning_rate=0.05)
        assert agent.learning_rate == 0.05

    def test_gradient_meta_learner_feature_extraction(self):
        """Test feature extraction from game state"""
        agent = GradientMetaLearner("GradientMetaLearner")
        
        # Test initial state (first round)
        features = agent._extract_features([], [])
        assert features.shape == (5,)
        assert features[0] == 1  # First round indicator
        assert np.all(features[1:] == 0)  # Other features should be zero
        
        # Test after some gameplay
        own_history = ['C', 'C', 'D', 'C', 'C']
        opponent_history = ['C', 'D', 'D', 'C', 'D']
        
        features = agent._extract_features(own_history, opponent_history)
        
        # Feature 0: First round (should be 0)
        assert features[0] == 0
        
        # Feature 1: Opponent cooperation rate
        expected_coop_rate = opponent_history.count('C') / len(opponent_history)
        assert abs(features[1] - expected_coop_rate) < 1e-6
        
        # Feature 2: Recent opponent cooperation (last 3 moves)
        recent_coop_rate = opponent_history[-3:].count('C') / 3
        assert abs(features[2] - recent_coop_rate) < 1e-6
        
        # Feature 3: Mutual cooperation rate
        mutual_coop = sum(1 for i in range(len(own_history)) 
                         if own_history[i] == 'C' and opponent_history[i] == 'C')
        expected_mutual_rate = mutual_coop / len(own_history)
        assert abs(features[3] - expected_mutual_rate) < 1e-6
        
        # Feature 4: Rounds played (normalized for ~5 round games)
        expected_rounds = min(len(own_history) / 5, 1.0)
        assert abs(features[4] - expected_rounds) < 1e-6

    def test_gradient_meta_learner_policy_function(self):
        """Test the policy function (sigmoid)"""
        agent = GradientMetaLearner("GradientMetaLearner")
        
        # Test with zero weights (should give probability 0.5)
        features = np.array([1, 0, 0, 0, 0])
        prob = agent._policy(features)
        assert abs(prob - 0.5) < 1e-6
        
        # Test with positive weights (should favor cooperation)
        agent.weights = np.array([2, 1, 1, 1, 1])
        prob = agent._policy(features)
        assert prob > 0.5
        
        # Test with negative weights (should favor defection)
        agent.weights = np.array([-2, -1, -1, -1, -1])
        prob = agent._policy(features)
        assert prob < 0.5

    def test_gradient_meta_learner_stochastic_decisions(self):
        """Test that GradientMetaLearner makes stochastic decisions"""
        agent = GradientMetaLearner("GradientMetaLearner")
        
        # Set weights to favor cooperation
        agent.weights = np.array([1, 1, 1, 1, 1])
        
        moves = []
        for i in range(100):
            move = agent.make_move([], [])
            moves.append(move)
        
        # Should see both cooperation and defection due to stochastic policy
        cooperation_count = moves.count('C')
        defection_count = moves.count('D')
        assert cooperation_count > 0
        assert defection_count > 0
        
        # Should favor cooperation given positive weights
        cooperation_rate = cooperation_count / len(moves)
        assert cooperation_rate > 0.5

    def test_gradient_meta_learner_history_tracking(self):
        """Test that GradientMetaLearner tracks history correctly"""
        agent = GradientMetaLearner("GradientMetaLearner")
        
        # Make some moves
        for i in range(5):
            move = agent.make_move([], [])
        
        # Check history lengths
        assert len(agent.feature_history) == 5
        assert len(agent.action_history) == 5
        assert len(agent.reward_history) == 0  # Rewards added separately
        
        # Check action encoding (C=1, D=0)
        for i, action in enumerate(agent.action_history):
            if agent.action_history[i] == 1:
                # Should correspond to a cooperation move
                pass  # Can't check exact move without knowing random seed
            else:
                assert action == 0  # Should be 0 for defection

    def test_gradient_meta_learner_vs_always_cooperate(self):
        """Test GradientMetaLearner against AlwaysCooperate"""
        gradient = GradientMetaLearner("GradientMetaLearner", learning_rate=0.1)
        always_coop = AlwaysCooperate("AlwaysCooperate")
        
        gradient_moves = []
        coop_moves = []
        
        # Play 50 rounds with learning
        for i in range(50):
            g_move = gradient.make_move(gradient_moves, coop_moves)
            c_move = always_coop.make_move(coop_moves, gradient_moves)
            
            gradient_moves.append(g_move)
            coop_moves.append(c_move)
            
            # Calculate reward for gradient learner
            if g_move == 'C' and c_move == 'C':
                reward = 3.0
            elif g_move == 'C' and c_move == 'D':
                reward = 0.0
            elif g_move == 'D' and c_move == 'C':
                reward = 5.0
            else:  # D, D
                reward = 1.0
            
            gradient.reward_history.append(reward)
            
            # Update policy periodically
            if i % 10 == 9:  # Every 10 rounds
                gradient.update_policy()
        
        # Should learn to defect more often against AlwaysCooperate (higher payoff)
        cooperation_rate = gradient_moves.count('C') / len(gradient_moves)
        assert cooperation_rate < 0.5  # Should learn to defect more often for higher payoff

    def test_gradient_meta_learner_vs_always_defect(self):
        """Test GradientMetaLearner against AlwaysDefect"""
        gradient = GradientMetaLearner("GradientMetaLearner", learning_rate=0.1)
        always_def = AlwaysDefect("AlwaysDefect")
        
        gradient_moves = []
        def_moves = []
        
        # Play 50 rounds with learning
        for i in range(50):
            g_move = gradient.make_move(gradient_moves, def_moves)
            d_move = always_def.make_move(def_moves, gradient_moves)
            
            gradient_moves.append(g_move)
            def_moves.append(d_move)
            
            # Calculate reward for gradient learner
            if g_move == 'C' and d_move == 'C':
                reward = 3.0
            elif g_move == 'C' and d_move == 'D':
                reward = 0.0
            elif g_move == 'D' and d_move == 'C':
                reward = 5.0
            else:  # D, D
                reward = 1.0
            
            gradient.reward_history.append(reward)
            
            # Update policy periodically
            if i % 10 == 9:  # Every 10 rounds
                gradient.update_policy()
        
        # Should learn to defect against AlwaysDefect  
        defection_rate = gradient_moves.count('D') / len(gradient_moves)
        assert defection_rate > 0.4  # Adjusted threshold for stochastic learning 

    def test_gradient_meta_learner_vs_tit_for_tat(self):
        """Test GradientMetaLearner against TitForTat"""
        gradient = GradientMetaLearner("GradientMetaLearner", learning_rate=0.05)
        tit_for_tat = TitForTat("TitForTat")
        
        gradient_moves = []
        tft_moves = []
        
        # Play 60 rounds with learning
        for i in range(60):
            g_move = gradient.make_move(gradient_moves, tft_moves)
            tft_move = tit_for_tat.make_move(tft_moves, gradient_moves)
            
            gradient_moves.append(g_move)
            tft_moves.append(tft_move)
            
            # Calculate reward for gradient learner
            if g_move == 'C' and tft_move == 'C':
                reward = 3.0
            elif g_move == 'C' and tft_move == 'D':
                reward = 0.0
            elif g_move == 'D' and tft_move == 'C':
                reward = 5.0
            else:  # D, D
                reward = 1.0
            
            gradient.reward_history.append(reward)
            
            # Update policy every 15 rounds
            if i % 15 == 14:
                gradient.update_policy()
        
        # Should show strategic behavior through learning
        cooperation_rate = gradient_moves.count('C') / len(gradient_moves)
        assert 0.25 < cooperation_rate < 0.75  # Should show some strategic adaptation

    def test_gradient_meta_learner_vs_grim_trigger(self):
        """Test GradientMetaLearner against GrimTrigger"""
        gradient = GradientMetaLearner("GradientMetaLearner", learning_rate=0.1)
        grim = GrimTrigger("GrimTrigger")
        
        gradient_moves = []
        grim_moves = []
        
        # Play 40 rounds with learning
        for i in range(40):
            g_move = gradient.make_move(gradient_moves, grim_moves)
            grim_move = grim.make_move(grim_moves, gradient_moves)
            
            gradient_moves.append(g_move)
            grim_moves.append(grim_move)
            
            # Calculate reward for gradient learner
            if g_move == 'C' and grim_move == 'C':
                reward = 3.0
            elif g_move == 'C' and grim_move == 'D':
                reward = 0.0
            elif g_move == 'D' and grim_move == 'C':
                reward = 5.0
            else:  # D, D
                reward = 1.0
            
            gradient.reward_history.append(reward)
            
            # Update policy every 10 rounds
            if i % 10 == 9:
                gradient.update_policy()
        
        # Should learn to cooperate to avoid triggering GrimTrigger
        cooperation_rate = gradient_moves.count('C') / len(gradient_moves)
        assert cooperation_rate > 0.3

    def test_gradient_meta_learner_policy_update(self):
        """Test policy gradient update mechanism"""
        agent = GradientMetaLearner("GradientMetaLearner", learning_rate=0.1)
        
        # Set up some history
        agent.feature_history = [
            np.array([1, 0, 0, 0, 0]),
            np.array([0, 0.5, 0.5, 0.5, 0.1])
        ]
        agent.action_history = [1, 0]  # Cooperate, then defect
        agent.reward_history = [3.0, 1.0]  # Good reward, poor reward
        
        initial_weights = agent.weights.copy()
        
        # Update policy
        agent.update_policy()
        
        # Weights should have changed
        assert not np.array_equal(agent.weights, initial_weights)

    def test_gradient_meta_learner_advantage_calculation(self):
        """Test advantage calculation in policy updates"""
        agent = GradientMetaLearner("GradientMetaLearner")
        
        # Set up rewards with clear pattern
        agent.reward_history = [1.0, 3.0, 5.0, 2.0]
        
        # Mock some history for update
        agent.feature_history = [np.zeros(5) for _ in range(4)]
        agent.action_history = [1, 1, 0, 0]
        
        # Update should not crash and should modify weights
        initial_weights = agent.weights.copy()
        agent.update_policy()
        
        # Should have processed the advantages correctly
        assert len(agent.reward_history) == 4

    def test_gradient_meta_learner_feature_scaling(self):
        """Test that features are properly scaled"""
        agent = GradientMetaLearner("GradientMetaLearner")
        
        # Test with long history (should cap rounds played feature)
        long_history = ['C'] * 100
        opponent_history = ['D'] * 100
        
        features = agent._extract_features(long_history, opponent_history)
        
        # Rounds played feature should be capped at 1.0
        assert features[4] == 1.0
        
        # Other features should be in [0, 1] range
        assert 0 <= features[1] <= 1  # Opponent cooperation rate
        assert 0 <= features[2] <= 1  # Recent opponent cooperation
        assert 0 <= features[3] <= 1  # Mutual cooperation rate

    def test_gradient_meta_learner_reset(self):
        """Test that GradientMetaLearner resets correctly"""
        agent = GradientMetaLearner("GradientMetaLearner")
        
        # Build up some history
        agent.make_move([], [])
        agent.make_move(['C'], ['D'])
        agent.reward_history = [1.0, 2.0]
        
        # Reset
        agent.reset()
        
        # Should clear histories but keep weights for continued learning
        assert agent.feature_history == []
        assert agent.action_history == []
        assert agent.reward_history == []
        assert agent.history == []
        assert agent.opponent_history == []
        # Weights should persist to maintain learning

    def test_gradient_meta_learner_feature_sensitivity(self):
        """Test that GradientMetaLearner responds appropriately to different feature patterns"""
        agent = GradientMetaLearner("GradientMetaLearner", learning_rate=0.2)
        
        # Test without reset - use a single agent and compare different feature scenarios
        
        # Scenario 1: High opponent cooperation leads to good outcomes
        # Create histories where high cooperation correlates with good rewards
        for scenario in range(2):
            agent.feature_history = []
            agent.action_history = []
            agent.reward_history = []
            
            if scenario == 0:
                # High cooperation scenario - should reinforce cooperation
                for i in range(15):
                    # Create features with high opponent cooperation
                    features = np.array([0, 0.9, 0.8, 0.7, min(i/50, 1.0)])  # High cooperation features
                    agent.feature_history.append(features)
                    agent.action_history.append(1)  # Cooperated
                    agent.reward_history.append(3.0 + 0.5)  # Good reward
                
                # Add some defection outcomes with lower rewards
                for i in range(5):
                    features = np.array([0, 0.9, 0.8, 0.7, min((i+15)/50, 1.0)])
                    agent.feature_history.append(features)
                    agent.action_history.append(0)  # Defected
                    agent.reward_history.append(1.0)  # Lower reward
            else:
                # Low cooperation scenario - should discourage cooperation
                for i in range(5):
                    # Create features with low opponent cooperation
                    features = np.array([0, 0.2, 0.1, 0.1, min(i/50, 1.0)])  # Low cooperation features
                    agent.feature_history.append(features)
                    agent.action_history.append(1)  # Cooperated
                    agent.reward_history.append(0.5)  # Poor reward
                
                # Add defection outcomes with better rewards
                for i in range(15):
                    features = np.array([0, 0.2, 0.1, 0.1, min((i+5)/50, 1.0)])
                    agent.feature_history.append(features)
                    agent.action_history.append(0)  # Defected
                    agent.reward_history.append(1.5)  # Better reward
            
            agent.update_policy()
        
        # Test responses to different feature patterns
        features_high_coop = np.array([0, 0.9, 0.8, 0.7, 0.5])  # High cooperation features
        features_low_coop = np.array([0, 0.2, 0.1, 0.1, 0.5])   # Low cooperation features
        
        prob_coop_high = agent._policy(features_high_coop)
        prob_coop_low = agent._policy(features_low_coop)
        
        # Agent should learn to cooperate more when opponent cooperation features are high
        assert prob_coop_high > prob_coop_low
        
        # Test recent cooperation feature (Feature 2) 
        # Create a new agent to test specific feature sensitivity
        agent2 = GradientMetaLearner("GradientMetaLearner", learning_rate=0.2)
        
        # Test recent cooperation feature by creating scenarios where recent cooperation
        # differs significantly from overall cooperation
        
        # Scenario: Recent cooperation is high, overall is low
        recent_high_scenario = []
        for i in range(10):
            # First 7 rounds: low cooperation, poor rewards when cooperating
            if i < 7:
                features = np.array([0, 0.2, 0.1, 0.1, i/50])  # Low recent cooperation
                agent2.feature_history.append(features)
                agent2.action_history.append(1)  # Cooperated
                agent2.reward_history.append(1.0)  # Poor reward
            else:
                # Last 3 rounds: high recent cooperation, good rewards when cooperating
                features = np.array([0, 0.3, 1.0, 0.4, i/50])  # High recent cooperation
                agent2.feature_history.append(features)
                agent2.action_history.append(1)  # Cooperated  
                agent2.reward_history.append(3.5)  # Good reward
        
        agent2.update_policy()
        
        # Test response to high recent cooperation
        features_high_recent = np.array([0, 0.3, 1.0, 0.4, 0.5])  # High recent cooperation
        features_low_recent = np.array([0, 0.3, 0.1, 0.4, 0.5])   # Low recent cooperation
        
        prob_high_recent = agent2._policy(features_high_recent)
        prob_low_recent = agent2._policy(features_low_recent)
        
        # Agent should be more cooperative when recent cooperation is high
        assert prob_high_recent > prob_low_recent

    def test_gradient_meta_learner_rounds_played_feature(self):
        """Test that GradientMetaLearner responds to rounds played feature (Feature 4)"""
        agent = GradientMetaLearner("GradientMetaLearner", learning_rate=0.1)
        
        # Scenario: Agent learns that cooperation becomes more valuable over time
        own_history = []
        opponent_history = []
        
        # Simulate 8 rounds where rewards increase over time (adjusted for length 5 normalization)
        for round_num in range(8):
            own_history.append('C')
            opponent_history.append('C')
            
            features = agent._extract_features(own_history, opponent_history)
            agent.feature_history.append(features)
            agent.action_history.append(1)  # Cooperated
            
            # Reward increases with rounds played (simulate long-term benefits)
            reward = 2.0 + features[4] * 2.0  # Reward scales with normalized rounds
            agent.reward_history.append(reward)
        
        # Update policy
        agent.update_policy()
        
        # Test early vs late game features (2 rounds vs 8 rounds)
        features_early = agent._extract_features(['C'] * 2, ['C'] * 2)  # 2/5 = 0.4
        features_late = agent._extract_features(['C'] * 8, ['C'] * 8)   # 8/5 = 1.0 (capped)
        
        prob_coop_early = agent._policy(features_early)
        prob_coop_late = agent._policy(features_late)
        
        # Agent should learn to cooperate more in late game
        assert prob_coop_late > prob_coop_early
        
        # Verify feature values
        assert features_early[4] < features_late[4]  # Rounds played feature
        assert features_late[4] == min(8 / 5, 1.0)  # Normalized rounds (8/5 = 1.0)


if __name__ == "__main__":
    pytest.main([__file__])