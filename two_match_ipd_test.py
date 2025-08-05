#!/usr/bin/env python3
"""
Two-match IPD test script with detailed token tracking
- Match 1: GPT4 Agent vs Gemini Agent (10 rounds exactly)
- Match 2: Claude Agent vs Mistral Agent (10 rounds exactly)
- Temperature 1.0 for all agents
- Detailed token tracking per round and per agent
"""
import sys
import os
from datetime import datetime
import json
import time

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: dotenv not available, using system environment variables")

# Add the parent directory to the path so we can import ipd_suite
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ipd_suite.agents import GPT4Agent, ClaudeAgent, MistralAgent, GeminiAgent


class TokenAndTimeTracker:
    """Track detailed token usage and timing for each agent"""
    def __init__(self, agent_name):
        self.agent_name = agent_name
        self.rounds = []
        self.total_tokens = 0
        self.total_api_calls = 0
        self.total_time = 0
        
    def record_round(self, round_num, tokens_before, tokens_after, input_tokens_before, input_tokens_after, output_tokens_before, output_tokens_after, time_start, time_end, move, reasoning=None, fallback_used=False):
        """Record token usage and timing for a specific round"""
        tokens_used = tokens_after - tokens_before
        input_tokens_used = input_tokens_after - input_tokens_before
        output_tokens_used = output_tokens_after - output_tokens_before
        time_taken = time_end - time_start
        self.rounds.append({
            'round': round_num,
            'tokens_used': tokens_used,
            'input_tokens_used': input_tokens_used,
            'output_tokens_used': output_tokens_used,
            'total_tokens_so_far': tokens_after,
            'total_input_tokens_so_far': input_tokens_after,
            'total_output_tokens_so_far': output_tokens_after,
            'time_taken_seconds': round(time_taken, 3),
            'total_time_so_far': round(self.total_time + time_taken, 3),
            'move': move,
            'reasoning': reasoning,  # Save full reasoning without truncation
            'reasoning_length': len(reasoning) if reasoning else 0,
            'fallback_used': fallback_used  # Track if automatic C was used
        })
        self.total_tokens = tokens_after
        self.total_time += time_taken
        
    def get_summary(self):
        """Get summary statistics"""
        if not self.rounds:
            return {
                'agent': self.agent_name,
                'total_tokens': 0,
                'total_input_tokens': 0,
                'total_output_tokens': 0,
                'total_api_calls': 0,
                'total_time_seconds': 0,
                'avg_tokens_per_round': 0,
                'avg_input_tokens_per_round': 0,
                'avg_output_tokens_per_round': 0,
                'avg_time_per_round': 0,
                'fallback_count': 0,
                'fallback_percentage': 0,
                'total_reasoning_length': 0,
                'avg_reasoning_length': 0,
                'rounds': []
            }
        
        fallback_count = sum(1 for round_data in self.rounds if round_data.get('fallback_used', False))
        total_reasoning_length = sum(round_data.get('reasoning_length', 0) for round_data in self.rounds)
        total_input_tokens = self.rounds[-1].get('total_input_tokens_so_far', 0) if self.rounds else 0
        total_output_tokens = self.rounds[-1].get('total_output_tokens_so_far', 0) if self.rounds else 0
        
        return {
            'agent': self.agent_name,
            'total_tokens': self.total_tokens,
            'total_input_tokens': total_input_tokens,
            'total_output_tokens': total_output_tokens,
            'total_api_calls': len(self.rounds),
            'total_time_seconds': round(self.total_time, 3),
            'avg_tokens_per_round': round(self.total_tokens / len(self.rounds), 1),
            'avg_input_tokens_per_round': round(total_input_tokens / len(self.rounds), 1),
            'avg_output_tokens_per_round': round(total_output_tokens / len(self.rounds), 1),
            'avg_time_per_round': round(self.total_time / len(self.rounds), 3),
            'fallback_count': fallback_count,
            'fallback_percentage': round((fallback_count / len(self.rounds)) * 100, 1),
            'total_reasoning_length': total_reasoning_length,
            'avg_reasoning_length': round(total_reasoning_length / len(self.rounds), 1) if self.rounds else 0,
            'rounds': self.rounds
        }


def play_exact_rounds_match(agent1, agent2, rounds=10):
    """Play exactly N rounds between two agents with detailed tracking"""
    match_start_time = time.time()
    
    print(f"\n{'='*60}")
    print(f"MATCH: {agent1.name} vs {agent2.name}")
    print(f"Playing exactly {rounds} rounds")
    print(f"Match started at: {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*60}")
    
    # Initialize trackers
    tracker1 = TokenAndTimeTracker(agent1.name)
    tracker2 = TokenAndTimeTracker(agent2.name)
    
    # Game state
    agent1_history = []
    agent2_history = []
    agent1_score = 0
    agent2_score = 0
    
    # Play exactly the specified number of rounds
    for round_num in range(1, rounds + 1):
        round_start_time = time.time()
        print(f"\nRound {round_num}/{rounds} - {datetime.now().strftime('%H:%M:%S')}")
        print("-" * 30)
        
        # Record token counts and time before moves
        tokens1_before = agent1.total_tokens
        tokens2_before = agent2.total_tokens
        input1_before = getattr(agent1, 'input_tokens', 0)
        input2_before = getattr(agent2, 'input_tokens', 0)
        output1_before = getattr(agent1, 'output_tokens', 0)
        output2_before = getattr(agent2, 'output_tokens', 0)
        
        # Agent 1 makes move
        agent1_start_time = time.time()
        agent1_fallback = False
        agent1_original_move = None
        try:
            move1 = agent1.make_move(agent1_history.copy(), agent2_history.copy())
            agent1_original_move = move1
            
            # Check if this was a fallback by replicating the agents.py logic
            if hasattr(agent1, 'last_reasoning') and move1 == 'C' and agent1.last_reasoning:
                # Replicate the exact move extraction logic from agents.py lines 808-819
                # but handle various formatting patterns that LLMs use
                response = agent1.last_reasoning.strip()
                lines = [line.strip() for line in response.split('\n') if line.strip()]  # Remove empty lines
                
                # Check multiple lines from the end to handle code blocks and formatting
                found_valid_move = False
                for line in reversed(lines[-3:]):  # Check last 3 non-empty lines
                    line_upper = line.upper()
                    # Remove common formatting like backticks, quotes, etc.
                    clean_line = line_upper.replace('`', '').replace('"', '').replace("'", '').strip()
                    
                    if clean_line in ['C', 'D']:
                        found_valid_move = True
                        break
                    elif 'C' in clean_line and 'D' not in clean_line:
                        found_valid_move = True
                        break
                    elif 'D' in clean_line and 'C' not in clean_line:
                        found_valid_move = True
                        break
                
                # Only flag as fallback if no valid move was found in the last few lines
                if not found_valid_move:
                    agent1_fallback = True
            
            if move1 not in ['C', 'D']:
                print(f"Warning: {agent1.name} returned invalid move '{move1}', defaulting to 'C'")
                move1 = 'C'
                agent1_fallback = True
        except Exception as e:
            print(f"Error: {agent1.name} failed to make move: {e}")
            move1 = 'C'
            agent1_fallback = True
        agent1_end_time = time.time()
        
        # Agent 2 makes move
        agent2_start_time = time.time()
        agent2_fallback = False
        agent2_original_move = None
        try:
            move2 = agent2.make_move(agent2_history.copy(), agent1_history.copy())
            agent2_original_move = move2
            
            # Check if this was a fallback by replicating the agents.py logic
            if hasattr(agent2, 'last_reasoning') and move2 == 'C' and agent2.last_reasoning:
                # Replicate the exact move extraction logic from agents.py lines 808-819
                # but handle various formatting patterns that LLMs use
                response = agent2.last_reasoning.strip()
                lines = [line.strip() for line in response.split('\n') if line.strip()]  # Remove empty lines
                
                # Check multiple lines from the end to handle code blocks and formatting
                found_valid_move = False
                for line in reversed(lines[-3:]):  # Check last 3 non-empty lines
                    line_upper = line.upper()
                    # Remove common formatting like backticks, quotes, etc.
                    clean_line = line_upper.replace('`', '').replace('"', '').replace("'", '').strip()
                    
                    if clean_line in ['C', 'D']:
                        found_valid_move = True
                        break
                    elif 'C' in clean_line and 'D' not in clean_line:
                        found_valid_move = True
                        break
                    elif 'D' in clean_line and 'C' not in clean_line:
                        found_valid_move = True
                        break
                
                # Only flag as fallback if no valid move was found in the last few lines
                if not found_valid_move:
                    agent2_fallback = True
            
            if move2 not in ['C', 'D']:
                print(f"Warning: {agent2.name} returned invalid move '{move2}', defaulting to 'C'")
                move2 = 'C'
                agent2_fallback = True
        except Exception as e:
            print(f"Error: {agent2.name} failed to make move: {e}")
            move2 = 'C'
            agent2_fallback = True
        agent2_end_time = time.time()
        
        # Record token counts after moves
        tokens1_after = agent1.total_tokens
        tokens2_after = agent2.total_tokens
        input1_after = getattr(agent1, 'input_tokens', 0)
        input2_after = getattr(agent2, 'input_tokens', 0)
        output1_after = getattr(agent1, 'output_tokens', 0)
        output2_after = getattr(agent2, 'output_tokens', 0)
        
        # Calculate payoffs
        if move1 == 'C' and move2 == 'C':
            payoff1, payoff2 = 3, 3
        elif move1 == 'C' and move2 == 'D':
            payoff1, payoff2 = 0, 5
        elif move1 == 'D' and move2 == 'C':
            payoff1, payoff2 = 5, 0
        else:  # Both defect
            payoff1, payoff2 = 1, 1
        
        # Update scores and histories
        agent1_score += payoff1
        agent2_score += payoff2
        agent1_history.append(move1)
        agent2_history.append(move2)
        
        # Track token usage and timing
        tracker1.record_round(round_num, tokens1_before, tokens1_after, input1_before, input1_after, output1_before, output1_after, agent1_start_time, agent1_end_time, move1, agent1.last_reasoning, agent1_fallback)
        tracker2.record_round(round_num, tokens2_before, tokens2_after, input2_before, input2_after, output2_before, output2_after, agent2_start_time, agent2_end_time, move2, agent2.last_reasoning, agent2_fallback)
        
        # Print round results with timing
        agent1_time = agent1_end_time - agent1_start_time
        agent2_time = agent2_end_time - agent2_start_time
        round_total_time = time.time() - round_start_time
        
        fallback1_indicator = " [FALLBACK]" if agent1_fallback else ""
        fallback2_indicator = " [FALLBACK]" if agent2_fallback else ""
        input1_used = input1_after - input1_before
        output1_used = output1_after - output1_before
        input2_used = input2_after - input2_before
        output2_used = output2_after - output2_before
        print(f"{agent1.name}: {move1}{fallback1_indicator} (payoff: {payoff1}, tokens: {tokens1_after - tokens1_before} [in:{input1_used}, out:{output1_used}], time: {agent1_time:.2f}s)")
        print(f"{agent2.name}: {move2}{fallback2_indicator} (payoff: {payoff2}, tokens: {tokens2_after - tokens2_before} [in:{input2_used}, out:{output2_used}], time: {agent2_time:.2f}s)")
        print(f"Round time: {round_total_time:.2f}s | Running scores - {agent1.name}: {agent1_score}, {agent2.name}: {agent2_score}")
        
        # Show reasoning (truncated)
        if agent1.last_reasoning:
            reasoning1 = agent1.last_reasoning[:150] + "..." if len(agent1.last_reasoning) > 150 else agent1.last_reasoning
            print(f"{agent1.name} reasoning: {reasoning1}")
        if agent2.last_reasoning:
            reasoning2 = agent2.last_reasoning[:150] + "..." if len(agent2.last_reasoning) > 150 else agent2.last_reasoning
            print(f"{agent2.name} reasoning: {reasoning2}")
    
    # Match summary with timing
    match_end_time = time.time()
    match_duration = match_end_time - match_start_time
    
    print(f"\n{'='*60}")
    print("MATCH RESULTS")
    print(f"{'='*60}")
    print(f"Match completed at: {datetime.now().strftime('%H:%M:%S')}")
    print(f"Total match duration: {match_duration:.2f} seconds ({match_duration/60:.1f} minutes)")
    print(f"{agent1.name}: {agent1_score} points ({agent1_score/rounds:.2f} avg)")
    print(f"{agent2.name}: {agent2_score} points ({agent2_score/rounds:.2f} avg)")
    
    winner = agent1.name if agent1_score > agent2_score else agent2.name if agent2_score > agent1_score else "TIE"
    print(f"Winner: {winner}")
    
    # Token usage and timing summary
    summary1 = tracker1.get_summary()
    summary2 = tracker2.get_summary()
    
    print(f"\nTOKEN & TIME SUMMARY:")
    print(f"{agent1.name}: {summary1['total_tokens']} tokens ({summary1['avg_tokens_per_round']:.1f} avg) [in:{summary1['total_input_tokens']:.0f}, out:{summary1['total_output_tokens']:.0f}], {summary1['total_time_seconds']:.2f}s ({summary1['avg_time_per_round']:.2f}s avg)")
    print(f"  Fallbacks: {summary1['fallback_count']}/{summary1['total_api_calls']} ({summary1['fallback_percentage']:.1f}%), Reasoning: {summary1['avg_reasoning_length']:.0f} chars avg")
    print(f"{agent2.name}: {summary2['total_tokens']} tokens ({summary2['avg_tokens_per_round']:.1f} avg) [in:{summary2['total_input_tokens']:.0f}, out:{summary2['total_output_tokens']:.0f}], {summary2['total_time_seconds']:.2f}s ({summary2['avg_time_per_round']:.2f}s avg)")
    print(f"  Fallbacks: {summary2['fallback_count']}/{summary2['total_api_calls']} ({summary2['fallback_percentage']:.1f}%), Reasoning: {summary2['avg_reasoning_length']:.0f} chars avg")
    
    return {
        'match': f"{agent1.name} vs {agent2.name}",
        'rounds_played': rounds,
        'match_duration_seconds': round(match_duration, 3),
        'match_duration_minutes': round(match_duration/60, 2),
        'scores': {agent1.name: agent1_score, agent2.name: agent2_score},
        'winner': winner,
        'agent1_tracking': summary1,
        'agent2_tracking': summary2,
        'game_history': {
            'agent1_moves': agent1_history,
            'agent2_moves': agent2_history
        }
    }


def main():
    """Main function to run the two-match test"""
    overall_start_time = time.time()
    print("="*80)
    print("TWO-MATCH IPD TEST WITH DETAILED TOKEN & TIME TRACKING")
    print("Match 1: GPT4 vs Gemini (10 rounds)")
    print("Match 2: Claude vs Mistral (10 rounds)")
    print("Temperature: 1.0 for all agents")
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # Check API keys
    required_keys = {
        'OPENAI_API_KEY': 'OpenAI GPT4',
        'GOOGLE_API_KEY': 'Google Gemini', 
        'ANTHROPIC_API_KEY': 'Anthropic Claude',
        'MISTRAL_API_KEY': 'Mistral'
    }
    
    missing_keys = []
    for key, service in required_keys.items():
        if not os.environ.get(key):
            missing_keys.append(f"{key} ({service})")
    
    if missing_keys:
        print("❌ Missing required API keys:")
        for key in missing_keys:
            print(f"   - {key}")
        print("\nPlease set these in your .env file or environment variables")
        return
    
    print("✓ All required API keys found")
    
    # Create agents with temperature 1.0 (using models from test file)
    try:
        print("\nCreating agents...")
        
        # GPT4 Agent - using o3 model from test file
        gpt4_agent = GPT4Agent(
            name="GPT4_Agent",
            api_key=os.environ['OPENAI_API_KEY'],
            model="o3",  # From test file
            temperature=1.0,
            termination_prob=0.1
        )
        print(f"✓ Created {gpt4_agent.name} (model: {gpt4_agent.model})")
        
        # Gemini Agent - using gemini-2.5-pro from test file
        gemini_agent = GeminiAgent(
            name="Gemini_Agent",
            api_key=os.environ['GOOGLE_API_KEY'],
            model="gemini-2.5-pro",  # From test file
            temperature=1.0,
            termination_prob=0.1
        )
        print(f"✓ Created {gemini_agent.name} (model: {gemini_agent.model})")
        
        # Claude Agent - using claude-opus-4-20250514 from test file
        claude_agent = ClaudeAgent(
            name="Claude_Agent",
            api_key=os.environ['ANTHROPIC_API_KEY'],
            model="claude-opus-4-20250514",  # From test file
            temperature=1.0,
            termination_prob=0.1
        )
        print(f"✓ Created {claude_agent.name} (model: {claude_agent.model})")
        
        # Mistral Agent - using mistral-large-latest from test file
        mistral_agent = MistralAgent(
            name="Mistral_Agent",
            api_key=os.environ['MISTRAL_API_KEY'],
            model="mistral-large-latest",  # From test file
            temperature=1.0,
            termination_prob=0.1
        )
        print(f"✓ Created {mistral_agent.name} (model: {mistral_agent.model})")
        
    except Exception as e:
        print(f"❌ Error creating agents: {e}")
        return
    
    # Store results
    all_results = []
    
    # Match 1: GPT4 vs Gemini
    print(f"\n{'='*80}")
    print("STARTING MATCH 1: GPT4 vs GEMINI")
    print(f"{'='*80}")
    
    try:
        match1_results = play_exact_rounds_match(gpt4_agent, gemini_agent, rounds=10)
        all_results.append(match1_results)
        print("✅ Match 1 completed successfully")
    except Exception as e:
        print(f"❌ Error in Match 1: {e}")
        import traceback
        traceback.print_exc()
    
    # Match 2: Claude vs Mistral
    print(f"\n{'='*80}")
    print("STARTING MATCH 2: CLAUDE vs MISTRAL")
    print(f"{'='*80}")
    
    try:
        match2_results = play_exact_rounds_match(claude_agent, mistral_agent, rounds=10)
        all_results.append(match2_results)
        print("✅ Match 2 completed successfully")
    except Exception as e:
        print(f"❌ Error in Match 2: {e}")
        import traceback
        traceback.print_exc()
    
    # Overall summary with timing
    overall_end_time = time.time()
    total_test_duration = overall_end_time - overall_start_time
    
    print(f"\n{'='*80}")
    print("OVERALL SUMMARY")
    print(f"{'='*80}")
    print(f"Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total test duration: {total_test_duration:.2f} seconds ({total_test_duration/60:.1f} minutes)")
    
    total_tokens_used = 0
    total_input_tokens = 0
    total_output_tokens = 0
    total_api_calls = 0
    total_api_time = 0
    total_fallbacks = 0
    
    for i, result in enumerate(all_results, 1):
        print(f"\nMatch {i}: {result['match']}")
        print(f"  Winner: {result['winner']}")
        print(f"  Duration: {result['match_duration_seconds']:.1f}s ({result['match_duration_minutes']:.1f}min)")
        print(f"  Rounds: {result['rounds_played']}")
        
        agent1_data = result['agent1_tracking']
        agent2_data = result['agent2_tracking']
        
        print(f"  {agent1_data['agent']}: {agent1_data['total_tokens']} tokens ({agent1_data['avg_tokens_per_round']:.1f} avg) [in:{agent1_data['total_input_tokens']:.0f}, out:{agent1_data['total_output_tokens']:.0f}], {agent1_data['total_time_seconds']:.1f}s")
        print(f"    Fallbacks: {agent1_data['fallback_count']} ({agent1_data['fallback_percentage']:.1f}%), Reasoning: {agent1_data['avg_reasoning_length']:.0f} chars avg")
        print(f"  {agent2_data['agent']}: {agent2_data['total_tokens']} tokens ({agent2_data['avg_tokens_per_round']:.1f} avg) [in:{agent2_data['total_input_tokens']:.0f}, out:{agent2_data['total_output_tokens']:.0f}], {agent2_data['total_time_seconds']:.1f}s")
        print(f"    Fallbacks: {agent2_data['fallback_count']} ({agent2_data['fallback_percentage']:.1f}%), Reasoning: {agent2_data['avg_reasoning_length']:.0f} chars avg")
        
        match_tokens = agent1_data['total_tokens'] + agent2_data['total_tokens']
        match_input_tokens = agent1_data['total_input_tokens'] + agent2_data['total_input_tokens']
        match_output_tokens = agent1_data['total_output_tokens'] + agent2_data['total_output_tokens']
        match_calls = agent1_data['total_api_calls'] + agent2_data['total_api_calls']
        match_api_time = agent1_data['total_time_seconds'] + agent2_data['total_time_seconds']
        match_fallbacks = agent1_data['fallback_count'] + agent2_data['fallback_count']
        
        print(f"  Match totals: {match_tokens} tokens [in:{match_input_tokens:.0f}, out:{match_output_tokens:.0f}], {match_calls} API calls, {match_api_time:.1f}s API time, {match_fallbacks} fallbacks")
        
        total_tokens_used += match_tokens
        total_input_tokens += match_input_tokens
        total_output_tokens += match_output_tokens
        total_api_calls += match_calls
        total_api_time += match_api_time
        total_fallbacks += match_fallbacks
    
    print(f"\nGRAND TOTALS:")
    print(f"- Total tokens used: {total_tokens_used:,} [input: {total_input_tokens:.0f}, output: {total_output_tokens:.0f}]")
    print(f"- Total API calls: {total_api_calls}")
    print(f"- Total fallbacks: {total_fallbacks} ({total_fallbacks/total_api_calls*100:.1f}% of calls)")
    print(f"- Total API time: {total_api_time:.1f} seconds ({total_api_time/60:.1f} minutes)")
    print(f"- Average tokens per call: {total_tokens_used/total_api_calls:.1f} [in: {total_input_tokens/total_api_calls:.1f}, out: {total_output_tokens/total_api_calls:.1f}]")
    print(f"- Average time per call: {total_api_time/total_api_calls:.2f} seconds")
    print(f"- API efficiency: {total_tokens_used/total_api_time:.0f} tokens/second")
    
    # Save detailed results to JSON
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"two_match_ipd_results_{timestamp}.json"
    
    output_data = {
        'test_info': {
            'timestamp': datetime.now().isoformat(),
            'test_type': 'two_match_ipd_10_rounds_with_timing',
            'temperature': 1.0,
            'rounds_per_match': 10,
            'total_test_duration_seconds': round(total_test_duration, 3),
            'total_test_duration_minutes': round(total_test_duration/60, 2)
        },
        'matches': all_results,
        'summary': {
            'total_tokens_used': total_tokens_used,
            'total_input_tokens': total_input_tokens,
            'total_output_tokens': total_output_tokens,
            'total_api_calls': total_api_calls,
            'total_fallbacks': total_fallbacks,
            'fallback_percentage': round(total_fallbacks/total_api_calls*100, 1) if total_api_calls > 0 else 0,
            'total_api_time_seconds': round(total_api_time, 3),
            'total_api_time_minutes': round(total_api_time/60, 2),
            'avg_tokens_per_call': round(total_tokens_used/total_api_calls, 1) if total_api_calls > 0 else 0,
            'avg_input_tokens_per_call': round(total_input_tokens/total_api_calls, 1) if total_api_calls > 0 else 0,
            'avg_output_tokens_per_call': round(total_output_tokens/total_api_calls, 1) if total_api_calls > 0 else 0,
            'avg_time_per_call': round(total_api_time/total_api_calls, 3) if total_api_calls > 0 else 0,
            'api_efficiency_tokens_per_second': round(total_tokens_used/total_api_time, 1) if total_api_time > 0 else 0
        }
    }
    
    try:
        with open(filename, 'w') as f:
            json.dump(output_data, f, indent=2)
        print(f"\n📄 Detailed results saved to: {filename}")
    except Exception as e:
        print(f"⚠️  Could not save results file: {e}")
    
    print(f"\n{'='*80}")
    print("TEST COMPLETED!")
    print(f"{'='*80}")


if __name__ == "__main__":
    main()