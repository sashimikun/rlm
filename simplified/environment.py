import sys
import io
import traceback
from typing import Any, Dict
from .llm import LLMClient

class Environment:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
        # Combine globals and locals into a single namespace for the REPL
        # This ensures recursive functions and global variable access work as expected
        self.namespace: Dict[str, Any] = {
            "llm_query": self._llm_query,
            "print": print,
        }

    def _llm_query(self, prompt: str) -> str:
        """
        The function injected into the environment to allow the code to call the LLM.
        """
        return self.llm_client.completion(prompt)

    def execute(self, code: str) -> str:
        """
        Executes the provided Python code string in the environment.
        Returns the captured stdout + any errors.
        """
        # Capture stdout
        old_stdout = sys.stdout
        redirected_output = io.StringIO()
        sys.stdout = redirected_output

        result_output = ""

        try:
            # Pass the single namespace as both globals and locals (or just globals)
            exec(code, self.namespace)

        except Exception:
            traceback.print_exc(file=redirected_output)
        finally:
            sys.stdout = old_stdout
            result_output = redirected_output.getvalue()

        return result_output

    def get_variable(self, name: str) -> Any:
        """Retrieves a variable from the environment."""
        return self.namespace.get(name)
