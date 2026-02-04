import sys
import io
import contextlib
from typing import Dict, Any, Callable, List

class SimpleEnv:
    """
    A simple environment for executing Python code with a persistent state.
    It allows injecting a callback function `llm_query` to enable recursion.
    """
    def __init__(self, llm_query_callback: Callable[[str], str]):
        self.locals: Dict[str, Any] = {}
        self.llm_query_callback = llm_query_callback

    def _llm_query(self, prompt: str) -> str:
        """
        The function that will be exposed to the Python environment as `llm_query`.
        """
        return self.llm_query_callback(prompt)

    def _final_answer(self, answer: Any) -> Any:
        """
        Helper to explicitly return a final answer from code.
        """
        return answer

    def execute_code(self, code: str) -> Dict[str, Any]:
        """
        Executes the provided code string.
        Returns a dictionary containing stdout, stderr, and the updated locals.
        """
        stdout_buf = io.StringIO()
        stderr_buf = io.StringIO()

        # Prepare the environment
        # We inject llm_query and FINAL_ANSWER
        exec_globals = {
            "__builtins__": __builtins__,
            "llm_query": self._llm_query,
            "print": print, # Ensure print works
        }

        # We copy locals to avoid pollution if we want strict separation,
        # but here we want persistence so we use self.locals.
        # However, exec takes two dicts: globals and locals.

        with contextlib.redirect_stdout(stdout_buf), contextlib.redirect_stderr(stderr_buf):
            try:
                exec(code, exec_globals, self.locals)
                error = None
            except Exception as e:
                import traceback
                error = traceback.format_exc()
                # Print error to stderr so it's captured
                print(error, file=stderr_buf)

        return {
            "stdout": stdout_buf.getvalue(),
            "stderr": stderr_buf.getvalue(),
            "locals": self.locals,
            "error": error
        }
