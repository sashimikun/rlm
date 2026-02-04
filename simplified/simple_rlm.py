import sys
import io
import re
from typing import List, Dict, Any, Optional

class MockLLM:
    """
    A simple mock LLM that returns predefined responses based on keywords in the prompt.
    """
    def completion(self, prompt: str) -> str:
        prompt_lower = str(prompt).lower()

        # Heuristic: If we see the answer in the history (which is part of the prompt), return Final Answer.
        if "fibonacci of 10 is 55" in prompt_lower:
            return "Final Answer: 55"
        if "the result from sub-call is: the capital of france is paris" in prompt_lower:
            return "Final Answer: Paris"

        if "fibonacci" in prompt_lower:
            return """
I will write a Python function to calculate the Fibonacci number.
```python
def fib(n):
    if n <= 1:
        return n
    return fib(n-1) + fib(n-2)

print(f"Fibonacci of 10 is {fib(10)}")
```
"""
        elif "recursion" in prompt_lower:
            return """
I will use recursion to find the capital of France.
```python
result = llm_query("What is the capital of France?")
print(f"The result from sub-call is: {result}")
```
"""
        elif "capital of france" in prompt_lower:
            return "The capital of France is Paris."
        else:
            return "I don't know how to handle this query. Final Answer: Unknown"

class SimpleRLM:
    def __init__(self, client: Any, max_iterations: int = 5):
        self.client = client
        self.max_iterations = max_iterations
        self.history: List[Dict[str, str]] = []

    def _llm_query(self, prompt: str) -> str:
        """
        The function injected into the environment.
        """
        # Print to real stdout so it shows up in the console even during capture
        print(f"[RLM] Recursive call: {prompt}", file=sys.__stdout__)

        # In a real implementation, we might want to create a new SimpleRLM instance here
        # to track depth, but for simplicity, we just call the client directly.
        return self.client.completion(prompt)

    def _execute_code(self, code: str, context_locals: Dict[str, Any]) -> str:
        """
        Executes code and captures stdout.
        """
        # Create a buffer to capture stdout
        stdout_capture = io.StringIO()
        original_stdout = sys.stdout

        try:
            sys.stdout = stdout_capture
            # Execute the code. Using context_locals for both globals and locals
            # ensures that functions defined in the code can see themselves and other variables.
            exec(code, context_locals, context_locals)
            output = stdout_capture.getvalue()
        except Exception as e:
            output = f"Error: {str(e)}"
        finally:
            # Restore stdout
            sys.stdout = original_stdout

        return output

    def completion(self, prompt: str) -> str:
        """
        Main RLM loop.
        """
        self.history = [{"role": "user", "content": prompt}]

        # Initialize execution environment with the recursive function
        context_locals = {"llm_query": self._llm_query}

        for i in range(self.max_iterations):
            print(f"\n[RLM] Iteration {i+1}")

            # Construct the prompt for the LLM
            # For simplicity, we just flatten the history
            prompt_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in self.history])

            # Call LLM
            response = self.client.completion(prompt_text)
            print(f"[RLM] LLM Response: {response}")

            self.history.append({"role": "assistant", "content": response})

            # Check for Final Answer
            if "Final Answer:" in response:
                return response.split("Final Answer:")[-1].strip()

            # Parse Code Blocks
            code_blocks = re.findall(r"```python(.*?)```", response, re.DOTALL)

            if not code_blocks:
                # If no code blocks and no final answer, assume the whole response is the answer
                # or just return it if we want to be simple
                if i == self.max_iterations - 1:
                     return response
                continue

            # Execute Code Blocks
            execution_output = ""
            for code in code_blocks:
                print("[RLM] Executing code...")
                output = self._execute_code(code.strip(), context_locals)
                print(f"[RLM] Execution Output: {output}")
                execution_output += output + "\n"

            # Add execution output to history
            if execution_output.strip():
                self.history.append({"role": "system", "content": f"Execution Output:\n{execution_output}"})

                # Check if the execution output contains the answer (heuristic)
                # In a real RLM, the LLM would see the output and decide.
                # Here we just continue the loop so the LLM can see the output in the next turn.

        return "Max iterations reached."
