from simplified.llm import MockLLMClient
from simplified.rlm import RLM

def test_fibonacci():
    # Simulate a conversation flow
    # The mock needs to be smart enough to respond to the evolving history

    # We can use a smarter mock that checks the *end* of the prompt
    class ScriptedMockLLM(MockLLMClient):
        def __init__(self):
            self.step = 0

        def completion(self, prompt: str) -> str:
            if "10th fibonacci number" in prompt and self.step == 0:
                self.step += 1
                return """I will calculate the 10th Fibonacci number using Python.
```python
def fib(n):
    if n <= 1: return n
    return fib(n-1) + fib(n-2)

result = fib(10)
print(f"The 10th fibonacci number is {result}")
final_answer = result
```"""
            return "I am done."

    client = ScriptedMockLLM()
    rlm = RLM(client, verbose=True)

    answer = rlm.ask("What is the 10th fibonacci number?")
    print(f"Result: {answer}")
    assert answer == "55"

def test_recursion():
    # Simulate a recursive call via llm_query
    class RecursiveMockLLM(MockLLMClient):
        def completion(self, prompt: str) -> str:
            # Check if this is a sub-call (simple check)
            if "What is 2 + 2?" in prompt and "system" not in prompt: # simplistic check for raw prompt
                 return "4"

            # Main flow
            if "Calculate (2+2) * 3" in prompt:
                return """I need to calculate 2+2 first.
```python
val = int(llm_query("What is 2 + 2?"))
print(f"2+2 is {val}")
final_answer = val * 3
```"""
            return "4" # fallback for the sub-query if prompt format is different

    client = RecursiveMockLLM()
    rlm = RLM(client, verbose=True)

    answer = rlm.ask("Calculate (2+2) * 3")
    print(f"Result: {answer}")
    assert answer == "12"

if __name__ == "__main__":
    print("Running test_fibonacci...")
    test_fibonacci()
    print("\nRunning test_recursion...")
    test_recursion()
    print("\nAll tests passed!")
