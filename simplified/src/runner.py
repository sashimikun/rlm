import sys
import json
import io
import traceback
import urllib.request

# Define llm_query in global scope (placeholder)
def llm_query(prompt, model=None):
    pass

def main(port):
    # Update llm_query with port
    global llm_query
    def _llm_query(prompt, model=None):
        url = f"http://127.0.0.1:{port}/llm-query"
        data = json.dumps({"prompt": prompt, "model": model}).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req) as response:
            resp_data = json.loads(response.read().decode("utf-8"))
            if "error" in resp_data:
                raise Exception(resp_data["error"])
            return resp_data["result"]
    llm_query = _llm_query

    # Globals for execution
    exec_globals = {"llm_query": llm_query}

    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            try:
                req = json.loads(line)
            except json.JSONDecodeError:
                continue

            code = req.get("code", "")

            # Capture stdout/stderr
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            sys.stdout = io.StringIO()
            sys.stderr = io.StringIO()

            try:
                # Execute the code
                exec(code, exec_globals)
            except Exception:
                traceback.print_exc()

            out = sys.stdout.getvalue()
            err = sys.stderr.getvalue()

            sys.stdout = old_stdout
            sys.stderr = old_stderr

            print(json.dumps({"stdout": out, "stderr": err}))
            sys.stdout.flush()

        except Exception:
             # Should not happen if inner try catches everything, but safety first
             pass

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: runner.py <port>")
        sys.exit(1)
    main(int(sys.argv[1]))
