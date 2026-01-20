import contextlib
import io
import sys
from collections.abc import Callable
from typing import Any


class SimpleEnv:
    """
    A simple execution environment using Python's exec().
    It maintains persistent state across executions via self.locals.
    """
    def __init__(self, llm_query_func: Callable[[str], str] | None = None):
        self.locals: dict[str, Any] = {}
        # We start with standard builtins.
        # In a production environment, you would want to restrict this (like LocalREPL does).
        self.globals: dict[str, Any] = {
            "__builtins__": __builtins__,
        }

        if llm_query_func:
            self.globals["llm_query"] = llm_query_func

    def execute_code(self, code: str) -> dict[str, Any]:
        """
        Executes code and returns a dictionary with results.

        Returns:
            dict: {
                "stdout": str,
                "stderr": str,
                "success": bool
            }
        """
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()

        # We use contextlib to capture stdout/stderr
        # We wrap it in a try/except block to catch execution errors
        with contextlib.redirect_stdout(stdout_capture), contextlib.redirect_stderr(stderr_capture):
            try:
                # Execute the code.
                # Variables assigned in 'code' will be stored in self.locals.
                exec(code, self.globals, self.locals)
                success = True
            except Exception as e:
                # If an error occurs, print it to stderr so it is captured in the result
                # and return success=False
                print(f"{type(e).__name__}: {e}", file=sys.stderr)
                success = False

        return {
            "stdout": stdout_capture.getvalue(),
            "stderr": stderr_capture.getvalue(),
            "success": success,
        }
