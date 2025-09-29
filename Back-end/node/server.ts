import express from "express";
import http from "http";
import axios from "axios";
import multer from "multer";
import admin from "firebase-admin";
import mongoose from "mongoose";
import swaggerJsdoc from "swagger-jsdoc";
import swaggerUi from "swagger-ui-express";
import path from "path";

const serviceAccount = require("./config/firebase-key.json");

// Rota de login papum
import authRoutes from "./routes/auth.routes";
import detectionRoutes from "./routes/detection.routes";
import dashboardRoutes from "./routes/dashboard.routes";

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount),
});

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

server.listen(PORT, () => {
  console.log(`Servidor Node.js rodando na porta ${PORT}`);
});

mongoose
  .connect("mongodb://localhost:27017/pi")
  .then(() => console.log("MongoDB conectado"))
  .catch((err) => console.error(err));

const swaggerOptions = {
  swaggerDefinition: {
    openapi: '3.0.0',
    info: {
      title: 'RECICLAAI - API',
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
  apis: [path.resolve(__dirname, "./routes/*.ts")],

};
const swaggerDocs = swaggerJsdoc(swaggerOptions);
app.use("/api-docs", swaggerUi.serve, swaggerUi.setup(swaggerDocs));
