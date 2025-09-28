import express from 'express';
import http from 'http';
import axios from 'axios';
import multer from 'multer';
import admin from 'firebase-admin';
import mongoose from 'mongoose';
const serviceAccount = require('./config/firebase-key.json');


// Rota de login papum
import authRoutes from './routes/auth.routes';
import detectionRoutes from './routes/detection.routes';
import dashboardRoutes from './routes/dashboard.routes';

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount)
});

const app = express();
const server = http.createServer(app);

const PORT = process.env.PORT || 3000;

app.use(express.json());

app.get('/', (req, res) => {
  res.send('Back-end Node.js com TypeScript rodando! 🚀');
});

app.use('/auth', authRoutes);
app.use('/detection', detectionRoutes);
app.use('/dashboard', dashboardRoutes);

server.listen(PORT, () => {
  console.log(`Servidor Node.js rodando na porta ${PORT}`);
});

mongoose.connect('mongodb://localhost:27017/pi')
  .then(() => console.log('MongoDB conectado'))
  .catch(err => console.error(err));