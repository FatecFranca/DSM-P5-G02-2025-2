"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.detectWaste = void 0;
const axios_1 = __importDefault(require("axios"));
const form_data_1 = __importDefault(require("form-data"));
const Detection_1 = __importDefault(require("../models/Detection"));
const FLASK_API_URL = 'http://localhost:5000/detect';
const detectWaste = async (req, res) => {
    const user = req.user;
    try {
        if (!req.file) {
            return res.status(400).json({ error: 'Nenhuma imagem enviada' });
        }
        const imageBuffer = req.file.buffer;
        const imageBase64 = imageBuffer.toString('base64'); // Para salvar no DB
        const formData = new form_data_1.default();
        formData.append('image', imageBuffer, req.file.originalname);
        const aiResponse = await axios_1.default.post(FLASK_API_URL, formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        });
        const detection = new Detection_1.default({
            userId: user._id,
            image: imageBase64,
            result: aiResponse.data
        });
        await detection.save();
        res.json({ detectionId: detection._id, result: aiResponse.data });
    }
    catch (error) {
        console.error('Erro na detecção:', error);
        res.status(500).json({ error: 'Erro ao processar imagem' });
    }
};
exports.detectWaste = detectWaste;
