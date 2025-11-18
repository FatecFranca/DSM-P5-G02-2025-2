# Use uma imagem oficial do Node.js (v20 é uma boa versão LTS)
FROM node:20

# Define o diretório de trabalho no container
WORKDIR /usr/src/app

# Copia o package.json e package-lock.json primeiro
# Isso otimiza o cache do Docker
COPY package*.json ./

# Instala todas as dependências (incluindo devDependencies como ts-node)
RUN npm install

# Copia o restante do código-fonte
COPY . .

# A porta 3000 será exposta pelo docker-compose
# O comando (npm run dev) também será definido pelo docker-compose