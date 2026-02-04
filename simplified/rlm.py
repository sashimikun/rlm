import re

from .client import BaseClient
from .env import LocalEnv
from .prompts import SYSTEM_PROMPT


class RLM:
    def __init__(self, client: BaseClient, max_iterations: int = 10):
        self.client = client
        self.max_iterations = max_iterations
        self.env = LocalEnv(client)
        self.history = []

    def load_context(self, context_data):
        self.env.load_context(context_data)

    def extract_code(self, response: str) -> list[str]:
        pattern = r"```repl\s*\n(.*?)\n```"
        return re.findall(pattern, response, re.DOTALL)

    def check_for_final_answer(self, stdout: str) -> str | None:
        if "FINAL ANSWER:" in stdout:
            return stdout.split("FINAL ANSWER:")[1].strip()
        return None

    def run(self, user_query: str) -> str:
        # Reset history
        self.history = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Here is the query: {user_query}"},
        ]

        print(f"Starting RLM with query: {user_query}")

        for i in range(self.max_iterations):
            print(f"\n--- Iteration {i + 1} ---")

            # Construct prompt from history
            # (Simple concatenation for this demo, usually would use list of messages)
            # For BaseClient simple interface, we might just join them
            full_prompt = "\n".join(
                [f"{msg['role'].upper()}: {msg['content']}" for msg in self.history]
            )
            full_prompt += "\nASSISTANT:"

            # Get completion
            response = self.client.completion(full_prompt)
            print(f"LLM Response:\n{response}")

            self.history.append({"role": "assistant", "content": response})

            # Extract code
            code_blocks = self.extract_code(response)

            if not code_blocks:
                print("No code blocks found. Asking to continue or finalize.")
                # If no code, maybe it just answered? Check response text for final answer?
                # For this simplified version, let's assume it must use code or say FINAL ANSWER in text
                if "FINAL ANSWER:" in response:
                    return response.split("FINAL ANSWER:")[1].strip()

                self.history.append(
                    {
                        "role": "user",
                        "content": "You didn't provide any code. If you have the answer, please say 'FINAL ANSWER: <answer>'. Otherwise, use code to make progress.",
                    }
                )
                continue

            # Execute code
            for code in code_blocks:
                print(f"Executing code:\n{code}")
                result = self.env.execute(code)
                output = f"STDOUT:\n{result['stdout']}\nSTDERR:\n{result['stderr']}"
                print(f"Execution Result:\n{output}")

                # Check for final answer in stdout
                final_ans = self.check_for_final_answer(result["stdout"])
                if final_ans:
                    return final_ans

                # Append result to history
                self.history.append(
                    {"role": "user", "content": f"Code execution result:\n{output}"}
                )

        return "Max iterations reached without final answer."
