# Use uma imagem oficial do Python
FROM python:3.10-slim

# Define o diretório de trabalho no container
WORKDIR /app

# Copia o arquivo de dependências
COPY requirements.txt .

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Baixa os pacotes NLTK necessários
RUN python -m nltk.downloader stopwords punkt punkt_tab

# Copia o restante do código-fonte
COPY . .

# O comando (flask run) será definido pelo docker-compose