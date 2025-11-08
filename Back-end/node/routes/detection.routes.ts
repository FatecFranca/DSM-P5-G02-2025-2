import { Router } from 'express';

import { detectWaste } from '../controllers/Detection.controller';
import { authenticateToken } from '../middleware/auth';
const router = Router();

/**
 * @swagger
 * /detection/detect:
 *   post:
 *     summary: Classificar texto (spam) pela IA
 *     tags:
 *       - Detection
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               message:
 *                 type: string
 *                 description: Texto para classificar (campo obrigatório)
 *     responses:
 *       200:
 *         description: Classificação bem-sucedida
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
 *                   example: { "is_spam": 1, "message": "Exemplo de texto" }
 *       400:
 *         description: Campo 'message' obrigatório
 *       500:
 *         description: Erro interno
 */
router.post('/detect', authenticateToken, detectWaste);


export default router;