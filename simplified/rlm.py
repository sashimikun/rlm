import re
from typing import List, Dict, Any, Optional
from .client import BaseClient
from .env import SimpleEnv
from .prompts import RLM_SYSTEM_PROMPT

class SimpleRLM:
    def __init__(self, client: BaseClient, max_iterations: int = 10):
        self.client = client
        self.max_iterations = max_iterations
        self.env = SimpleEnv(llm_query_callback=self._llm_query)

    def _llm_query(self, prompt: str) -> str:
        """
        Callback for the environment to query the LLM.
        """
        # In this simplified version, we treat a sub-query as a fresh call
        # to the same client with just the new prompt.
        return self.client.completion([{"role": "user", "content": prompt}])

    def _parse_code_blocks(self, text: str) -> List[str]:
        """
        Extracts python code blocks from the text.
        """
        # Regex for markdown code blocks with 'python' tag
        pattern = r"```python\s*(.*?)\s*```"
        matches = re.findall(pattern, text, re.DOTALL)
        # Also support blocks without language tag if needed, but strict is better for now.
        return matches

    def _find_final_answer(self, text: str) -> Optional[str]:
        """
        Checks for FINAL(answer) or FINAL_VAR(variable_name) patterns.
        """
        # Check for FINAL(answer)
        match = re.search(r"FINAL\((.*?)\)", text, re.DOTALL)
        if match:
            return match.group(1)

        # Check for FINAL_VAR(var_name)
        match = re.search(r"FINAL_VAR\((.*?)\)", text)
        if match:
            var_name = match.group(1).strip()
            # Remove quotes if present
            if (var_name.startswith('"') and var_name.endswith('"')) or \
               (var_name.startswith("'") and var_name.endswith("'")):
                var_name = var_name[1:-1]

            return str(self.env.locals.get(var_name, f"Error: Variable '{var_name}' not found"))

        return None

    def completion(self, prompt: str) -> str:
        """
        Main RLM loop.
        """
        messages = [{"role": "system", "content": RLM_SYSTEM_PROMPT}]
        messages.append({"role": "user", "content": prompt})

        print(f"--- Starting RLM for: {prompt} ---")

        for i in range(self.max_iterations):
            print(f"Iteration {i+1}: Calling LLM...")
            response = self.client.completion(messages)
            messages.append({"role": "assistant", "content": response})
            print(f"LLM Response:\n{response}\n")

            # Check for final answer in response
            final_answer = self._find_final_answer(response)
            if final_answer:
                print(f"Found Final Answer: {final_answer}")
                return final_answer

            # Extract and execute code
            code_blocks = self._parse_code_blocks(response)
            if not code_blocks:
                print("No code blocks found.")
                continue

            execution_output = ""
            for code in code_blocks:
                print(f"Executing Code:\n{code}")
                result = self.env.execute_code(code)
                output = f"Execution Result:\nSTDOUT:\n{result['stdout']}\nSTDERR:\n{result['stderr']}"
                if result['error']:
                    output += f"\nERROR:\n{result['error']}"
                execution_output += output + "\n"
                print(f"Execution Output:\n{output}")

            messages.append({"role": "user", "content": execution_output})

        return "Max iterations reached."
