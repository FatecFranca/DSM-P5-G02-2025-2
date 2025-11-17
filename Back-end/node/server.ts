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

server.listen(PORT, "0.0.0.0", () => {
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
 customCss: `
    .swagger-ui .topbar {
      background: #000000;
      height: 70px;
      border-bottom: 2px solid #333;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
      position: relative;
    }
    .swagger-ui .topbar::before {
      content: '';
      position: absolute;
      left: 10px;
      top: 50%;
      transform: translateY(-50%);
      height: 90px;
      width: 200px;
      background: url('/logo.png') no-repeat center;
      background-size: contain;
    }
    .swagger-ui .topbar .link {
      display: none;
    }
  `
}));
