import pytest
import sys
import os

# Add the parent directory to the path so we can import ipd_suite
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ipd_suite.agents import SoftGrudger, TitForTat, AlwaysDefect, AlwaysCooperate, GrimTrigger


class TestSoftGrudgerAgent:
    """Test suite for SoftGrudger agent behavior"""

    def test_soft_grudger_initial_cooperation(self):
        """Test that SoftGrudger cooperates initially"""
        sg = SoftGrudger("SoftGrudger")
        
        # Should cooperate on first move
        move = sg.make_move([], [])
        assert move == 'C'
        
        # Should continue cooperating if opponent cooperates
        move = sg.make_move(['C'], ['C'])
        assert move == 'C'

    def test_soft_grudger_vs_always_cooperate(self):
        """Test SoftGrudger against AlwaysCooperate (should always cooperate)"""
        sg = SoftGrudger("SoftGrudger")
        always_coop = AlwaysCooperate("AlwaysCooperate")
        
        sg_moves = []
        coop_moves = []
        
        # Play 20 rounds
        for i in range(20):
            sg_move = sg.make_move(sg_moves, coop_moves)
            coop_move = always_coop.make_move(coop_moves, sg_moves)
            
            sg_moves.append(sg_move)
            coop_moves.append(coop_move)
        
        # Should never punish since opponent never defects
        assert not sg.punishing
        assert all(move == 'C' for move in sg_moves)

    def test_soft_grudger_punishment_sequence(self):
        """Test that SoftGrudger executes punishment sequence correctly"""
        sg = SoftGrudger("SoftGrudger")
        
        # Start with cooperation
        assert sg.make_move([], []) == 'C'
        
        # Opponent defects - should start punishment
        move = sg.make_move(['C'], ['D'])
        assert move == 'D'
        assert sg.punishing
        assert sg.punishment_index == 1
        
        # Continue punishment sequence: D-D-D-D-C-C
        expected_sequence = ['D', 'D', 'D', 'C', 'C']
        actual_sequence = []
        
        for i in range(len(expected_sequence)):
            move = sg.make_move(['C'] + actual_sequence, ['D'] * (i + 2))
            actual_sequence.append(move)
        
        assert actual_sequence == expected_sequence
        
        # After punishment, should return to cooperation
        assert not sg.punishing
        assert sg.punishment_index == 0

    def test_soft_grudger_vs_always_defect(self):
        """Test SoftGrudger against AlwaysDefect"""
        sg = SoftGrudger("SoftGrudger")
        always_def = AlwaysDefect("AlwaysDefect")
        
        sg_moves = []
        def_moves = []
        
        # Play multiple rounds to see punishment cycles
        for i in range(15):
            sg_move = sg.make_move(sg_moves, def_moves)
            def_move = always_def.make_move(def_moves, sg_moves)
            
            sg_moves.append(sg_move)
            def_moves.append(def_move)
        
        # Should start with cooperation
        assert sg_moves[0] == 'C'
        
        # Should punish after first defection
        # Expected pattern: C, D, D, D, D, C, C, (repeat punishment if defection continues)
        assert sg_moves[1] == 'D'  # Start punishment
        
        # Should have cycles of punishment
        punishment_moves = sg_moves[1:]
        assert 'D' in punishment_moves  # Should have defection
        assert 'C' in punishment_moves  # Should have cooperation in punishment

    def test_soft_grudger_vs_tit_for_tat(self):
        """Test SoftGrudger against TitForTat"""
        sg = SoftGrudger("SoftGrudger")
        tft = TitForTat("TitForTat")
        
        sg_moves = []
        tft_moves = []
        
        # Play 20 rounds
        for i in range(20):
            sg_move = sg.make_move(sg_moves, tft_moves)
            tft_move = tft.make_move(tft_moves, sg_moves)
            
            sg_moves.append(sg_move)
            tft_moves.append(tft_move)
        
        # Against TitForTat, should mostly cooperate since TFT starts with cooperation
        cooperation_rate = sg_moves.count('C') / len(sg_moves)
        assert cooperation_rate >= 0.7  # Should cooperate most of the time

    def test_soft_grudger_punishment_interruption(self):
        """Test that SoftGrudger can handle interruptions during punishment"""
        sg = SoftGrudger("SoftGrudger")
        
        # Start punishment
        sg.make_move([], [])  # C
        sg.make_move(['C'], ['D'])  # D (start punishment)
        sg.make_move(['C', 'D'], ['D', 'D'])  # D
        
        # Should be in punishment mode
        assert sg.punishing
        assert sg.punishment_index == 2
        
        # If opponent cooperates, continue punishment sequence
        move = sg.make_move(['C', 'D', 'D'], ['D', 'D', 'C'])
        assert move == 'D'  # Still in punishment
        
        # Continue punishment regardless of opponent's moves
        move = sg.make_move(['C', 'D', 'D', 'D'], ['D', 'D', 'C', 'C'])
        assert move == 'C'  # Should be at cooperation phase of punishment

    def test_soft_grudger_multiple_punishment_cycles(self):
        """Test SoftGrudger with multiple punishment cycles"""
        sg = SoftGrudger("SoftGrudger")
        
        moves = []
        opponent_moves = []
        
        # First cycle: cooperate, then opponent defects
        move1 = sg.make_move(moves, opponent_moves)
        moves.append(move1)
        opponent_moves.append('C')
        assert move1 == 'C'
        
        # Opponent defects, start first punishment
        move2 = sg.make_move(moves, opponent_moves)
        moves.append(move2)
        opponent_moves.append('D')
        assert move2 == 'D'
        
        # Complete first punishment cycle
        for i in range(5):  # D-D-D-D-C-C remaining
            move = sg.make_move(moves, opponent_moves)
            moves.append(move)
            opponent_moves.append('D')
        
        # After punishment, should return to cooperation
        assert not sg.punishing
        
        # If opponent defects again, should start new punishment cycle
        move_new = sg.make_move(moves, opponent_moves)
        moves.append(move_new)
        opponent_moves.append('D')
        
        # Should start new punishment
        assert sg.punishing
        assert sg.punishment_index == 1

    def test_soft_grudger_vs_grim_trigger(self):
        """Test SoftGrudger against GrimTrigger"""
        sg = SoftGrudger("SoftGrudger")
        grim = GrimTrigger("GrimTrigger")
        
        sg_moves = []
        grim_moves = []
        
        # Play multiple rounds
        for i in range(15):
            sg_move = sg.make_move(sg_moves, grim_moves)
            grim_move = grim.make_move(grim_moves, sg_moves)
            
            sg_moves.append(sg_move)
            grim_moves.append(grim_move)
        
        # Both should start cooperating
        assert sg_moves[0] == 'C'
        assert grim_moves[0] == 'C'
        
        # Should maintain cooperation since neither defects first
        cooperation_rate = sg_moves.count('C') / len(sg_moves)
        assert cooperation_rate >= 0.8

    def test_soft_grudger_reset(self):
        """Test that SoftGrudger resets properly"""
        sg = SoftGrudger("SoftGrudger")
        
        # Start punishment
        sg.make_move([], [])
        sg.make_move(['C'], ['D'])
        
        # Should be in punishment mode
        assert sg.punishing
        assert sg.punishment_index > 0
        
        # Reset
        sg.reset()
        
        # Should be clean
        assert not sg.punishing
        assert sg.punishment_index == 0
        assert sg.history == []
        assert sg.opponent_history == []

    def test_soft_grudger_punishment_sequence_exact(self):
        """Test the exact punishment sequence D-D-D-D-C-C"""
        sg = SoftGrudger("SoftGrudger")
        
        # Initial cooperation
        move0 = sg.make_move([], [])
        assert move0 == 'C'
        
        # Opponent defects, start punishment
        move1 = sg.make_move(['C'], ['D'])
        assert move1 == 'D'
        assert sg.punishment_index == 1
        
        # Continue punishment sequence
        expected_punishment = ['D', 'D', 'D', 'C', 'C']
        actual_punishment = []
        
        for i in range(len(expected_punishment)):
            move = sg.make_move(['C', 'D'] + actual_punishment, ['D'] * (i + 2))
            actual_punishment.append(move)
        
        assert actual_punishment == expected_punishment
        
        # After punishment, should return to normal cooperation
        final_move = sg.make_move(['C', 'D'] + actual_punishment, ['D'] * 7)
        assert final_move == 'C'
        assert not sg.punishing

    def test_soft_grudger_gradual_response(self):
        """Test that SoftGrudger's response is gradual and measured"""
        sg = SoftGrudger("SoftGrudger")
        
        # Track punishment pattern
        moves = []
        opponent_moves = ['C', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'C', 'C']
        
        for i in range(len(opponent_moves)):
            move = sg.make_move(moves, opponent_moves[:i])
            moves.append(move)
        
        # Should start with cooperation
        assert moves[0] == 'C'
        
        # Should punish but then offer cooperation at end of sequence
        # Pattern should be: C, D, D, D, D, C, C, (new punishment if defection continues)
        assert moves[1] == 'D'  # Start punishment
        assert 'C' in moves[5:7]  # Should have cooperation in punishment sequence
        
        # Should be measured - not permanent retaliation like GrimTrigger
        cooperation_in_punishment = moves[4:7].count('C')
        assert cooperation_in_punishment >= 1  # Should offer cooperation


if __name__ == "__main__":
    pytest.main([__file__])