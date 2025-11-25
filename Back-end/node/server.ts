import dotenv from "dotenv";
dotenv.config();
import express from "express";
import http from "http";
import axios from "axios";
import admin from "firebase-admin";
import mongoose from "mongoose";
import swaggerJsdoc from "swagger-jsdoc";
import swaggerUi from "swagger-ui-express";
import path from "path";

//const serviceAccount = require("./config/firebase-key.json");

// Rota de login papum
import authRoutes from "./routes/auth.routes";
import detectionRoutes from "./routes/detection.routes";
import dashboardRoutes from "./routes/dashboard.routes";

//admin.initializeApp({
//  credential: admin.credential.cert(serviceAccount),
//});

const app = express();
const server = http.createServer(app);

const PORT = process.env.PORT || 3000;

app.use(express.json());

app.get("/", (req, res) => {
  res.send("Back-end Node.js com TypeScript rodando! 🚀");
});

app.use("/auth", authRoutes);
app.use("/detection", detectionRoutes);
app.use("/dashboard", dashboardRoutes);
app.use(express.json());
app.use(express.static('public'));

server.listen(PORT, () => {
  console.log(`Servidor rodando em http://localhost:${PORT}`);
});
const MONGODB_URI = process.env.MONGO_URI;
if (!MONGODB_URI) {
  throw new Error("MONGO_URI não foi definida no ambiente.");
}

mongoose.connect(MONGODB_URI)
  .then(() => console.log('Conectado ao MongoDB com sucesso!'))
  .catch((err) => console.error('Falha ao conectar ao MongoDB:', err));

const swaggerOptions = {
  swaggerDefinition: {
    openapi: '3.0.0',
    info: {
      title: 'RECICLA_AI - API',
      version: '1.0.0',
      description: 'Documentação da API do projeto de PI',
      contact: {
        name: 'Inácio',
      },
    },
 
    servers: [
      {
        url: `http://localhost:${PORT}`,
        description: 'Servidor local'
      }
    ],
    components: {
      securitySchemes: {
        bearerAuth: {
          type: 'http',
          scheme: 'bearer',
          bearerFormat: 'JWT',
        }
      }
    },
    security: [ //
        {
            bearerAuth: []
        }
    ]
  },
apis: [path.resolve(__dirname, __dirname.includes("dist") ? "./routes/*.js" : "./routes/*.ts")],
};
const swaggerDocs = swaggerJsdoc(swaggerOptions);
app.use("/api-docs", swaggerUi.serve, swaggerUi.setup(swaggerDocs, {

}));
