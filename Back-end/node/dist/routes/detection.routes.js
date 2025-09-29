"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const multer_1 = __importDefault(require("multer"));
const Detection_controller_1 = require("../controllers/Detection.controller");
const auth_1 = require("../middleware/auth");
const upload = (0, multer_1.default)();
const router = (0, express_1.Router)();
/**
 * @swagger
 * /detection/detect:
 *   post:
 *     summary: Enviar imagem para detecção de lixo
 *     tags:
 *       - Detection
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         multipart/form-data:
 *           schema:
 *             type: object
 *             properties:
 *               image:
 *                 type: string
 *                 format: binary
 *                 description: Arquivo de imagem
 *     responses:
 *       200:
 *         description: Detecção bem-sucedida
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 detectionId:
 *                   type: string
 *                   example: "68d80de073b1c7446f3d2251"
 *                 imageBase64:
 *                   type: string
 *                   example: "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ..."
 *                 result:
 *                   type: object
 *                   example: { "confidence": 0.45, "material": "orgânico", "reciclavel": false, "tipo": "lixo" }
 *       400:
 *         description: Nenhuma imagem enviada
 *       500:
 *         description: Erro ao processar imagem
 */
router.post('/detect', auth_1.authenticateToken, upload.single('image'), Detection_controller_1.detectWaste);
exports.default = router;
