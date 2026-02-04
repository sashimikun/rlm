import unittest
import sys
import os

# Ensure package is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from simplified.core.agent import ToolLoopAgent
from simplified.core.llm import MinimalLLM

class TestToolLoopAgent(unittest.TestCase):
    def test_mock_recursion(self):
        llm = MinimalLLM(api_key=None) # Force Mock
        agent = ToolLoopAgent(llm=llm, max_depth=2, max_steps=5)

        query = "Compute complex value"
        result = agent.run(query)

        self.assertIn("Final Answer: 42", result)
        self.assertIn("42", result)

    def test_depth_limit(self):
        # We can't easily test depth limit with the current mock logic unless we force infinite recursion.
        # But we can verify the agent initializes correctly.
        llm = MinimalLLM(api_key=None)
        agent = ToolLoopAgent(llm=llm, max_depth=0)
        # With max_depth 0, it shouldn't be able to recurse.
        # But the mock LLM will try to generate code calling llm_query.
        # If we run it, the injected llm_query should return "Error: Maximum recursion depth reached."
        # And the agent should see that error.

        query = "Compute complex value"
        # The mock LLM will get "Error..." back from llm_query.
        # The mock LLM logic in core/llm.py expects "Received: The magic number is 42".
        # It won't get that. It will default to "I am a mock LLM..."

        result = agent.run(query)
        # We expect it NOT to succeed
        self.assertNotEqual(result, "The complex value is 42. Final Answer: 42.")
        self.assertIn("I am a mock LLM", result)

if __name__ == "__main__":
    unittest.main()
