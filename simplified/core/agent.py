from typing import List, Dict, Any, Optional
from simplified.core.llm import MinimalLLM
from simplified.core.utils import find_code_blocks
from simplified.tools.python_repl import PythonREPL

class ToolLoopAgent:
    def __init__(
        self,
        llm: MinimalLLM,
        system_prompt: str = "You are a helpful assistant. You can write and execute Python code.",
        depth: int = 0,
        max_depth: int = 3,
        max_steps: int = 10
    ):
        self.llm = llm
        self.system_prompt = system_prompt
        self.depth = depth
        self.max_depth = max_depth
        self.max_steps = max_steps

        self.messages: List[Dict[str, Any]] = []

        # Initialize Tool (REPL)
        self.repl = PythonREPL()
        # Inject recursion capability
        self.repl.register_function("llm_query", self._llm_query)

    def _llm_query(self, prompt: str) -> str:
        """
        The recursive function exposed to the REPL.
        """
        import sys
        # Print to real stdout to avoid capture by REPL
        print(f"  [Depth {self.depth}] Recursing with prompt: {prompt}", file=sys.__stdout__)

        if self.depth >= self.max_depth:
            return "Error: Maximum recursion depth reached."

        # Spawn sub-agent
        sub_agent = ToolLoopAgent(
            llm=self.llm,
            system_prompt=self.system_prompt,
            depth=self.depth + 1,
            max_depth=self.max_depth,
            max_steps=self.max_steps
        )
        return sub_agent.run(prompt)

    def run(self, user_prompt: str) -> str:
        """
        Main ToolLoop.
        """
        # Reset messages for a fresh run (or we could persist them)
        self.messages = [
            {"role": "system", "content": f"{self.system_prompt}\nDepth: {self.depth}/{self.max_depth}"},
            {"role": "user", "content": user_prompt}
        ]

        step = 0
        while step < self.max_steps:
            # 1. Generate
            response_text = self.llm.completion(self.messages)

            # Log for visibility
            indent = "  " * self.depth
            # print(f"{indent}Step {step+1}: Model response: {response_text[:50]}...")

            self.messages.append({"role": "assistant", "content": response_text})

            # 2. Parse Tools (Code Blocks)
            code_blocks = find_code_blocks(response_text)

            # 3. Stop Condition: No code blocks -> Final Answer
            # (In a real system we might look for 'Final Answer:', here simplification)
            if not code_blocks:
                return response_text

            # 4. Execute Tools
            for code in code_blocks:
                print(f"{indent}Executing Code:\n{code}")
                result = self.repl.run(code)
                print(f"{indent}Result: {result[:100]}...")

                # Append result as a user message (simulating tool output)
                self.messages.append({
                    "role": "user",
                    "content": f"Execution Result:\n{result}"
                })

            step += 1

        return "Error: Max steps reached without final answer."
