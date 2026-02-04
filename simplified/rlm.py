import re

from simplified.client import BaseClient
from simplified.env import SimpleEnv
from simplified.prompts import RLM_SYSTEM_PROMPT


class SimpleRLM:
    def __init__(self, client: BaseClient, max_iterations: int = 10):
        self.client = client
        self.max_iterations = max_iterations

    def completion(self, prompt: str) -> str:
        """
        Main entry point for the RLM.
        """
        # Define the recursive callback
        # In this simplified version, recursion calls the client directly
        # effectively doing a depth-1 recursion.
        def llm_query_callback(query: str) -> str:
            # We treat the sub-query as a fresh completion call to the client
            # In a more complex system, this might spawn a new RLM instance
            return self.client.completion([
                {"role": "user", "content": query}
            ])

        # Initialize environment
        env = SimpleEnv(llm_query_func=llm_query_callback)

        # Initialize history
        history = [
            {"role": "system", "content": RLM_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]

        for _ in range(self.max_iterations):
            # Call LLM
            response = self.client.completion(history)

            # Append assistant response to history
            history.append({"role": "assistant", "content": response})

            # Check for final answer
            if "Final Answer:" in response:
                # Extract the final answer
                parts = response.split("Final Answer:")
                return parts[-1].strip()

            # Parse code blocks
            code_blocks = self._extract_code_blocks(response)

            if not code_blocks:
                # If no code and no final answer, we might want to prompt it to continue or stop.
                # For simplicity, we just continue, hoping the LLM realizes it needs to do something.
                # Or we can treat it as the final answer if it looks like one.
                # But let's assume the LLM follows instructions.
                pass

            # Execute code blocks
            outputs = []
            for code in code_blocks:
                result = env.execute_code(code)
                output_str = ""
                if result["stdout"]:
                    output_str += f"Stdout:\n{result['stdout']}\n"
                if result["stderr"]:
                    output_str += f"Stderr:\n{result['stderr']}\n"
                if not result["success"]:
                    output_str += "Execution failed.\n"

                outputs.append(output_str)

            if outputs:
                system_msg = "Execution Output:\n" + "\n".join(outputs)
                history.append({"role": "system", "content": system_msg})

        return "Max iterations reached without a final answer."

    def _extract_code_blocks(self, text: str) -> list[str]:
        pattern = r"```python\s*(.*?)\s*```"
        return re.findall(pattern, text, re.DOTALL)
