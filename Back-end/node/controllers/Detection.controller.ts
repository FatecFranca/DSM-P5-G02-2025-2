import { Request, Response } from 'express';
import axios from 'axios';
import FormData from 'form-data';
import Detection from '../models/Detection';

// Endpoints configuráveis via env para permitir alternar entre classify e detect
const FLASK_API_URL_CLASSIFY = process.env.FLASK_CLASSIFY_URL || 'http://localhost:5000/classify';
const FLASK_API_URL_DETECT = process.env.FLASK_DETECT_URL || 'http://localhost:5000/detect';

export const detectWaste = async (req: Request, res: Response) => {
  const user = (req as any).user;

  try {
    // Caso o cliente envie um JSON com { message: "..." } -> usar classificador de texto (IA atual)
    if (req.body && req.body.message) {
      const { message } = req.body;

      const aiResponse = await axios.post(FLASK_API_URL_CLASSIFY, { message });
      // IA Flask atual retorna: { message: original, is_spam: 0|1 }
      const respData = aiResponse.data || {};

      const result = {
        type: 'text',
        message: respData.message || message,
        is_spam: respData.is_spam === undefined ? null : Boolean(respData.is_spam),
        // pode haver confidence no futuro
        confidence: respData.confidence
      } as any;

      const detection = new Detection({
        userId: user._id,
        // preservar campo image se veio (p.ex. mobile pode enviar também imagem e message)
        image: req.file ? req.file.buffer.toString('base64') : undefined,
        type: 'text',
        result
      });
      await detection.save();

      return res.json({ detectionId: detection._id, result });
    }

    // Caso envie imagem multipart/form-data -> tentar encaminhar para endpoint de detecção de imagens
    if (req.file) {
      // manter comportamento antigo: enviar multipart para /detect
      const imageBuffer = req.file.buffer;
      const imageBase64 = imageBuffer.toString('base64'); // Para salvar no DB

      const formData = new FormData();
      formData.append('image', imageBuffer, req.file.originalname);

      // Tentar chamar endpoint de detecção de imagens. Se endpoint não existir, retornaremos mensagem adequada.
      try {
        const aiResponse = await axios.post(FLASK_API_URL_DETECT, formData, {
          headers: formData.getHeaders ? formData.getHeaders() : { 'Content-Type': 'multipart/form-data' }
        });

        const detection = new Detection({
          userId: user._id,
          image: imageBase64,
          type: 'image',
          result: aiResponse.data
        });
        await detection.save();

        return res.json({ detectionId: detection._id, result: aiResponse.data });
      } catch (err) {
        console.warn('Endpoint de detecção de imagens indisponível, envie texto {message} ou implemente /detect no Flask');
        // Salvar registro parcial indicando falha ao processar imagem
        const detection = new Detection({
          userId: user._id,
          image: imageBase64,
          type: 'image',
          result: { error: 'image-detection-unavailable' }
        });
        await detection.save();

        return res.status(501).json({ error: 'Endpoint de detecção de imagens indisponível. Envie JSON { message } para classificar texto.' });
      }
    }

    return res.status(400).json({ error: "Envie 'message' em JSON ou um arquivo 'image' multipart/form-data" });
  } catch (error) {
    console.error('Erro na detecção:', error);
    res.status(500).json({ error: 'Erro ao processar requisição de detecção' });
  }
};