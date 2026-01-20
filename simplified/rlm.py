from simplified.client import BaseClient
from simplified.env import LocalEnv
from simplified.utils import find_code_blocks, find_final_answer, format_execution_result

class RLM:
    def __init__(self, client: BaseClient, max_iterations: int = 10):
        self.client = client
        self.max_iterations = max_iterations

    def completion(self, prompt: str) -> str:
        # 1. Initialize Environment with recursive callback
        # The callback allows the environment to call this RLM instance again (or the client directly)
        # For simplicity, we'll let it call the client directly for now, effectively "recursion depth 1" behavior
        # deeper recursion would require instantiating a new RLM or reusing this one carefully.

        def llm_query(query_prompt: str) -> str:
            # Simple recursive call: Just ask the base LLM.
            # In a full system, this might spawn a whole new RLM loop.
            return self.client.completion([{"role": "user", "content": query_prompt}])

        env = LocalEnv(llm_callback=llm_query)

        # 2. Initialize History
        messages = [
            {"role": "system", "content": (
                "You are a Recursive Language Model. You can execute Python code to solve problems.\n"
                "Use ```repl\ncode here\n``` to execute code.\n"
                "Use `llm_query(prompt)` inside your code to ask the LLM a sub-question.\n"
                "When you have the answer, output `FINAL(your answer)` or `FINAL_VAR(variable_name)`."
            )},
            {"role": "user", "content": prompt}
        ]

        # 3. Main Loop
        for _ in range(self.max_iterations):
            # Inference
            response = self.client.completion(messages)
            messages.append({"role": "assistant", "content": response})

            # Check for code blocks
            code_blocks = find_code_blocks(response)
            if code_blocks:
                # Execute blocks
                outputs = []
                for code in code_blocks:
                    result = env.execute(code)
                    formatted = format_execution_result(result)
                    outputs.append(f"Code:\n```python\n{code}\n```\nREPL output:\n{formatted}")

                # Append execution results to history
                messages.append({"role": "user", "content": "\n\n".join(outputs)})

            # Check for final answer
            final_ans = find_final_answer(response, env)
            if final_ans:
                return final_ans

            if not code_blocks:
                # If no code and no final answer, arguably the model is just chatting.
                # But in strict RLM, we might want to force it to do something.
                # For now, we just continue loop, effectively treating it as multi-turn chat
                pass

        return "Max iterations reached without final answer."
