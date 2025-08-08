#!/usr/bin/env python3
"""
Test concurrent tournament execution with LLM agents
"""

import time
import asyncio
import os
from dotenv import load_dotenv
from ipd_suite import TitForTat, GrimTrigger, Tournament

# Load environment variables
load_dotenv('.env')

# Only run this test if we have API keys
def has_api_keys():
    return bool(os.getenv('OPENAI_API_KEY') or os.getenv('GOOGLE_API_KEY'))

def test_llm_concurrent():
    """Test concurrent vs synchronous with LLM agents"""
    
    if not has_api_keys():
        print("No API keys found. Skipping LLM concurrency test.")
        print("Set OPENAI_API_KEY or GOOGLE_API_KEY to test with real LLM agents.")
        return
        
    try:
        from ipd_suite import GPT4Agent, GeminiAgent
        
        # Create a mix of agents including LLM agents
        agents = [
            TitForTat("TitForTat"),
            GrimTrigger("GrimTrigger")
        ]
        
        # Add LLM agents if API keys are available
        if os.getenv('OPENAI_API_KEY'):
            agents.append(GPT4Agent("GPT4_Test", os.getenv('OPENAI_API_KEY'), temperature=0.5, termination_prob=0.7))
        
        if os.getenv('GOOGLE_API_KEY'):
            agents.append(GeminiAgent("Gemini_Test", os.getenv('GOOGLE_API_KEY'), temperature=0.5, termination_prob=0.7))
            
        print("=== LLM Concurrent Tournament Test ===")
        print(f"Testing with {len(agents)} agents (including LLM agents)")
        print(f"Total matches: {len(agents) * (len(agents) - 1) // 2}")
        
        # Test parameters - higher termination for faster tests
        termination_prob = 0.8  
        max_rounds = 5
        
        # Test synchronous version
        print("\n1. Running SYNCHRONOUS tournament with LLM agents...")
        tournament_sync = Tournament(
            agents=[agent for agent in agents], 
            termination_prob=termination_prob,
            max_rounds=max_rounds,
            verbose=True
        )
        
        start_time = time.time()
        result_sync = tournament_sync._run_tournament_sync()
        sync_time = time.time() - start_time
        
        print(f"Synchronous time: {sync_time:.2f} seconds")
        
        # Test asynchronous version
        print("\n2. Running CONCURRENT tournament with LLM agents...")
        tournament_async = Tournament(
            agents=[agent for agent in agents],
            termination_prob=termination_prob,
            max_rounds=max_rounds,
            verbose=True,
            max_concurrent=3  # Allow 3 concurrent matches
        )
        
        start_time = time.time()
        result_async = asyncio.run(tournament_async.run_tournament_async())
        async_time = time.time() - start_time
        
        print(f"Concurrent time: {async_time:.2f} seconds")
        
        # Compare results
        print(f"\n3. Performance comparison:")
        print(f"Synchronous: {sync_time:.2f}s")
        print(f"Concurrent:  {async_time:.2f}s")
        if sync_time > async_time:
            speedup = sync_time / async_time
            print(f"🚀 Speedup: {speedup:.2f}x faster with concurrency")
        else:
            slowdown = async_time / sync_time
            print(f"⚠️  Slowdown: {slowdown:.2f}x slower (overhead dominates)")
            
        print(f"\n4. API Call Analysis:")
        
        # Count total API calls made
        total_api_calls = 0
        total_tokens = 0
        for agent in agents:
            if hasattr(agent, 'api_calls'):
                print(f"- {agent.name}: {agent.api_calls} API calls, {agent.total_tokens} tokens")
                total_api_calls += agent.api_calls
                total_tokens += agent.total_tokens
                
        print(f"Total API calls: {total_api_calls}")
        print(f"Total tokens: {total_tokens}")
        
        if total_api_calls > 0:
            avg_time_per_call_sync = sync_time / total_api_calls if total_api_calls > 0 else 0
            avg_time_per_call_async = async_time / total_api_calls if total_api_calls > 0 else 0
            print(f"Avg time per API call (sync): {avg_time_per_call_sync:.3f}s")
            print(f"Avg time per API call (async): {avg_time_per_call_async:.3f}s")
        
        print("\n=== LLM Test Complete ===")
        
    except ImportError as e:
        print(f"Could not import LLM agents: {e}")
    except Exception as e:
        print(f"Error during LLM test: {e}")

if __name__ == "__main__":
    test_llm_concurrent()