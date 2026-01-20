import http from 'node:http';

export type QueryHandler = (prompt: string, model?: string) => Promise<string>;

export class CallbackServer {
  private server: http.Server;
  private port: number;
  private handler: QueryHandler | null = null;

  constructor() {
    this.server = http.createServer(async (req, res) => {
      if (req.method === 'POST' && req.url === '/llm-query') {
        let body = '';
        req.on('data', chunk => {
          body += chunk.toString();
        });
        req.on('end', async () => {
          try {
            const data = JSON.parse(body);
            if (this.handler) {
              const result = await this.handler(data.prompt, data.model);
              res.writeHead(200, { 'Content-Type': 'application/json' });
              res.end(JSON.stringify({ result }));
            } else {
              res.writeHead(503, { 'Content-Type': 'application/json' });
              res.end(JSON.stringify({ error: 'Handler not ready' }));
            }
          } catch (e) {
            res.writeHead(500, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: String(e) }));
          }
        });
      } else {
        res.writeHead(404);
        res.end();
      }
    });
    this.port = 0; // Random port
  }

  setHandler(handler: QueryHandler) {
    this.handler = handler;
  }

  start(): Promise<number> {
    return new Promise((resolve, reject) => {
      this.server.listen(0, '127.0.0.1', () => {
        const addr = this.server.address();
        if (typeof addr === 'object' && addr !== null) {
          this.port = addr.port;
          resolve(this.port);
        } else {
          reject(new Error('Failed to get server port'));
        }
      });
    });
  }

  stop() {
    this.server.close();
  }
}
