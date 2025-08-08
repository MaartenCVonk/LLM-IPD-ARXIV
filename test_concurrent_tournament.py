#!/usr/bin/env python3
"""
Quick test script for concurrent tournament execution
"""

import time
import asyncio
from ipd_suite import TitForTat, GrimTrigger, Random, Tournament

def test_concurrent_vs_sync():
    """Test concurrent vs synchronous tournament execution"""
    
    # Create a small set of agents for testing
    agents = [
        TitForTat("TitForTat1"),
        TitForTat("TitForTat2"),
        GrimTrigger("GrimTrigger1"),
        GrimTrigger("GrimTrigger2"), 
        Random("Random1"),
        Random("Random2")
    ]
    
    # Test parameters
    termination_prob = 0.5  # Higher termination for faster tests
    max_rounds = 10
    
    print("=== Concurrent Tournament Test ===")
    print(f"Testing with {len(agents)} agents")
    print(f"Total matches: {len(agents) * (len(agents) - 1) // 2}")
    
    # Test synchronous version
    print("\n1. Running SYNCHRONOUS tournament...")
    tournament_sync = Tournament(
        agents=agents.copy(), 
        termination_prob=termination_prob,
        max_rounds=max_rounds,
        verbose=True
    )
    
    start_time = time.time()
    result_sync = tournament_sync._run_tournament_sync()
    sync_time = time.time() - start_time
    
    print(f"Synchronous time: {sync_time:.2f} seconds")
    
    # Test asynchronous version
    print("\n2. Running CONCURRENT tournament...")
    tournament_async = Tournament(
        agents=agents.copy(),
        termination_prob=termination_prob, 
        max_rounds=max_rounds,
        verbose=True,
        max_concurrent=5  # Allow 5 concurrent matches
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
        print(f"Speedup: {speedup:.2f}x faster")
    else:
        slowdown = async_time / sync_time
        print(f"Slowdown: {slowdown:.2f}x slower")
    
    # Verify results are equivalent
    print(f"\n4. Result verification:")
    print(f"Both tournaments completed: {len(result_sync.match_results)} matches")
    print(f"Results match: {len(result_sync.match_results) == len(result_async.match_results)}")
    
    # Test the main tournament method (should auto-detect async)
    print(f"\n5. Testing main run_tournament() method...")
    tournament_auto = Tournament(
        agents=agents.copy(),
        termination_prob=termination_prob,
        max_rounds=max_rounds,
        verbose=True,
        max_concurrent=3
    )
    
    start_time = time.time()
    result_auto = tournament_auto.run_tournament()
    auto_time = time.time() - start_time
    
    print(f"Auto-detection time: {auto_time:.2f} seconds")
    print(f"Auto-detection completed {len(result_auto.match_results)} matches")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_concurrent_vs_sync()