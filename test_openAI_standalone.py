#!/usr/bin/env python3
"""
Standalone test for OpenAI models: gpt-5-mini, gpt-5-nano, and gpt-4.1-mini
"""
import sys
import os
import time

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Add the parent directory to the path so we can import ipd_suite
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ipd_suite.agents import GPT4Agent


def test_openai_models():
    """Test OpenAI models: gpt-5-mini, gpt-5-nano, and gpt-4.1-mini at temperature 1"""
    print("="*60)
    print("OPENAI MODELS TEST - gpt-5-mini, gpt-5-nano, gpt-4.1-mini")
    print("="*60)
    
    # Check API key
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY environment variable not set")
        return False
    
    print("✓ OpenAI API key found")
    
    models = ['gpt-5-mini', 'gpt-5-nano', 'gpt-4.1-mini']
    results = {}
    total_calls = 0
    total_tokens = 0
    
    try:
        for model in models:
            print(f"\n🤖 Testing model: {model}")
            print("-" * 40)
            
            # Create agent
            agent = GPT4Agent(
                name=f"Test_{model.replace('-', '_')}",
                api_key=api_key,
                model=model,
                temperature=1.0,  # OpenAI uses temperature 1.0 for all models in run_experiments.py
                termination_prob=0.25  # Representative shadow condition
            )
            
            # Test scenarios
            scenarios = [
                ([], [], "empty"),
                (['C'], ['D'], "single"),
                (['C', 'D', 'C'], ['D', 'C', 'D'], "multi")
            ]
            
            moves = []
            timings = []
            for my_hist, opp_hist, name in scenarios:
                start_time = time.time()
                move = agent.make_move(my_hist, opp_hist)
                end_time = time.time()
                time_taken = end_time - start_time

                moves.append(move)
                timings.append(time_taken)
                print(f"  {name}: {move} (time: {time_taken:.2f}s)")

            # Long representative query test
            print(f"  🧪 Long query test for {model}:")
            long_own_history = ['C', 'D', 'C', 'C', 'D', 'D', 'C', 'D', 'C', 'C', 'D', 'C', 'D', 'D', 'C', 'C', 'D', 'C', 'D', 'C']
            long_opp_history = ['D', 'C', 'D', 'C', 'C', 'D', 'D', 'C', 'D', 'D', 'C', 'D', 'C', 'C', 'D', 'D', 'C', 'D', 'C', 'D']

            # Add mock match history
            agent.match_history = [
                {'opponent': 'Opponent_001', 'rounds': [{'your_move': 'C', 'opponent_move': 'D'}, {'your_move': 'D', 'opponent_move': 'C'}]},
                {'opponent': 'Opponent_002', 'rounds': [{'your_move': 'C', 'opponent_move': 'C'}, {'your_move': 'C', 'opponent_move': 'D'}, {'your_move': 'D', 'opponent_move': 'D'}]}
            ]

            start_time = time.time()
            move_long = agent.make_move(long_own_history, long_opp_history)
            end_time = time.time()
            time_taken_long = end_time - start_time

            prompt_used = agent._create_prompt(long_own_history, long_opp_history)
            estimated_tokens = agent.estimate_tokens(prompt_used)

            moves.append(move_long)
            timings.append(time_taken_long)

            print(f"    Long query: {move_long} (time: {time_taken_long:.2f}s)")
            print(f"    Prompt length: {len(prompt_used)} chars")
            print(f"    Estimated tokens: {estimated_tokens}")
            print(f"    Processing speed: {estimated_tokens/time_taken_long:.1f} tokens/second")

            # Validate
            valid = all(m in ['C', 'D'] for m in moves)
            avg_time = sum(timings) / len(timings)
            results[model] = {
                'moves': moves,
                'calls': agent.api_calls,
                'tokens': agent.total_tokens,
                'valid': valid,
                'timings': timings,
                'avg_time': avg_time,
                'long_query_time': time_taken_long
            }

            total_calls += agent.api_calls
            total_tokens += agent.total_tokens

            print(f"✓ {model}: {agent.api_calls} calls, {agent.total_tokens} tokens, avg time: {avg_time:.2f}s, valid: {valid}")
        
        # Summary
        print("\n" + "="*60)
        print("✅ ALL MODELS TESTED!")
        print("="*60)
        
        all_valid = all(r['valid'] for r in results.values())
        print(f"Total API calls: {total_calls}")
        print(f"Total tokens: {total_tokens}")
        print(f"All moves valid: {all_valid}")

        print("\n📊 TIMING SUMMARY:")
        for model, result in results.items():
            print(f"{model}:")
            print(f"  Moves: {result['moves']} ({result['calls']} calls)")
            print(f"  Average time: {result['avg_time']:.2f}s")
            print(f"  Long query time: {result['long_query_time']:.2f}s")

        return all_valid
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_openai_models()
    exit(0 if success else 1)