"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.authenticateToken = void 0;
const jsonwebtoken_1 = __importDefault(require("jsonwebtoken"));
const User_1 = __importDefault(require("../models/User"));
const JWTSecret = process.env.JWT_SECRET || 'tafaltandot';
const authenticateToken = async (req, res, next) => {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1];
    if (!token) {
        return res.status(401).json({ message: 'Token não fornecido' });
    }
    try {
        const decoded = jsonwebtoken_1.default.verify(token, JWTSecret);
        const user = await User_1.default.findById(decoded.id);
        if (!user) {
            return res.status(401).json({ message: 'Usuário não encontrado' });
        }
        req.user = user; // Adiciona o usuário ao req
        next();
    }
    catch (error) {
        res.status(403).json({ message: 'Token inválido' });
    }
};
exports.authenticateToken = authenticateToken;
