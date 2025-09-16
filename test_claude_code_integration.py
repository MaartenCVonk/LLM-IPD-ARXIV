#!/usr/bin/env python3
"""
Test script for ClaudeCodeAgent integration
"""
import sys
import os
import time

# Add the parent directory to the path so we can import ipd_suite
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ipd_suite.agents import ClaudeCodeAgent


def test_claude_code_agent():
    """Test ClaudeCodeAgent with Claude Code SDK"""
    print("="*60)
    print("CLAUDE CODE AGENT INTEGRATION TEST")
    print("="*60)

    try:
        # Create agent - no API key required!
        agent = ClaudeCodeAgent(
            name="TestClaudeCode",
            model="claude-code",
            temperature=0.5,
            termination_prob=0.25
        )

        print(f"✓ Created ClaudeCodeAgent: {agent.name}")
        print(f"  Model: {agent.model}")
        print(f"  Temperature: {agent.temperature}")
        print(f"  Termination probability: {agent.termination_prob}")

        # Test initial state
        assert agent.api_calls == 0
        assert agent.total_tokens == 0
        print("✓ Initial state verified (0 API calls, 0 tokens)")

        # Test 1: Simple API call
        print("\n🧪 Test 1: Basic API call with history ['C'], ['D']")
        start_time = time.time()
        move = agent.make_move(['C'], ['D'])
        end_time = time.time()

        # Verify the call was made
        assert agent.api_calls == 1
        assert agent.total_tokens > 0
        assert move in ['C', 'D']

        time_taken = end_time - start_time
        print(f"✓ Move: {move}")
        print(f"✓ API calls: {agent.api_calls}")
        print(f"✓ Total tokens: {agent.total_tokens}")
        print(f"✓ Time taken: {time_taken:.2f} seconds")

        if hasattr(agent, 'last_reasoning') and agent.last_reasoning:
            reasoning_preview = agent.last_reasoning[:200] + "..." if len(agent.last_reasoning) > 200 else agent.last_reasoning
            print(f"✓ Reasoning: {reasoning_preview}")
        else:
            print("ℹ️  No reasoning attribute or reasoning captured")

        # Test 2: Long query with match history
        print("\n🧪 Test 2: Long query with match history")

        # Add mock match history
        agent.match_history = [
            {'opponent': 'Opponent_001', 'rounds': [{'your_move': 'C', 'opponent_move': 'D'}]},
            {'opponent': 'Opponent_002', 'rounds': [{'your_move': 'D', 'opponent_move': 'C'}]}
        ]

        long_own_history = ['C', 'D'] * 10  # 20 rounds
        long_opp_history = ['D', 'C'] * 10  # 20 rounds

        start_time = time.time()
        move2 = agent.make_move(long_own_history, long_opp_history)
        end_time = time.time()

        assert agent.api_calls == 2
        assert move2 in ['C', 'D']

        time_taken = end_time - start_time
        print(f"✓ Move: {move2}")
        print(f"✓ Time taken: {time_taken:.2f} seconds")
        print(f"✓ Total API calls: {agent.api_calls}")
        print(f"✓ Total tokens: {agent.total_tokens}")

        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("✅ ClaudeCodeAgent is working correctly with Claude Code SDK")
        print("="*60)

        return True

    except ImportError as e:
        print(f"❌ IMPORT ERROR: {e}")
        print("Make sure claude-code-sdk is installed: pip install claude-code-sdk")
        return False
    except Exception as e:
        print(f"\n❌ ERROR during testing: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        print("Full traceback:")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_claude_code_agent()
    exit_code = 0 if success else 1
    exit(exit_code)