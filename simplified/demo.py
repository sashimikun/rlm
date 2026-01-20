from simple_rlm import SimpleRLM, MockLLM

def main():
    print("=== Test 1: Fibonacci (Code Execution) ===")
    rlm = SimpleRLM(client=MockLLM())
    result = rlm.completion("Calculate the 10th Fibonacci number")
    print(f"Final Result: {result}")

    print("\n=== Test 2: Recursion (LLM calling LLM) ===")
    rlm = SimpleRLM(client=MockLLM())
    result = rlm.completion("Use recursion to find the capital of France")
    print(f"Final Result: {result}")

if __name__ == "__main__":
    main()
