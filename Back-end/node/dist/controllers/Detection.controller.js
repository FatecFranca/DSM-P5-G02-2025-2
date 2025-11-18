"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.detectWaste = void 0;
const axios_1 = __importDefault(require("axios"));
const Detection_1 = __importDefault(require("../models/Detection"));
// Endpoint do classificador de texto
const FLASK_API_URL_CLASSIFY = process.env.FLASK_CLASSIFY_URL || 'http://localhost:5000/classify';
const detectWaste = async (req, res) => {
    const user = req.user;
    try {
        // Aceita somente JSON { message }
        if (!req.body || !req.body.message) {
            return res.status(400).json({ error: "Campo 'message' é obrigatório" });
        }
        const { message } = req.body;
        const aiResponse = await axios_1.default.post(FLASK_API_URL_CLASSIFY, { message });
        const respData = aiResponse.data || {};
        const result = {
            type: 'text',
            message: respData.message || message,
            is_spam: respData.is_spam === undefined ? null : Boolean(respData.is_spam),
            confidence: respData.confidence
        };
        const detection = new Detection_1.default({
            userId: user._id,
            type: 'text',
            result
        });
        await detection.save();
        return res.json({ detectionId: detection._id, result });
    }
    catch (error) {
        console.error('Erro na detecção:', error);
        res.status(500).json({ error: 'Erro ao processar requisição de detecção' });
    }
};
exports.detectWaste = detectWaste;
