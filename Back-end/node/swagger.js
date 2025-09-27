const swaggerAutogen = require('swagger-autogen')();

const doc = {
  info: {
    title: 'API de Classificação de Lixo',
    version: '1.0.0',
    description: 'API para autenticação, detecção de lixo e dashboard',
  },
  host: 'localhost:3000',
  schemes: ['http'],
  securityDefinitions: {
    bearerAuth: {
      type: 'apiKey',
      name: 'Authorization',
      in: 'header',
      description: 'JWT Authorization header using the Bearer scheme. Example: "Authorization: Bearer {token}"',
    },
  },
  security: [
    {
      bearerAuth: [],
    },
  ],
};

const outputFile = './swagger-output.json';
const endpointsFiles = ['./server.js'];  

swaggerAutogen(outputFile, endpointsFiles, doc).then(() => {
  require('./server.js');  
});