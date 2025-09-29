"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = __importDefault(require("express"));
const http_1 = __importDefault(require("http"));
const firebase_admin_1 = __importDefault(require("firebase-admin"));
const mongoose_1 = __importDefault(require("mongoose"));
const swagger_jsdoc_1 = __importDefault(require("swagger-jsdoc"));
const swagger_ui_express_1 = __importDefault(require("swagger-ui-express"));
const path_1 = __importDefault(require("path"));
const serviceAccount = require("./config/firebase-key.json");
// Rota de login papum
const auth_routes_1 = __importDefault(require("./routes/auth.routes"));
const detection_routes_1 = __importDefault(require("./routes/detection.routes"));
const dashboard_routes_1 = __importDefault(require("./routes/dashboard.routes"));
firebase_admin_1.default.initializeApp({
    credential: firebase_admin_1.default.credential.cert(serviceAccount),
});
const app = (0, express_1.default)();
const server = http_1.default.createServer(app);
const PORT = process.env.PORT || 3000;
app.use(express_1.default.json());
app.get("/", (req, res) => {
    res.send("Back-end Node.js com TypeScript rodando! 🚀");
});
app.use("/auth", auth_routes_1.default);
app.use("/detection", detection_routes_1.default);
app.use("/dashboard", dashboard_routes_1.default);
server.listen(PORT, () => {
    console.log(`Servidor Node.js rodando na porta ${PORT}`);
});
mongoose_1.default
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
        security: [
            {
                bearerAuth: []
            }
        ]
    },
    apis: [path_1.default.resolve(__dirname, __dirname.includes("dist") ? "./routes/*.js" : "./routes/*.ts")],
};
const swaggerDocs = (0, swagger_jsdoc_1.default)(swaggerOptions);
app.use("/api-docs", swagger_ui_express_1.default.serve, swagger_ui_express_1.default.setup(swaggerDocs));
