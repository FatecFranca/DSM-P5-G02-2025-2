"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const Dashboard_controller_1 = require("../controllers/Dashboard.controller");
const auth_1 = require("../middleware/auth");
const router = (0, express_1.Router)();
/**
 * @swagger
 * /dashboard/last10:
 *   get:
 *     summary: Obter últimas 10 detecções do usuário
 *     tags:
 *       - Dashboard
 *     security:
 *       - bearerAuth: []
 *     responses:
 *       200:
 *         description: Lista das últimas 10 detecções
 *         content:
 *           application/json:
 *             schema:
 *               type: array
 *               items:
 *                 type: object
 *                 properties:
 *                   result:
 *                     type: object
 *                     example: { "is_spam": 1, "message": "Exemplo de texto" }
 *                   status:
 *                     type: string
 *                     example: "sucesso"
 *                   createdAt:
 *                     type: string
 *                     format: date-time
 *       500:
 *         description: Erro interno
 */
router.get('/last10', auth_1.authenticateToken, Dashboard_controller_1.getLast10Detections);
/**
 * @swagger
 * /dashboard/history:
 *   get:
 *     summary: Obter histórico completo com médias
 *     tags:
 *       - Dashboard
 *     security:
 *       - bearerAuth: []
 *     responses:
 *       200:
 *         description: Histórico completo e médias
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 total:
 *                   type: integer
 *                   example: 25
 *                 detections:
 *                   type: array
 *                   items:
 *                     type: object
 *                 medias:
 *                   type: object
 *                   properties:
 *                     spamPercent:
 *                       type: string
 *                       example: "12.00%"
 *       500:
 *         description: Erro interno
 */
router.get('/history', auth_1.authenticateToken, Dashboard_controller_1.getFullHistory);
/**
 * @swagger
 * /dashboard/details/{id}:
 *   get:
 *     summary: Obter detalhes de uma detecção específica
 *     tags:
 *       - Dashboard
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *         description: ID da detecção
 *         example: "68d80de073b1c7446f3d2251"
 *     responses:
 *       200:
 *         description: Detalhes da detecção
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 detectionId:
 *                   type: string
 *                 result:
 *                   type: object
 *                   example: { "is_spam": 1, "message": "Exemplo de texto" }
 *                 status:
 *                   type: string
 *                   example: "sucesso"
 *                 createdAt:
 *                   type: string
 *                   format: date-time
 *       404:
 *         description: Detecção não encontrada
 *       500:
 *         description: Erro interno
 */
router.get('/details/:id', auth_1.authenticateToken, Dashboard_controller_1.getDetectionDetails);
exports.default = router;
