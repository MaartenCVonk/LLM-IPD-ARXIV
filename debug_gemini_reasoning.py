#!/usr/bin/env python3
"""
Debug script to check Gemini reasoning capture
"""
import sys
import os

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Add the parent directory to the path so we can import ipd_suite
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ipd_suite.agents import GeminiAgent


def debug_gemini_reasoning():
    """Debug Gemini agent reasoning capture"""
    print("="*60)
    print("DEBUG: GEMINI REASONING CAPTURE")
    print("="*60)
    
    api_key = os.environ.get('GOOGLE_API_KEY')
    if not api_key:
        print("❌ GOOGLE_API_KEY not found")
        return
    
    print("✓ API key found")
    
    try:
        agent = GeminiAgent(
            name="DebugGemini",
            api_key=api_key,
            model="gemini-1.5-flash",  # Using simpler model for debugging
            temperature=0.7,
            termination_prob=0.1
        )
        
        print(f"✓ Created agent: {agent.name}")
        print(f"  Model: {agent.model}")
        
        # Test the prompt creation
        prompt = agent._create_prompt(['C'], ['D'])
        print(f"\n📝 PROMPT BEING SENT:")
        print("-" * 40)
        print(prompt)
        print("-" * 40)
        
        # Make a move and capture the API response
        print(f"\n🔍 MAKING API CALL...")
        
        # Manually call the API to see raw response
        try:
            raw_response = agent._call_api(prompt)
            print(f"\n📤 RAW API RESPONSE:")
            print("-" * 40)
            print(repr(raw_response))  # Use repr to see exact string
            print("-" * 40)
            print("Raw response:")
            print(raw_response)
            print("-" * 40)
            
        except Exception as e:
            print(f"❌ Raw API call failed: {e}")
            return
        
        # Now test the full make_move method
        print(f"\n🎯 TESTING FULL make_move METHOD:")
        move = agent.make_move(['C'], ['D'])
        
        print(f"Move returned: {move}")
        print(f"last_reasoning type: {type(agent.last_reasoning)}")
        print(f"last_reasoning length: {len(agent.last_reasoning) if agent.last_reasoning else 0}")
        print(f"last_reasoning content:")
        print("-" * 40)
        if agent.last_reasoning:
            print(repr(agent.last_reasoning))  # Use repr to see exact content
            print("-" * 40)
            print(agent.last_reasoning)
        else:
            print("None")
        print("-" * 40)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    debug_gemini_reasoning()