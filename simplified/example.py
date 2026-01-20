from simplified.client import BaseClient
from simplified.rlm import RLM


class SmartMockClient(BaseClient):
    def __init__(self):
        super().__init__()
        self.step = 0

    def completion(self, prompt: str) -> str:
        # Simple state machine to simulate a reasoned response

        if "Count the words in the context" in prompt and self.step == 0:
            self.step += 1
            return """I need to count the words in the `context` variable. I will write a Python script to do this.

```repl
words = context.split()
count = len(words)
print(f"Word count is: {count}")
```
"""

        if "Word count is: 5" in prompt and self.step == 1:
            self.step += 1
            return """I have the word count.

FINAL ANSWER: 5
"""

        return "I am confused. Please help."


def main():
    # Setup
    client = SmartMockClient()
    rlm = RLM(client)

    # Data
    context = "apple banana cherry date elderberry"  # 5 words
    rlm.load_context(context)

    # Run
    query = "Count the words in the context."
    result = rlm.run(query)

    print(f"\nResult: {result}")


if __name__ == "__main__":
    main()
