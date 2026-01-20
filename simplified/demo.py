from simplified.client import MockClient
from simplified.rlm import SimpleRLM

def test_math_scenario():
    print("\n=== Test Scenario: Math ===")
    # Define mock responses
    responses = {
        "Add 10 and 20": "I will calculate this.\n```python\nprint(10+20)\n```",
        "Execution Result": "FINAL(30)" # After seeing the result 30
    }

    # We need to be careful with the mock key matching.
    # The client checks if the key is in the last message.
    # 1. User: "Add 10 and 20" -> Mock matches "Add 10 and 20" -> Returns code.
    # 2. User (Env output): "...STDOUT:\n30..." -> Mock matches "Execution Result"? No, likely needs something more specific or default.

    # Let's refine the mock logic or the keys.
    # The MockClient checks: `if key in last_msg:`

    client = MockClient(responses={
        "Add 10 and 20": "```python\nprint(10+20)\n```",
        "STDOUT:\n30": "The answer is 30. FINAL(30)"
    })

    rlm = SimpleRLM(client)
    result = rlm.completion("Add 10 and 20")
    print(f"Result: {result}")
    assert result == "30"

def test_recursion_scenario():
    print("\n=== Test Scenario: Recursion ===")

    # Logic:
    # 1. User: "Capital of France?"
    # 2. Mock: Calls llm_query.
    # 3. Env executes llm_query('Capital of France') -> Mock Client called again with "Capital of France".
    # 4. Mock should respond to "Capital of France" with "Paris".
    # 5. Env prints "Paris".
    # 6. Mock sees "Paris" in output, returns FINAL.

    responses = {
        "Capital of France?": "```python\nans = llm_query('Capital of France')\nprint(ans)\n```",
        "Capital of France": "Paris", # The sub-call
        "STDOUT:\nParis": "FINAL(Paris)"
    }

    client = MockClient(responses=responses)
    rlm = SimpleRLM(client)
    result = rlm.completion("Capital of France?")
    print(f"Result: {result}")
    assert result == "Paris"

if __name__ == "__main__":
    test_math_scenario()
    test_recursion_scenario()
