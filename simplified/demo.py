import sys
import os

# Ensure the parent directory is in python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simplified.rlm import RLM
from simplified.client import MockClient

def main():
    print("Initializing RLM with MockClient...")
    client = MockClient()
    rlm = RLM(client, max_iterations=5)

    print("\n--- Test 1: Math Calculation ---")
    prompt = "Calculate 5 * 5"
    print(f"User Prompt: {prompt}")
    answer = rlm.completion(prompt)
    print(f"Final Answer: {answer}")
    assert answer == "25"

    print("\n--- Test 2: Recursive Query ---")
    prompt = "What is the capital of France?"
    print(f"User Prompt: {prompt}")
    answer = rlm.completion(prompt)
    print(f"Final Answer: {answer}")
    assert answer == "Paris"

    print("\n--- Test 3: FINAL_VAR with Single Turn ---")
    prompt = "Calculate 10 + 10"
    print(f"User Prompt: {prompt}")
    answer = rlm.completion(prompt)
    print(f"Final Answer: {answer}")
    assert answer == "20"

    print("\nAll tests passed!")

if __name__ == "__main__":
    main()
