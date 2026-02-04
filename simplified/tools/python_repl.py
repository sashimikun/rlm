import sys
import io
import contextlib
import traceback
from typing import Callable, Any, Dict

class PythonREPL:
    def __init__(self, globals_dict: Dict[str, Any] = None):
        self.globals = globals_dict if globals_dict is not None else {}
        self.locals = {}

    def register_function(self, name: str, func: Callable):
        """Register a function to be available in the REPL."""
        self.globals[name] = func

    def run(self, code: str) -> str:
        """
        Executes python code and returns stdout/stderr.
        """
        # Capture stdout/stderr
        stdout_buf = io.StringIO()
        stderr_buf = io.StringIO()

        with contextlib.redirect_stdout(stdout_buf), contextlib.redirect_stderr(stderr_buf):
            try:
                # We share globals/locals to maintain state across calls
                exec(code, self.globals, self.locals)
            except Exception:
                traceback.print_exc(file=stderr_buf)

        output = stdout_buf.getvalue()
        errors = stderr_buf.getvalue()

        result = output
        if errors:
            result += f"\nErrors:\n{errors}"

        return result.strip()
