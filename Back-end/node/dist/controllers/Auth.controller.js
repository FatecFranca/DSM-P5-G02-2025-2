"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.googleAuth = exports.login = exports.register = void 0;
const User_1 = __importDefault(require("../models/User"));
const bcryptjs_1 = __importDefault(require("bcryptjs"));
const jsonwebtoken_1 = __importDefault(require("jsonwebtoken"));
const admin = __importStar(require("firebase-admin"));
const JWTSecret = process.env.JWT_SECRET || 'tafaltandot';
const register = async (req, res) => {
    const { username, email, name, password } = req.body;
    try {
        const existingUser = await User_1.default.findOne({ $or: [{ username }, { email }] });
        if (existingUser) {
            return res.status(400).json({ message: 'Username ou email já existe' });
        }
        const hashedPassword = await bcryptjs_1.default.hash(password, 10);
        const user = new User_1.default({ username, email, name, password: hashedPassword });
        await user.save();
        const token = jsonwebtoken_1.default.sign({ id: user._id }, JWTSecret, { expiresIn: '1d' });
        res.status(201).json({ token });
    }
    catch (error) {
        console.error('Erro ao registrar usuário:', error);
        res.status(500).json({ message: 'Erro ao registrar usuário' });
    }
};
exports.register = register;
const login = async (req, res) => {
    const { identifier, password } = req.body;
    try {
        const user = await User_1.default.findOne({ $or: [{ username: identifier }, { email: identifier }] });
        if (!user) {
            return res.status(404).json({ message: 'Usuário não encontrado' });
        }
        const isPasswordValid = await bcryptjs_1.default.compare(password, user.password);
        if (!isPasswordValid) {
            return res.status(401).json({ message: 'Senha incorreta' });
        }
        const token = jsonwebtoken_1.default.sign({ id: user._id }, JWTSecret, { expiresIn: '1d' });
        res.status(200).json({ token });
    }
    catch (error) {
        console.error('Erro ao fazer login:', error);
        res.status(500).json({ message: 'Erro ao fazer login' });
    }
};
exports.login = login;
const googleAuth = async (req, res) => {
    const { idToken } = req.body;
    try {
        const decodedToken = await admin.auth().verifyIdToken(idToken);
        const { uid, email, name } = decodedToken;
        let user = await User_1.default.findOne({ email });
        if (!user) {
            user = new User_1.default({ email, name });
            await user.save();
        }
        const token = jsonwebtoken_1.default.sign({ id: user._id }, JWTSecret, { expiresIn: '1d' });
        res.status(200).json({ token });
    }
    catch (error) {
        console.error('Erro ao autenticar com Google:', error);
        res.status(500).json({ message: 'Erro ao autenticar com Google' });
    }
};
exports.googleAuth = googleAuth;
