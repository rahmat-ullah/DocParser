const { createServer } = require('http');
const { parse } = require('url');
const next = require('next');
const SocketIOServer = require('./lib/socketServer');

const dev = process.env.NODE_ENV !== 'production';
const app = next({ dev });
const handle = app.getRequestHandler();

let socketServer;

app.prepare().then(() => { 
  const server = createServer((req, res) => {
    const parsedUrl = parse(req.url, true);
    handle(req, res, parsedUrl);
  });

  // Initialize Socket.IO server
  socketServer = new SocketIOServer(server);

  // Make socketServer available globally for API routes
  global.socketServer = socketServer;

  server.listen(3000, err => {
    if (err) throw err;
    console.log('> Ready on http://localhost:3000');
  });
});

