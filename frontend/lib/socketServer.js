const { Server } = require('socket.io');
const Redis = require('redis');

class SocketIOServer {
  constructor(server) {
    this.io = new Server(server, {
      cors: {
        origin: process.env.NODE_ENV === 'production' ? false : ['http://localhost:3000'],
        methods: ['GET', 'POST']
      }
    });

    this.redis = Redis.createClient({
      host: process.env.REDIS_HOST || 'localhost',
      port: process.env.REDIS_PORT || 6379,
    });

    this.setupEventHandlers();
    this.setupRedisSubscription();
  }

  setupEventHandlers() {
    this.io.on('connection', (socket) => {
      console.log('User connected:', socket.id);

      // Handle joining document processing rooms
      socket.on('join-document', (documentId) => {
        socket.join(`document-${documentId}`);
        console.log(`Socket ${socket.id} joined document-${documentId}`);
      });

      // Handle leaving document processing rooms
      socket.on('leave-document', (documentId) => {
        socket.leave(`document-${documentId}`);
        console.log(`Socket ${socket.id} left document-${documentId}`);
      });

      socket.on('disconnect', () => {
        console.log('User disconnected:', socket.id);
      });
    });
  }

  setupRedisSubscription() {
    const subscriber = this.redis.duplicate();
    
    subscriber.on('connect', () => {
      console.log('Redis subscriber connected');
    });

    subscriber.on('error', (err) => {
      console.error('Redis subscriber error:', err);
    });

    // Subscribe to progress events
    subscriber.subscribe('document-progress', (message) => {
      try {
        const progressData = JSON.parse(message);
        this.emitProgress(progressData);
      } catch (error) {
        console.error('Error parsing progress message:', error);
      }
    });
  }

  emitProgress(progressData) {
    const { documentId, stage, progress, message } = progressData;
    
    // Emit to specific document room
    this.io.to(`document-${documentId}`).emit('progress', {
      stage,
      progress,
      message,
      timestamp: new Date().toISOString()
    });

    console.log(`Progress emitted for document ${documentId}: ${stage} - ${progress}%`);
  }

  // Method to emit progress directly (for direct gateway integration)
  emitDirectProgress(documentId, stage, progress, message) {
    this.emitProgress({
      documentId,
      stage,
      progress,
      message
    });
  }

  // Method to get Socket.IO instance
  getIO() {
    return this.io;
  }
}

module.exports = SocketIOServer;
