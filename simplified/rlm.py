from typing import List, Dict, Any
from .llm import LLMClient
from .environment import Environment
from .utils import parse_code_blocks

SYSTEM_PROMPT = """You are an intelligent agent that can write and execute Python code.
You can use the `llm_query(prompt)` function to ask yourself questions or get information.
To answer the user's question, you should:
1. Break down the problem.
2. Write Python code to solve steps.
3. Use `print()` to output results you want to see.
4. When you have the final answer, assign it to the variable `final_answer`.
"""

class RLM:
    def __init__(self, llm_client: LLMClient, max_iterations: int = 10, verbose: bool = False):
        self.llm_client = llm_client
        self.max_iterations = max_iterations
        self.verbose = verbose
        self.environment = Environment(llm_client)
        self.history: List[Dict[str, str]] = []

    def _log(self, message: str):
        if self.verbose:
            print(f"[RLM] {message}")

    def ask(self, question: str) -> str:
        self.history = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question}
        ]

        for i in range(self.max_iterations):
            self._log(f"Iteration {i+1}/{self.max_iterations}")

            # Construct prompt from history
            # In a real system this would be more complex (formatting messages to a string)
            # Here we just concatenate for the simple mock/client
            prompt_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in self.history])

            # 1. Generate
            response = self.llm_client.completion(prompt_str)
            self._log(f"Model Response:\n{response}")
            self.history.append({"role": "assistant", "content": response})

            # 2. Check for code
            code_blocks = parse_code_blocks(response)

            if not code_blocks:
                # If no code, maybe it's just talking. Check if it's done.
                # In this simple version, we assume if no code, it might be the answer.
                # But better to check for the final_answer variable.
                pass

            # 3. Execute
            execution_output = ""
            for code in code_blocks:
                self._log(f"Executing Code:\n{code}")
                output = self.environment.execute(code)
                self._log(f"Execution Output:\n{output}")
                execution_output += f"Output:\n{output}\n"

            # 4. Check for final answer in environment
            final_answer = self.environment.get_variable("final_answer")
            if final_answer:
                self._log(f"Final Answer Found: {final_answer}")
                return str(final_answer)

            # 5. Update history with observation
            if execution_output:
                self.history.append({"role": "user", "content": f"Execution Result:\n{execution_output}"})
            else:
                if not code_blocks:
                     # If no code was executed, and no final answer, prompt to continue or clarify
                     self.history.append({"role": "user", "content": "Please continue. If you have the answer, assign it to `final_answer`."})

        return "Max iterations reached without a final answer."
