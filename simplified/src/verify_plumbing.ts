import { CallbackServer } from './server.js';
import { PythonEnvironment, createPythonTool } from './python-tool.js';

async function verify() {
  console.log("Starting verification...");

  const server = new CallbackServer();
  const port = await server.start();

  server.setHandler(async (prompt) => {
    console.log(`Callback received: ${prompt}`);
    return "Recursion Works!";
  });

  const env = new PythonEnvironment(port);
  const tool = createPythonTool(env);

  const code = `
print("Hello from Python")
response = llm_query("Test Prompt")
print(f"LLM Response: {response}")
`;

  console.log("Executing python code...");
  // Tools in AI SDK 3.1+ are executed by calling .execute() but strictly it's an object with execute method.
  // The 'createPythonTool' returns a CoreTool.
  // We need to check the return type of createPythonTool.
  // ai sdk tool() returns a tool definition object.
  // We can call .execute(args, options).

  const result = await tool.execute({ code }, { toolCallId: 'test', messages: [] });

  console.log("Result:", result);

  env.stop();
  server.stop();
}

verify().catch(console.error);
