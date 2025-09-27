import { Request, Response } from 'express';
import { IUser } from '../models/User';  // Importe a interface do model

interface AuthenticatedRequest extends Request {
  user?: IUser;
}

export const getUser = (req: AuthenticatedRequest, res: Response) => {
  const user = req.user;
  res.json(user);
};

export const getUserInfo = (req: AuthenticatedRequest, res: Response) => {
  const user = req.user;
  if (!user) {
    return res.status(404).json({ message: 'Usuário não encontrado' });
  }
  res.json({
    id: user._id,
    username: user.username,
    email: user.email,
    name: user.name,
    createdAt: user.createdAt,
    updatedAt: user.updatedAt
  });
};