import 'dotenv/config';
import { generateText } from 'ai';
import { openai } from '@ai-sdk/openai';
import { CallbackServer } from './server.js';
import { PythonEnvironment, createPythonTool } from './python-tool.js';

// The Main RLM Function
async function rlm(prompt: string, depth = 0, maxDepth = 3): Promise<string> {
  // Fallback to standard LM call if max depth reached
  if (depth >= maxDepth) {
    console.log(`[Depth ${depth}] Max depth reached. Fallback to standard generation.`);
    const result = await generateText({
      model: openai('gpt-4o'),
      prompt,
    });
    return result.text;
  }

  const server = new CallbackServer();
  const port = await server.start();

  // Set handler for recursion
  server.setHandler(async (subPrompt, subModel) => {
      console.log(`[Depth ${depth}] Recursing with prompt: "${subPrompt.substring(0, 50)}..."`);
      // Recursively call rlm
      return await rlm(subPrompt, depth + 1, maxDepth);
  });

  const env = new PythonEnvironment(port);

  try {
      const result = await generateText({
          model: openai('gpt-4o'),
          system: `You are a Recursive Language Model.
You have access to a Python REPL.
You can execute code to solve problems.
You can also call yourself recursively using the function \`llm_query(prompt)\` inside the Python code.
Use \`llm_query\` when you need to delegate a sub-task or ask a general question that requires knowledge you don't have immediately available or solvable by code.
Variables are persistent.
When you have the final answer, simply state it.`,
          prompt,
          tools: {
              execute_python: createPythonTool(env),
          },
          maxSteps: 10, // The Loop
      });

      return result.text;
  } finally {
      env.stop();
      server.stop();
  }
}

// Entry point
async function main() {
    const prompt = process.argv[2] || "Calculate the 10th fibonacci number, then ask the LLM for a fun fact about that number using llm_query().";
    console.log(`Starting RLM with prompt: "${prompt}"`);
    try {
        const answer = await rlm(prompt);
        console.log("\nFinal Answer:\n", answer);
    } catch (e) {
        console.error("Error:", e);
    }
}

main();
