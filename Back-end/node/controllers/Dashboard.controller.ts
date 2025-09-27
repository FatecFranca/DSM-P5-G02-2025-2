import { Request, Response } from 'express';
import Detection from '../models/Detection';

export const getLast10Detections = async (req: Request, res: Response) => {
  const user = (req as any).user;
  try {
    const detections = await Detection.find({ userId: user._id })
      .sort({ createdAt: -1 })
      .limit(10)
      .select('result status createdAt');
    res.json(detections);
  } catch (error) {
    res.status(500).json({ error: 'Erro ao buscar últimas detecções' });
  }
};

export const getFullHistory = async (req: Request, res: Response) => {
  const user = (req as any).user;
  try {
    const detections = await Detection.find({ userId: user._id }).sort({ createdAt: -1 });
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
  } catch (error) {
    res.status(500).json({ error: 'Erro ao buscar histórico' });
  }
};

export const getDetectionDetails = async (req: Request, res: Response) => {
  const user = (req as any).user;
  const { id } = req.params;
  try {
    const detection = await Detection.findOne({ _id: id, userId: user._id });
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
  } catch (error) {
    res.status(500).json({ error: 'Erro ao buscar detalhes' });
  }
};