from simplified.client import BaseClient
from simplified.rlm import RLM


class RecursiveMockClient(BaseClient):
    def __init__(self):
        super().__init__()
        self.step = 0

    def completion(self, prompt: str) -> str:
        # Check if this is a recursive sub-call
        # Recursive calls in this example start with "Summarize this chunk"
        # and are usually short.
        if prompt.startswith("Summarize this chunk"):
            return "Summary of chunk"

        # Main loop logic
        # Check if we are at step 0 (initial request)
        # We look for the user query at the end or near the end
        if "Summarize the context" in prompt and self.step == 0:
            self.step += 1
            return """The context is long. I should split it and summarize each part using `llm_query`.

```repl
# Split context (simulated split)
parts = ["part1", "part2"]
summaries = []
for p in parts:
    s = llm_query(f"Summarize this chunk: {p}")
    summaries.append(s)

print(f"Summaries: {summaries}")
```
"""

        # Check if we have the result from step 0
        if "Summaries: ['Summary of chunk', 'Summary of chunk']" in prompt and self.step == 1:
            self.step += 1
            return """I have the summaries.

FINAL ANSWER: Combined Summary
"""

        return "I am confused."


def main():
    # Setup
    client = RecursiveMockClient()
    rlm = RLM(client)

    # Data
    context = "A very long text that needs splitting..."
    rlm.load_context(context)

    # Run
    query = "Summarize the context."
    result = rlm.run(query)

    print(f"\nResult: {result}")


if __name__ == "__main__":
    main()
