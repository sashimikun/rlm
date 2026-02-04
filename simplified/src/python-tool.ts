import { tool } from 'ai';
import { z } from 'zod';
import { PythonShell } from 'python-shell';
import path from 'path';
import { fileURLToPath } from 'url';

// Fix for __dirname in ESM
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export class PythonEnvironment {
  private shell: PythonShell;
  private pendingResolves: ((val: any) => void)[] = [];

  constructor(port: number) {
    const scriptPath = path.join(__dirname, 'runner.py');
    this.shell = new PythonShell(scriptPath, {
      args: [port.toString()],
      mode: 'json',
      pythonOptions: ['-u'], // Unbuffered
    });

    this.shell.on('message', (message: any) => {
      const resolve = this.pendingResolves.shift();
      if (resolve) {
        resolve(message);
      }
    });

    this.shell.on('error', (err) => {
      console.error('Python Shell Error:', err);
    });
  }

  execute(code: string): Promise<{ stdout: string; stderr: string }> {
    return new Promise((resolve) => {
      this.pendingResolves.push(resolve);
      this.shell.send({ code } as any);
    });
  }

  stop() {
    this.shell.end((err) => {
      if (err) console.error('Error stopping shell:', err);
    });
  }
}

export const createPythonTool = (env: PythonEnvironment) => {
  return tool({
    description: 'Execute Python code. Variables are persistent across calls. Use print() to output results.',
    parameters: z.object({
      code: z.string().describe('The python code to execute'),
    }),
    execute: async ({ code }) => {
      try {
        const result = await env.execute(code);
        return {
           output: result.stdout,
           error: result.stderr ? result.stderr : undefined
        };
      } catch (err: any) {
        return { error: err.message || String(err) };
      }
    },
  });
};
