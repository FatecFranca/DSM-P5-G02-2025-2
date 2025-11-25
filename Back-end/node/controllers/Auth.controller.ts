import {Request, Response} from 'express';
import User from '../models/User';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import * as admin from 'firebase-admin';

const JWTSecret = process.env.JWT_SECRET || 'tafaltandot';

export const register = async (req: Request, res: Response) => {
  const { email, name, password, username } = req.body;
  try {
    const existingUser = await User.findOne({ $or: [{ email }] });
    if (existingUser) {
      return res.status(400).json({ message: ' email já existe' });
    }

    const hashedPassword = await bcrypt.hash(password, 10);
    // username agora é opcional
    const userData: any = { email, name, password: hashedPassword };
    if (username) userData.username = username;
    const user = new User(userData);
    await user.save();

    const token = jwt.sign({ id: user._id }, JWTSecret, { expiresIn: '1d' });
    res.status(201).json({ token });
  } catch (error) {
    console.error('Erro ao registrar usuário:', error);
    res.status(500).json({ message: 'Erro ao registrar usuário' });
  }
};

export const login = async (req: Request, res: Response) => {
  const { email, password } = req.body;
  try {
    const user = await User.findOne({ email });
    if (!user) {
      return res.status(404).json({ message: 'Usuário não encontrado' });
    }

    const isPasswordValid = await bcrypt.compare(password, user.password);
    if (!isPasswordValid) {
      return res.status(401).json({ message: 'Senha incorreta' });
    }

    const token = jwt.sign({ id: user._id }, JWTSecret, { expiresIn: '1d' });
    res.status(200).json({ token });
  } catch (error) {
    console.error('Erro ao fazer login:', error);
    res.status(500).json({ message: 'Erro ao fazer login' });
  }
};

export const googleAuth = async (req: Request, res: Response) => {
  const { idToken } = req.body;
    try {
    const decodedToken = await admin.auth().verifyIdToken(idToken);
    const { uid, email, name } = decodedToken;
    let user = await User.findOne({ email });

    if (!user) {
        user = new User({ email, name });
        await user.save();
    }

    const token = jwt.sign({ id: user._id }, JWTSecret, { expiresIn: '1d' });
    res.status(200).json({ token });
  } catch (error) {
    console.error('Erro ao autenticar com Google:', error);
    res.status(500).json({ message: 'Erro ao autenticar com Google' });
  }
};
