const path = require('path');
const swaggerAutogen = require('swagger-autogen')();

const doc = {
  info: {
    title: 'Practice 19 API',
    description: 'User management API with PostgreSQL',
    version: '1.0.0',
  },
  host: 'localhost:3000',
  basePath: '/',
  schemes: ['http'],
  consumes: ['application/json'],
  produces: ['application/json'],
  tags: [
    { name: 'Users', description: 'User management endpoints' },
  ],
  definitions: {
    User: {
      id: 1,
      first_name: 'John',
      last_name: 'Doe',
      age: 25,
      created_at: 1700000000,
      updated_at: 1700000000,
    },
    CreateUser: {
      $first_name: 'John',
      $last_name: 'Doe',
      $age: 25,
    },
    UpdateUser: {
      $first_name: 'John',
      $last_name: 'Doe',
      $age: 25,
    },
  },
};

const outputFile = path.join(__dirname, '../swagger-output.json');
const endpointsFiles = ['./src/server.js'];

swaggerAutogen(outputFile, endpointsFiles, doc).then(() => {
  console.log('Swagger spec generated at ' + outputFile);
});
