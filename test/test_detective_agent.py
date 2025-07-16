import pytest
import sys
import os

# Add the parent directory to the path so we can import ipd_suite
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ipd_suite.agents import Detective, TitForTat, AlwaysDefect, AlwaysCooperate, GrimTrigger


class TestDetectiveAgent:
    """Test suite for Detective agent behavior"""

    def test_detective_test_sequence(self):
        """Test that Detective executes its test sequence correctly"""
        detective = Detective("Detective")
        
        # Test sequence should be C-D-C-C
        expected_sequence = ['C', 'D', 'C', 'C']
        actual_sequence = []
        
        for i in range(4):
            move = detective.make_move(actual_sequence, ['C'] * i)
            actual_sequence.append(move)
        
        assert actual_sequence == expected_sequence

    def test_detective_vs_always_cooperate(self):
        """Test Detective against AlwaysCooperate (should classify as sucker)"""
        detective = Detective("Detective")
        always_coop = AlwaysCooperate("AlwaysCooperate")
        
        detective_moves = []
        coop_moves = []
        
        # Play 10 rounds
        for i in range(10):
            det_move = detective.make_move(detective_moves, coop_moves)
            coop_move = always_coop.make_move(coop_moves, detective_moves)
            
            detective_moves.append(det_move)
            coop_moves.append(coop_move)
        
        # After test phase, Detective should identify AlwaysCooperate as sucker
        # and exploit by always defecting
        assert detective.opponent_type == 'sucker'
        
        # After round 4, Detective should mostly defect
        post_test_moves = detective_moves[4:]
        defection_rate = post_test_moves.count('D') / len(post_test_moves)
        assert defection_rate == 1  # Should always defect

    def test_detective_vs_tit_for_tat(self):
        """Test Detective against TitForTat (should classify as retaliator)"""
        detective = Detective("Detective")
        tft = TitForTat("TitForTat")
        
        detective_moves = []
        tft_moves = []
        
        # Play 10 rounds
        for i in range(10):
            det_move = detective.make_move(detective_moves, tft_moves)
            tft_move = tft.make_move(tft_moves, detective_moves)
            
            detective_moves.append(det_move)
            tft_moves.append(tft_move)
        
        # Detective should identify TitForTat as retaliator
        assert detective.opponent_type == 'retaliator'
        
        # After test phase, Detective should play TitForTat strategy
        # (copy opponent's last move)
        for i in range(5, 10):
            if i > 0:
                assert detective_moves[i] == tft_moves[i-1]

    def test_detective_vs_always_defect(self):
        """Test Detective against AlwaysDefect (should classify as retaliator since it 'retaliates' to everything)"""
        detective = Detective("Detective")
        always_def = AlwaysDefect("AlwaysDefect")
        
        detective_moves = []
        def_moves = []
        
        # Play 10 rounds
        for i in range(10):
            det_move = detective.make_move(detective_moves, def_moves)
            def_move = always_def.make_move(def_moves, detective_moves)
            
            detective_moves.append(det_move)
            def_moves.append(def_move)
        
        # Detective should classify AlwaysDefect as retaliator (it defects on round 2 when Detective defects)
        assert detective.opponent_type == 'retaliator'

    def test_detective_vs_grim_trigger(self):
        """Test Detective against GrimTrigger (should classify as retaliator)"""
        detective = Detective("Detective")
        grim = GrimTrigger("GrimTrigger")
        
        detective_moves = []
        grim_moves = []
        
        # Play 10 rounds
        for i in range(10):
            det_move = detective.make_move(detective_moves, grim_moves)
            grim_move = grim.make_move(grim_moves, detective_moves)
            
            detective_moves.append(det_move)
            grim_moves.append(grim_move)
        
        # Detective should identify GrimTrigger as retaliator
        # (it retaliates to Detective's defection in round 2)
        assert detective.opponent_type == 'retaliator'

    def test_detective_reset(self):
        """Test that Detective resets properly"""
        detective = Detective("Detective")
        
        # Play a few rounds
        detective.make_move([], [])
        detective.make_move(['C'], ['C'])
        detective.make_move(['C', 'D'], ['C', 'D'])
        
        # Should have some state
        assert len(detective.history) == 0  # history is managed externally
        assert detective.opponent_type is None or detective.opponent_type in ['sucker', 'retaliator', 'random']
        
        # Reset
        detective.reset()
        
        # Should be clean
        assert detective.opponent_type is None
        assert detective.history == []
        assert detective.opponent_history == []

    def test_detective_opponent_classification_logic(self):
        """Test the opponent classification logic directly"""
        detective = Detective("Detective")
        
        # Test sucker classification (cooperates, doesn't retaliate)
        sucker_history = ['C', 'C', 'C', 'C']
        detective._analyze_opponent(sucker_history)
        assert detective.opponent_type == 'sucker'
        
        # Test retaliator classification (retaliates to defection)
        detective.reset()
        retaliator_history = ['C', 'C', 'D', 'C']  # Retaliates in round 3
        detective._analyze_opponent(retaliator_history)
        assert detective.opponent_type == 'retaliator'
        
        # Test random classification (low cooperation, retaliates)
        detective.reset()
        random_history = ['D', 'D', 'D', 'D']
        detective._analyze_opponent(random_history)
        assert detective.opponent_type == 'retaliator'
        
        # Test edge case: insufficient history
        detective.reset()
        short_history = ['C', 'D']
        detective._analyze_opponent(short_history)
        assert detective.opponent_type == 'random'

    def test_detective_mixed_strategy_vs_random(self):
        """Test Detective's mixed strategy against random opponents"""
        detective = Detective("Detective")
        
        # Simulate a random opponent that doesn't fit other categories
        detective_moves = []
        random_moves = ['D', 'C', 'C', 'D']  # Low cooperation, retaliates
        
        # Play first 4 rounds (test phase) - Detective uses test sequence
        for i in range(4):
            det_move = detective.make_move(detective_moves, random_moves[:i])
            detective_moves.append(det_move)
        
        # Verify Detective follows test sequence C-D-C-C
        expected_test_sequence = ['C', 'D', 'C', 'C']
        assert detective_moves[:4] == expected_test_sequence
        
        # After round 4, opponent should be analyzed
        # Make one more move to trigger analysis
        det_move = detective.make_move(detective_moves, random_moves)
        detective_moves.append(det_move)
        
        # Verify opponent is classified as random/retaliator (not sucker)
        assert detective.opponent_type == 'random'
        
        # Continue playing - should use mixed strategy
        for i in range(5, 10):
            det_move = detective.make_move(detective_moves, random_moves + ['C'] * (i-4))
            detective_moves.append(det_move)
        
        # Verify mixed strategy behavior (not all cooperation like with suckers)
        post_test_moves = detective_moves[4:]
        assert len(post_test_moves) > 0
        cooperation_rate = post_test_moves.count('C') / len(post_test_moves)
        defection_rate = post_test_moves.count('D') / len(post_test_moves)
        
        # Should not be pure cooperation (like with suckers) or pure defection
        assert cooperation_rate < 1.0  # Not always cooperating
        assert defection_rate < 1.0    # Not always defecting
        assert cooperation_rate + defection_rate == 1.0  # Only C and D moves


if __name__ == "__main__":
    pytest.main([__file__])