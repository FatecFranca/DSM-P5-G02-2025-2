"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.getDetectionDetails = exports.getFullHistory = exports.getLast10Detections = void 0;
const Detection_1 = __importDefault(require("../models/Detection"));
const getLast10Detections = async (req, res) => {
    const user = req.user;
    try {
        const detections = await Detection_1.default.find({ userId: user._id })
            .sort({ createdAt: -1 })
            .limit(10)
            .select('result status createdAt');
        res.json(detections);
    }
    catch (error) {
        res.status(500).json({ error: 'Erro ao buscar últimas detecções' });
    }
};
exports.getLast10Detections = getLast10Detections;
const getFullHistory = async (req, res) => {
    const user = req.user;
    try {
        const detections = await Detection_1.default.find({ userId: user._id }).sort({ createdAt: -1 });
        const total = detections.length;
        const reciclavelCount = detections.filter(d => d.result.reciclavel).length;
        const organicoCount = detections.filter(d => d.result.material === 'orgânico').length;
        const mediaReciclavel = total > 0 ? (reciclavelCount / total) * 100 : 0;
        const mediaOrganico = total > 0 ? (organicoCount / total) * 100 : 0;
        res.json({
            total,
            detections,
            medias: {
                reciclavelPercent: mediaReciclavel.toFixed(2) + '%',
                organicoPercent: mediaOrganico.toFixed(2) + '%'
            }
        });
    }
    catch (error) {
        res.status(500).json({ error: 'Erro ao buscar histórico' });
    }
};
exports.getFullHistory = getFullHistory;
const getDetectionDetails = async (req, res) => {
    const user = req.user;
    const { id } = req.params;
    try {
        const detection = await Detection_1.default.findOne({ _id: id, userId: user._id });
        if (!detection) {
            return res.status(404).json({ message: 'Detecção não encontrada' });
        }
        res.json({
            detectionId: detection._id,
            imageBase64: detection.image,
            result: detection.result,
            status: detection.status,
            createdAt: detection.createdAt
        });
    }
    catch (error) {
        res.status(500).json({ error: 'Erro ao buscar detalhes' });
    }
};
exports.getDetectionDetails = getDetectionDetails;
