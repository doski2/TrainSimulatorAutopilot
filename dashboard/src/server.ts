import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import { createServer } from 'http';
import { Server } from 'socket.io';
import path from 'path';
import { SignalingDataService } from './services/SignalingDataService';
import { apiRoutes } from './routes/api';

const app = express();
const server = createServer(app);
const io = new Server(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"]
  }
});

const PORT = process.env.PORT || 3000;

// Middleware
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net", "https://cdn.socket.io", "https://cdnjs.cloudflare.com"],
      styleSrc: ["'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net", "https://cdnjs.cloudflare.com"],
      connectSrc: ["'self'", "ws://localhost:3000", "wss://localhost:3000", "https://cdn.jsdelivr.net"],
      imgSrc: ["'self'", "data:", "https://"],
      fontSrc: ["'self'", "https://cdnjs.cloudflare.com"]
    }
  }
}));
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, '../public')));

// Servicios
const signalingService = new SignalingDataService();

// Rutas API
app.use('/api', apiRoutes(signalingService));

// Ruta principal
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, '../public/index.html'));
});

// WebSocket connections
io.on('connection', (socket) => {
  console.log('Cliente conectado:', socket.id);

  // Enviar datos iniciales
  socket.emit('initial-data', signalingService.getAllData());

  // Suscribirse a actualizaciones
  const updateInterval = setInterval(() => {
    const data = signalingService.getAllData();
    socket.emit('data-update', data);
  }, 1000); // Actualizar cada segundo

  socket.on('disconnect', () => {
    console.log('Cliente desconectado:', socket.id);
    clearInterval(updateInterval);
  });

  // Manejar comandos desde el dashboard
  socket.on('command', (command: any) => {
    console.log('Comando recibido:', command);
    // Aquí se podría integrar con el sistema Python
  });
});

server.listen(PORT, () => {
  console.log(`🚂 Dashboard del Train Simulator corriendo en http://localhost:${PORT}`);
});

export { app, server, io };