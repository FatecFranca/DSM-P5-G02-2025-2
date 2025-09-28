"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.getUserInfo = exports.getUser = void 0;
const getUser = (req, res) => {
    const user = req.user;
    res.json(user);
};
exports.getUser = getUser;
const getUserInfo = (req, res) => {
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
exports.getUserInfo = getUserInfo;
