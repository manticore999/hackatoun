import { mkdirSync, writeFileSync } from 'node:fs';
import { defineConfig, type Plugin } from 'vite';
import react from '@vitejs/plugin-react';

/** Dev only: POST a PNG data URL to /__shot?name=x to save it under SHOT_DIR (default .shots/). */
function devShot(): Plugin {
  return {
    name: 'dev-shot',
    apply: 'serve',
    configureServer(server) {
      const dir = process.env.SHOT_DIR ?? '.shots';
      mkdirSync(dir, { recursive: true });
      server.middlewares.use('/__shot', (req, res) => {
        const name = new URL(req.url ?? '', 'http://x').searchParams.get('name')?.replace(/[^\w-]/g, '') || 'shot';
        let body = '';
        req.on('data', (c) => (body += c));
        req.on('end', () => {
          writeFileSync(`${dir}/${name}.png`, Buffer.from(body.replace(/^data:image\/png;base64,/, ''), 'base64'));
          res.end('ok');
        });
      });
    },
  };
}

export default defineConfig({
  plugins: [react(), devShot()],
  server: { port: 5173, open: false },
});
