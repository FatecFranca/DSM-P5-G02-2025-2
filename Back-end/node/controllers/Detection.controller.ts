import { Request, Response } from 'express';
import axios from 'axios';
import FormData from 'form-data';
import Detection from '../models/Detection';

const FLASK_API_URL = 'http://localhost:5000/detect';

export const detectWaste = async (req: Request, res: Response) => {
  const user = (req as any).user;

  try {
    if (!req.file) {
      return res.status(400).json({ error: 'Nenhuma imagem enviada' });
    }

    const imageBuffer = req.file.buffer;
    const imageBase64 = imageBuffer.toString('base64');  // Para salvar no DB

    const formData = new FormData();
    formData.append('image', imageBuffer, req.file.originalname);

    const aiResponse = await axios.post(FLASK_API_URL, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });

    const detection = new Detection({
      userId: user._id,
      image: imageBase64,
      result: aiResponse.data
    });
    await detection.save();

    res.json({ detectionId: detection._id, result: aiResponse.data });
  } catch (error) {
    console.error('Erro na detecção:', error);
    res.status(500).json({ error: 'Erro ao processar imagem' });
  }
};