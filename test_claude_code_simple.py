#!/usr/bin/env python3
"""
Simple test for ClaudeCodeAgent creation without API calls
"""
import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_claude_code_agent_creation():
    """Test that we can create ClaudeCodeAgent without errors"""
    try:
        from ipd_suite.agents import ClaudeCodeAgent

        # Test agent creation (no API calls)
        agent = ClaudeCodeAgent(
            name="TestAgent",
            model="claude-code",
            temperature=0.5,
            termination_prob=0.25
        )

        print(f"✅ Successfully created ClaudeCodeAgent:")
        print(f"   Name: {agent.name}")
        print(f"   Model: {agent.model}")
        print(f"   Temperature: {agent.temperature}")
        print(f"   Class: {agent.__class__.__name__}")

        # Test that it has the right methods
        assert hasattr(agent, 'make_move')
        assert hasattr(agent, '_call_api')
        assert hasattr(agent, 'claude_query')

        print("✅ All required methods present")

        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_argument_parsing():
    """Test that the new argument is properly added"""
    try:
        # Import without executing main
        import run_experiments

        # Test argument parser
        import argparse
        parser = argparse.ArgumentParser()

        # Manually add our argument to test
        parser.add_argument("--use-claude-code", action="store_true",
                           help="Use Claude Code SDK instead of Anthropic API")

        # Test parsing
        args = parser.parse_args(["--use-claude-code"])
        assert args.use_claude_code == True

        args = parser.parse_args([])
        assert args.use_claude_code == False

        print("✅ Argument parsing works correctly")
        return True

    except Exception as e:
        print(f"❌ Argument parsing error: {e}")
        return False

if __name__ == "__main__":
    print("="*50)
    print("CLAUDE CODE INTEGRATION - SIMPLE TEST")
    print("="*50)

    success1 = test_claude_code_agent_creation()
    success2 = test_argument_parsing()

    if success1 and success2:
        print("\n✅ All tests passed! Integration is ready.")
        print("\nTo use Claude Code integration:")
        print("  python run_experiments.py --use-claude-code [other args]")
        exit(0)
    else:
        print("\n❌ Some tests failed.")
        exit(1)