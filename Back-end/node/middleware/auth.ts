import {Request, Response, NextFunction} from 'express';
import jwt from 'jsonwebtoken';
import User from '../models/User';

const JWTSecret = process.env.JWT_SECRET || 'tafaltandot';

export const authenticateToken = async (req: Request, res: Response, next: NextFunction) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) {
    return res.status(401).json({ message: 'Token não fornecido' });
  }

  try {
    const decoded = jwt.verify(token, JWTSecret) as { id: string };
    const user = await User.findById(decoded.id);
    if (!user) {
      return res.status(401).json({ message: 'Usuário não encontrado' });
    }
    (req as any).user = user;  // Adiciona o usuário ao req
    next();
  } catch (error) {
    res.status(403).json({ message: 'Token inválido' });
  }
};
