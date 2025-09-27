import { Router } from 'express';
import multer from 'multer';

import { detectWaste } from '../controllers/Detection.controller';
import { authenticateToken } from '../middleware/auth';
const upload = multer();
const router = Router();
/**
 * @swagger
 * /detection/detect:
 *   post:
 *     summary: Enviar imagem para detecção de lixo
 *     tags: [Detection]
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
 *                 description: Arquivo de imagem (ex.: JPG, PNG)
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
 *                 result:
 *                   type: object
 *                   example: { "confidence": 0.45, "material": "orgânico", "reciclavel": false, "tipo": "lixo" }
 *       400:
 *         description: Nenhuma imagem enviada
 *       500:
 *         description: Erro ao processar imagem
 */
router.post('/detect', authenticateToken, upload.single('image'), detectWaste);

module.exports = router;