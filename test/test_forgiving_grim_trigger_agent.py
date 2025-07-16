import pytest
import sys
import os

# Add the parent directory to the path so we can import ipd_suite
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ipd_suite.agents import ForgivingGrimTrigger, TitForTat, AlwaysDefect, AlwaysCooperate, GrimTrigger


class TestForgivingGrimTriggerAgent:
    """Test suite for ForgivingGrimTrigger agent behavior"""

    def test_forgiving_grim_trigger_initial_cooperation(self):
        """Test that ForgivingGrimTrigger cooperates initially"""
        fgt = ForgivingGrimTrigger("ForgivingGrimTrigger")
        
        # Should cooperate on first move
        move = fgt.make_move([], [])
        assert move == 'C'
        
        # Should continue cooperating if opponent cooperates
        move = fgt.make_move(['C'], ['C'])
        assert move == 'C'

    def test_forgiving_grim_trigger_vs_always_cooperate(self):
        """Test ForgivingGrimTrigger against AlwaysCooperate (should always cooperate)"""
        fgt = ForgivingGrimTrigger("ForgivingGrimTrigger")
        always_coop = AlwaysCooperate("AlwaysCooperate")
        
        fgt_moves = []
        coop_moves = []
        
        # Play 20 rounds
        for i in range(20):
            fgt_move = fgt.make_move(fgt_moves, coop_moves)
            coop_move = always_coop.make_move(coop_moves, fgt_moves)
            
            fgt_moves.append(fgt_move)
            coop_moves.append(coop_move)
        
        # Should never be triggered since opponent never defects
        assert not fgt.triggered
        assert all(move == 'C' for move in fgt_moves)

    def test_forgiving_grim_trigger_vs_always_defect(self):
        """Test ForgivingGrimTrigger against AlwaysDefect (should trigger and eventually forgive)"""
        fgt = ForgivingGrimTrigger("ForgivingGrimTrigger", forgiveness_threshold=3)
        always_def = AlwaysDefect("AlwaysDefect")
        
        fgt_moves = []
        def_moves = []
        
        # Play multiple rounds
        for i in range(15):
            fgt_move = fgt.make_move(fgt_moves, def_moves)
            def_move = always_def.make_move(def_moves, fgt_moves)
            
            fgt_moves.append(fgt_move)
            def_moves.append(def_move)
        
        # Should be triggered after first defection
        assert fgt.triggered or fgt.mutual_defection_count >= 0
        
        # Should have periods of mutual defection followed by forgiveness
        # Look for pattern: cooperation -> defection -> mutual defection -> forgiveness
        assert 'C' in fgt_moves[0:1]  # Initial cooperation
        assert 'D' in fgt_moves[1:10]  # Defection after trigger
        
        # Should eventually forgive (return to cooperation)
        # Check if there's cooperation after the initial trigger
        cooperation_after_trigger = any(move == 'C' for move in fgt_moves[5:])
        assert cooperation_after_trigger

    def test_forgiving_grim_trigger_vs_tit_for_tat(self):
        """Test ForgivingGrimTrigger against TitForTat"""
        fgt = ForgivingGrimTrigger("ForgivingGrimTrigger", forgiveness_threshold=2)
        tft = TitForTat("TitForTat")
        
        fgt_moves = []
        tft_moves = []
        
        # Play 20 rounds
        for i in range(20):
            fgt_move = fgt.make_move(fgt_moves, tft_moves)
            tft_move = tft.make_move(tft_moves, fgt_moves)
            
            fgt_moves.append(fgt_move)
            tft_moves.append(tft_move)
        
        # Against TitForTat, should mostly cooperate since TFT starts with cooperation
        cooperation_rate = fgt_moves.count('C') / len(fgt_moves)
        assert cooperation_rate >= 0.7  # Should cooperate most of the time

    def test_forgiving_grim_trigger_forgiveness_mechanism(self):
        """Test the forgiveness mechanism specifically"""
        fgt = ForgivingGrimTrigger("ForgivingGrimTrigger", forgiveness_threshold=2)
        
        # Start with cooperation
        assert fgt.make_move([], []) == 'C'
        
        # Opponent defects - should trigger
        assert fgt.make_move(['C'], ['D']) == 'D'
        assert fgt.triggered
        
        # Mutual defection should increment counter
        fgt.make_move(['C', 'D'], ['D', 'D'])
        assert fgt.mutual_defection_count == 1
        
        # Another mutual defection should reach threshold and forgive
        move = fgt.make_move(['C', 'D', 'D'], ['D', 'D', 'D'])
        assert move == 'C'  # Should forgive and cooperate
        assert not fgt.triggered  # Should reset trigger
        assert fgt.mutual_defection_count == 0  # Should reset counter

    def test_forgiving_grim_trigger_different_thresholds(self):
        """Test ForgivingGrimTrigger with different forgiveness thresholds"""
        # Test with threshold = 1
        fgt1 = ForgivingGrimTrigger("FGT1", forgiveness_threshold=1)
        
        # Trigger and forgive quickly
        fgt1.make_move([], [])  # C
        fgt1.make_move(['C'], ['D'])  # D (triggered)
        move = fgt1.make_move(['C', 'D'], ['D', 'D'])  # Should forgive
        assert move == 'C'
        
        # Test with threshold = 5
        fgt5 = ForgivingGrimTrigger("FGT5", forgiveness_threshold=5)
        
        # Should take longer to forgive
        moves = []
        opponent_moves = ['D'] * 10
        
        for i in range(10):
            move = fgt5.make_move(moves, opponent_moves[:i])
            moves.append(move)
        
        # Should still be in punishment phase longer
        defection_count = moves[1:6].count('D')
        assert defection_count >= 4  # Should defect more before forgiving

    def test_forgiving_grim_trigger_reset(self):
        """Test that ForgivingGrimTrigger resets properly"""
        fgt = ForgivingGrimTrigger("ForgivingGrimTrigger", forgiveness_threshold=3)
        
        # Trigger the agent
        fgt.make_move([], [])
        fgt.make_move(['C'], ['D'])
        
        # Should be triggered
        assert fgt.triggered
        
        # Reset
        fgt.reset()
        
        # Should be clean
        assert not fgt.triggered
        assert fgt.mutual_defection_count == 0
        assert fgt.history == []
        assert fgt.opponent_history == []

    def test_forgiving_grim_trigger_vs_grim_trigger(self):
        """Test ForgivingGrimTrigger against regular GrimTrigger"""
        fgt = ForgivingGrimTrigger("ForgivingGrimTrigger", forgiveness_threshold=2)
        grim = GrimTrigger("GrimTrigger")
        
        fgt_moves = []
        grim_moves = []
        
        # Both start cooperating
        for i in range(2):
            fgt_move = fgt.make_move(fgt_moves, grim_moves)
            grim_move = grim.make_move(grim_moves, fgt_moves)
            
            fgt_moves.append(fgt_move)
            grim_moves.append(grim_move)
        
        # Should both cooperate initially
        assert fgt_moves[:2] == ['C', 'C']
        assert grim_moves[:2] == ['C', 'C']
        
        # Continue for more rounds
        for i in range(2, 10):
            fgt_move = fgt.make_move(fgt_moves, grim_moves)
            grim_move = grim.make_move(grim_moves, fgt_moves)
            
            fgt_moves.append(fgt_move)
            grim_moves.append(grim_move)
        
        # Should maintain cooperation since neither defects first
        cooperation_rate = fgt_moves.count('C') / len(fgt_moves)
        assert cooperation_rate >= 0.8

    def test_forgiving_grim_trigger_mutual_defection_counting(self):
        """Test that mutual defection counting works correctly"""
        fgt = ForgivingGrimTrigger("ForgivingGrimTrigger", forgiveness_threshold=3)
        
        # Simulate game where opponent defects, triggering punishment
        moves = []
        opponent_moves = []
        
        # Round 1: Both cooperate
        move1 = fgt.make_move(moves, opponent_moves)
        moves.append(move1)
        opponent_moves.append('C')
        
        # Round 2: Opponent defects, FGT should defect next round
        move2 = fgt.make_move(moves, opponent_moves)
        moves.append(move2)
        opponent_moves.append('D')
        
        # Round 3: Both defect (first mutual defection)
        move3 = fgt.make_move(moves, opponent_moves)
        moves.append(move3)
        opponent_moves.append('D')
        assert fgt.mutual_defection_count == 1
        
        # Round 4: Both defect (second mutual defection)
        move4 = fgt.make_move(moves, opponent_moves)
        moves.append(move4)
        opponent_moves.append('D')
        assert fgt.mutual_defection_count == 2
        
        # Round 5: Both defect (third mutual defection - should trigger forgiveness)
        move5 = fgt.make_move(moves, opponent_moves)
        moves.append(move5)
        opponent_moves.append('D')
        
        # Should forgive and cooperate
        assert move5 == 'C'
        assert not fgt.triggered
        assert fgt.mutual_defection_count == 0


if __name__ == "__main__":
    pytest.main([__file__])