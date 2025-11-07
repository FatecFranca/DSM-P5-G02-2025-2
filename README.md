# 🧠 Verify  
Aplicativo interdisciplinar desenvolvido pelo **Grupo 02 — DSM 5º Semestre (2025/2)**, que utiliza **Inteligência Artificial** para identificar se uma mensagem é **spam** ou **legítima**.

---

## 📂 Estrutura do Repositório
```
DSM-P5-G02-2025-2/
├── back-end/
│   ├── ia/              # Scripts e modelos de IA (Python)
│   ├── node/            # API em Node.js + Express + MongoDB
│   └── README.md
├── mobile/              # Aplicativo em Flutter
│   └── README.md
└── README.md            # Este arquivo
```

---

## 🚀 Descrição do Projeto
O **Verify** é um aplicativo que permite ao usuário enviar mensagens de texto para análise, e a IA classifica se o conteúdo é **spam** ou **não spam**.  
O objetivo é auxiliar na **segurança digital** e evitar fraudes em comunicações.

---

## 🧠 Tecnologias Utilizadas

### 🔹 Back-end
- **Node.js** com **Express.js**  
- **MongoDB** para persistência dos dados  
- **Python** para treinamento e execução do modelo de **IA (Machine Learning)**  
- **API REST** para comunicação entre o app e a IA  

### 🔹 Mobile
- **Flutter (Dart)** para o aplicativo multiplataforma  
- **HTTP Requests** para comunicação com o back-end  
- **Design limpo e responsivo** com base no Material Design  

---

## ⚙️ Como Executar o Projeto

### 🖥️ Back-end

1. Acesse a pasta:
   ```bash
   cd back-end/node
   ```

2. Instale as dependências:
   ```bash
   npm install
   ```

3. Inicie o servidor:
   ```bash
   npm start
   ```
   O servidor ficará disponível em: `http://localhost:3000`

4. (Opcional) Para rodar a IA:
   ```bash
   cd ../ia
   python app.py
   ```

---

### 📱 Mobile

1. Acesse a pasta:
   ```bash
   cd mobile
   ```

2. Instale as dependências:
   ```bash
   flutter pub get
   ```

3. Execute o app:
   ```bash
   flutter run
   ```

---

## 🧩 Funcionalidades Principais
- Envio de mensagens para análise  
- Classificação automática (spam / não spam)  
- Exibição do resultado de forma simples e rápida  
- Histórico de mensagens analisadas  

---

## 👥 Grupo 02 — DSM P5 (2025/2)
- **Inácio Santana**  
- **Jhonathan Dias** 
- **Vinicius de Paula**   

---


## 📜 Licença
Este projeto é de uso acadêmico para fins do **Projeto Interdisciplinar — FATEC DSM (2025/2)**.
