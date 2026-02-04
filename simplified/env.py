import io
import traceback
from contextlib import redirect_stderr, redirect_stdout


class LocalEnv:
    def __init__(self, client):
        self.client = client
        self.globals = {}
        self.locals = {}
        self.setup_globals()

    def setup_globals(self):
        self.globals = {
            "__builtins__": __builtins__,
            "llm_query": self._llm_query,
            "llm_query_batched": self._llm_query_batched,
            "print": print,  # Ensure print is available
        }
        self.locals = {}

    def _llm_query(self, prompt: str) -> str:
        """Called by the executing code to query the LLM."""
        print(f"[Env] Executing recursive LLM query: {prompt[:50]}...")
        return self.client.completion(prompt)

    def _llm_query_batched(self, prompts: list[str]) -> list[str]:
        """Called by the executing code to query the LLM in batch."""
        # For simplicity, just loop sequentially in this simplified version
        return [self._llm_query(p) for p in prompts]

    def load_context(self, context_data):
        """Loads data into the 'context' variable."""
        self.locals["context"] = context_data

    def execute(self, code: str) -> dict:
        """
        Executes code and returns a dict with stdout, stderr, and success status.
        """
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()

        # Merge globals and locals for execution context
        # In a real REPL, we want persistent locals.
        # Python's exec(code, globals, locals) updates locals in place.

        # We need to ensure globals has __builtins__
        if "__builtins__" not in self.globals:
            self.globals["__builtins__"] = __builtins__

        success = True
        try:
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                exec(code, self.globals, self.locals)
        except Exception:
            traceback.print_exc(file=stderr_capture)
            success = False

        return {
            "stdout": stdout_capture.getvalue(),
            "stderr": stderr_capture.getvalue(),
            "success": success,
            "locals": self.locals,  # For inspection if needed
        }
