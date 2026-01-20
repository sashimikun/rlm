import os
import sys

# Ensure the package is in python path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from simplified.core.agent import ToolLoopAgent
from simplified.core.llm import MinimalLLM

def main():
    print("Initializing Simplified RLM Agent...")

    # Check for API Key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("No OPENAI_API_KEY found. Using Mock LLM.")
    else:
        print("Using OpenAI API.")

    llm = MinimalLLM(api_key=api_key)
    agent = ToolLoopAgent(llm=llm, max_depth=2, max_steps=5)

    print("\n--- Starting Recursive Task ---")
    query = "Compute complex value"
    print(f"User Query: {query}")

    final_answer = agent.run(query)

    print("\n--- Final Result ---")
    print(final_answer)

if __name__ == "__main__":
    main()
