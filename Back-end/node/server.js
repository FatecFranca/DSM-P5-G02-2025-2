const express = require('express');
const http = require('http');
const axios = require('axios');
const multer = require('multer');
const admin = require('firebase-admin');
const serviceAccount = require('./config/firebase-key.json');
const mongose = require('mongoose');


// Rota de login papum
const authRoutes = require('./routes/auth.routes');
// Rota de aiaiaiai
const detectionRoutes = require('./routes/detection.routes');
const dashboardRoutes = require('./routes/dashboard.routes');

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount)
});

const app = express();
const server = http.createServer(app);



const PORT = process.env.PORT || 3000;


app.use(express.json());

app.get('/', (req, res) => {
  res.send('Back-end Node.js rodando! Use WebSocket para detecção em tempo real.');
});

app.use('/auth', authRoutes);
app.use('/detection', detectionRoutes);
app.use('/dashboard', dashboardRoutes);



server.listen(PORT, () => {
  console.log(`Servidor Node.js rodando na porta ${PORT}`);
});

mongose.connect('mongodb://localhost:27017/pi', {  // Substitua 'seu_banco' pelo nome do banco
  
  useUnifiedTopology: true
}).then(() => console.log('MongoDB conectado')).catch(err => console.error(err));