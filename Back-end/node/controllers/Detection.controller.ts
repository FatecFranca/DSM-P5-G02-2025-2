import { Request, Response } from 'express';
import axios from 'axios';
import Detection from '../models/Detection';

// Endpoint do classificador de texto
const FLASK_API_URL_CLASSIFY = process.env.FLASK_CLASSIFY_URL || 'http://backend-ia:5000/classify';

export const detectWaste = async (req: Request, res: Response) => {
  const user = (req as any).user;

  try {
    // Aceita somente JSON { message }
    if (!req.body || !req.body.message) {
      return res.status(400).json({ error: "Campo 'message' é obrigatório" });
    }

    const { message } = req.body;
    const aiResponse = await axios.post(FLASK_API_URL_CLASSIFY, { message });
    const respData = aiResponse.data || {};

    const result = {
      type: 'text',
      message: respData.message || message,
      is_spam: respData.is_spam === undefined ? null : Boolean(respData.is_spam),
      confidence: respData.confidence
    } as any;

    const detection = new Detection({
      userId: user._id,
      type: 'text',
      result
    });
    await detection.save();

    return res.json({ detectionId: detection._id, result });
  } catch (error) {
    console.error('Erro na detecção:', error);
    res.status(500).json({ error: 'Erro ao processar requisição de detecção' });
  }
};