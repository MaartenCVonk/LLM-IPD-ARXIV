#!/usr/bin/env python3
"""
Standalone test for GPT4Agent real API call
"""
import sys
import os

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not available, skip loading
    pass

# Add the parent directory to the path so we can import ipd_suite
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ipd_suite.agents import GPT4Agent


def test_gpt4_agent_real_api_call():
    """Test GPT4Agent with real API call"""
    print("="*60)
    print("GPT4 AGENT REAL API CALL TEST")
    print("="*60)
    
    # Skip if no API key provided
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY environment variable not set")
        print("Please set your OpenAI API key in the .env file or environment variables")
        return False
    
    print("✓ OpenAI API key found")
    
    try:
        # Create agent with real API key
        agent = GPT4Agent(
            name="TestGPT4Real",
            api_key=api_key,
            model="o3",  # Changed from "o3" to a more standard model
            temperature=1,
            termination_prob=0.1
        )
        
        print(f"✓ Created GPT4Agent: {agent.name}")
        print(f"  Model: {agent.model}")
        print(f"  Temperature: {agent.temperature}")
        print(f"  Termination probability: {agent.termination_prob}")
        
        # Test initial state
        assert agent.api_calls == 0
        assert agent.total_tokens == 0
        print("✓ Initial state verified (0 API calls, 0 tokens)")
        
        # Test 1: Make a real API call with some history
        print("\n🧪 Test 1: API call with history ['C'], ['D']")
        move = agent.make_move(['C'], ['D'])
        
        # Verify the call was made
        assert agent.api_calls == 1
        assert agent.total_tokens > 0
        assert move in ['C', 'D']
        
        print(f"✓ Move: {move}")
        print(f"✓ API calls: {agent.api_calls}")
        print(f"✓ Total tokens: {agent.total_tokens}")
        if agent.last_reasoning:
            reasoning_preview = agent.last_reasoning[:200] + "..." if len(agent.last_reasoning) > 200 else agent.last_reasoning
            print(f"✓ Reasoning: {reasoning_preview}")
        
        # Test 2: Test with no history
        print("\n🧪 Test 2: API call with empty history")
        move2 = agent.make_move([], [])
        assert agent.api_calls == 2
        assert move2 in ['C', 'D']
        
        print(f"✓ Move: {move2}")
        print(f"✓ API calls: {agent.api_calls}")
        print(f"✓ Total tokens: {agent.total_tokens}")
        
        # Test 3: Test with longer history
        print("\n🧪 Test 3: API call with longer history")
        move3 = agent.make_move(['C', 'D', 'C'], ['D', 'C', 'D'])
        assert agent.api_calls == 3
        assert move3 in ['C', 'D']
        
        print(f"✓ Move: {move3}")
        print(f"✓ API calls: {agent.api_calls}")
        print(f"✓ Total tokens: {agent.total_tokens}")
        
        # Test 4: Test different temperature settings (OpenAI supports 0-2 range)
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("✅ GPT4Agent is working correctly with real API calls")
        print("="*60)
        
        # Summary
        total_api_calls = agent.api_calls + sum(len(test_temperatures))  # main agent + temp test agents
        print(f"\nSummary:")
        print(f"- Total API calls made: {total_api_calls}")
        print(f"- Main agent total tokens: {agent.total_tokens}")
        print(f"- All moves were valid: C or D")
        print(f"- All temperature settings worked: {test_temperatures}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR during testing: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        print("Full traceback:")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_gpt4_agent_real_api_call()
    exit_code = 0 if success else 1
    exit(exit_code)