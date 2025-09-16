#!/usr/bin/env python3
"""
Standalone test for ClaudeAgent real API call with timing measurements
"""
import sys
import os
import time

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not available, skip loading
    pass

# Add the parent directory to the path so we can import ipd_suite
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ipd_suite.agents import ClaudeAgent


def test_claude_agent_real_api_call():
    """Test ClaudeAgent with real API call and timing measurements"""
    print("="*60)
    print("CLAUDE AGENT REAL API CALL TEST WITH TIMING")
    print("="*60)

    # Skip if no API key provided
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ ANTHROPIC_API_KEY environment variable not set")
        print("Please set your Anthropic API key in the .env file or environment variables")
        return False

    print("✓ Anthropic API key found")

    try:
        # Create agent with exact model and temperature from run_experiments.py
        agent = ClaudeAgent(
            name="TestClaudeReal",
            api_key=api_key,
            model="claude-sonnet-4-20250514",  # Exact model from run_experiments.py
            temperature=0.5,  # Middle temperature from run_experiments.py [0.2, 0.5, 0.8]
            termination_prob=0.25  # Representative shadow condition
        )

        print(f"✓ Created ClaudeAgent: {agent.name}")
        print(f"  Model: {agent.model}")
        print(f"  Temperature: {agent.temperature}")
        print(f"  Termination probability: {agent.termination_prob}")

        # Test initial state
        assert agent.api_calls == 0
        assert agent.total_tokens == 0
        print("✓ Initial state verified (0 API calls, 0 tokens)")

        # Test 1: Make a real API call with some history
        print("\n🧪 Test 1: API call with history ['C'], ['D']")
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
        print(f"✓ Efficiency: {agent.total_tokens/time_taken:.0f} tokens/second")

        # Check and display reasoning
        if agent.last_reasoning and agent.last_reasoning.strip():
            reasoning_preview = agent.last_reasoning[:200] + "..." if len(agent.last_reasoning) > 200 else agent.last_reasoning
            print(f"✓ Reasoning: {reasoning_preview}")
            print(f"✓ Reasoning length: {len(agent.last_reasoning)} characters")
        else:
            print(f"⚠️  No reasoning captured from Claude agent")

        # Test 2: Test with no history
        print("\n🧪 Test 2: API call with empty history")
        start_time = time.time()
        move2 = agent.make_move([], [])
        end_time = time.time()
        assert agent.api_calls == 2
        assert move2 in ['C', 'D']

        time_taken = end_time - start_time
        print(f"✓ Move: {move2}")
        print(f"✓ API calls: {agent.api_calls}")
        print(f"✓ Total tokens: {agent.total_tokens}")
        print(f"✓ Time taken: {time_taken:.2f} seconds")

        # Test 3: Test with longer history
        print("\n🧪 Test 3: API call with longer history")
        start_time = time.time()
        move3 = agent.make_move(['C', 'D', 'C'], ['D', 'C', 'D'])
        end_time = time.time()
        assert agent.api_calls == 3
        assert move3 in ['C', 'D']

        time_taken = end_time - start_time
        print(f"✓ Move: {move3}")
        print(f"✓ API calls: {agent.api_calls}")
        print(f"✓ Total tokens: {agent.total_tokens}")
        print(f"✓ Time taken: {time_taken:.2f} seconds")

        # Test 3.5: Long representative query test (simulates real IPD scenario)
        print("\n🧪 Test 3.5: Long representative query (20-round history + match history)")
        # Simulate a realistic scenario with long game history and match history
        long_own_history = ['C', 'D', 'C', 'C', 'D', 'D', 'C', 'D', 'C', 'C', 'D', 'C', 'D', 'D', 'C', 'C', 'D', 'C', 'D', 'C']
        long_opp_history = ['D', 'C', 'D', 'C', 'C', 'D', 'D', 'C', 'D', 'D', 'C', 'D', 'C', 'C', 'D', 'D', 'C', 'D', 'C', 'D']

        # Add some mock match history to make it more representative
        agent.match_history = [
            {'opponent': 'Opponent_001', 'rounds': [{'your_move': 'C', 'opponent_move': 'D'}, {'your_move': 'D', 'opponent_move': 'C'}]},
            {'opponent': 'Opponent_002', 'rounds': [{'your_move': 'C', 'opponent_move': 'C'}, {'your_move': 'C', 'opponent_move': 'D'}, {'your_move': 'D', 'opponent_move': 'D'}]}
        ]

        start_time = time.time()
        move_long = agent.make_move(long_own_history, long_opp_history)
        end_time = time.time()

        assert agent.api_calls == 4
        assert move_long in ['C', 'D']

        time_taken_long = end_time - start_time
        prompt_used = agent._create_prompt(long_own_history, long_opp_history)
        estimated_tokens = agent.estimate_tokens(prompt_used)

        print(f"✓ Move: {move_long}")
        print(f"✓ Time taken: {time_taken_long:.2f} seconds")
        print(f"✓ Prompt length: {len(prompt_used)} characters")
        print(f"✓ Estimated tokens: {estimated_tokens}")
        print(f"✓ Processing speed: {estimated_tokens/time_taken_long:.1f} tokens/second")

        if agent.last_reasoning and agent.last_reasoning.strip():
            reasoning_preview = agent.last_reasoning[:200] + "..." if len(agent.last_reasoning) > 200 else agent.last_reasoning
            print(f"✓ Reasoning: {reasoning_preview}")
        else:
            print(f"⚠️  No reasoning captured from long query")

        # Test 4: Test different temperature settings from run_experiments.py
        print("\n🧪 Test 4: Different temperature settings from run_experiments.py")
        test_temperatures = [0.2, 0.5, 0.8]  # Exact temperatures from run_experiments.py

        for temp in test_temperatures:
            print(f"\n  Testing temperature: {temp}")
            temp_agent = ClaudeAgent(
                name=f"TestClaudeTemp{temp}",
                api_key=api_key,
                model="claude-sonnet-4-20250514",
                temperature=temp,
                termination_prob=0.25
            )

            # Verify temperature is set correctly
            assert temp_agent.temperature == temp
            print(f"  ✓ Temperature set: {temp_agent.temperature}")

            # Make API call with this temperature
            start_time = time.time()
            temp_move = temp_agent.make_move(['C'], ['D'])
            end_time = time.time()
            assert temp_move in ['C', 'D']
            assert temp_agent.api_calls == 1

            time_taken = end_time - start_time
            print(f"  ✓ Move with temp {temp}: {temp_move}")
            print(f"  ✓ API calls: {temp_agent.api_calls}")
            print(f"  ✓ Tokens used: {temp_agent.total_tokens}")
            print(f"  ✓ Time taken: {time_taken:.2f} seconds")

            # Check reasoning for temperature test
            if temp_agent.last_reasoning and temp_agent.last_reasoning.strip():
                reasoning_preview = temp_agent.last_reasoning[:100] + "..." if len(temp_agent.last_reasoning) > 100 else temp_agent.last_reasoning
                print(f"  ✓ Reasoning: {reasoning_preview}")
            else:
                print(f"  ⚠️  No reasoning captured")

        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("✅ ClaudeAgent is working correctly with real API calls")
        print("="*60)

        # Summary
        total_api_calls = agent.api_calls + len(test_temperatures)  # main agent + temp test agents
        print(f"\n📊 SUMMARY:")
        print(f"- Total API calls made: {total_api_calls}")
        print(f"- Main agent total tokens: {agent.total_tokens}")
        print(f"- All moves were valid: C or D")
        print(f"- All temperature settings worked: {test_temperatures}")
        print(f"- Model used: {agent.model}")

        # Show final reasoning from main agent
        if agent.last_reasoning and agent.last_reasoning.strip():
            print(f"\n📋 FULL REASONING FROM LAST CALL:")
            print("-" * 50)
            print(agent.last_reasoning)
            print("-" * 50)

        return True

    except Exception as e:
        print(f"\n❌ ERROR during testing: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        print("Full traceback:")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_claude_agent_real_api_call()
    exit_code = 0 if success else 1
    exit(exit_code)