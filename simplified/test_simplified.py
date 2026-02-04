from simplified.client import MockClient
from simplified.rlm import SimpleRLM


def test_rlm_math():
    print("Testing Math Scenario...")
    # Map prompt keywords to responses
    responses = {
        "Calculate 5 + 3": """I will use python.
```python
print(5+3)
```""",
        "Stdout:\n8": "Final Answer: 8"
    }

    client = MockClient(responses=responses)
    rlm = SimpleRLM(client)

    result = rlm.completion("Calculate 5 + 3")
    print(f"Result: {result}")
    assert result == "8"
    print("Math Scenario Passed!")

def test_rlm_recursion():
    print("Testing Recursion Scenario...")
    # Scenario: "What is double of X?" where X is fetched via recursion.
    # LLM 1: "I need to find X via recursion." -> llm_query("What is X?")
    # LLM 2 (Recursive call): "X is 10."
    # LLM 1: "Ok X is 10. Double is 20." -> Final Answer: 20

    responses = {
        "What is double of X?": """I will find X.
```python
x = llm_query("What is X?")
print(int(x) * 2)
```""",
        "What is X?": "10",
        "Stdout:\n20": "Final Answer: 20"
    }

    client = MockClient(responses=responses)
    rlm = SimpleRLM(client)

    result = rlm.completion("What is double of X?")
    print(f"Result: {result}")
    assert result == "20"
    print("Recursion Scenario Passed!")

if __name__ == "__main__":
    test_rlm_math()
    test_rlm_recursion()
    print("All tests passed!")
