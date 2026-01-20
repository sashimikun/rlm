import sys
import io
import contextlib
from typing import Callable, Any

class LocalEnv:
    def __init__(self, llm_callback: Callable[[str], str]):
        self.globals = {
            "__builtins__": __builtins__, # In a real secure env, this should be restricted
            "llm_query": llm_callback,
            "FINAL_VAR": self._final_var
        }
        self.locals = {}

    def _final_var(self, value):
        return value

    @contextlib.contextmanager
    def _capture_output(self):
        new_out, new_err = io.StringIO(), io.StringIO()
        old_out, old_err = sys.stdout, sys.stderr
        try:
            sys.stdout, sys.stderr = new_out, new_err
            yield new_out, new_err
        finally:
            sys.stdout, sys.stderr = old_out, old_err

    def execute(self, code: str) -> dict:
        stdout = ""
        stderr = ""

        with self._capture_output() as (out, err):
            try:
                # Merge globals and locals for execution
                exec_globals = self.globals.copy()
                exec_globals.update(self.locals)

                exec(code, exec_globals)

                # Update locals with any new variables
                for k, v in exec_globals.items():
                    if k not in self.globals and not k.startswith('_'):
                        self.locals[k] = v

            except Exception as e:
                # print(e, file=sys.stderr) # This would go to the captured stderr
                err.write(f"{type(e).__name__}: {str(e)}")

        stdout = out.getvalue()
        stderr = err.getvalue()

        return {
            "stdout": stdout,
            "stderr": stderr,
            "locals": {k: repr(v) for k, v in self.locals.items()}
        }
