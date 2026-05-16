const swaggerAutogen = require('swagger-autogen')()

const doc = {
  info: {
    version: '1.0.0',
    title: 'User API',
    description: 'Practice 20 - MongoDB CRUD operations'
  },
  host: 'localhost:3000',
  basePath: '/',
  schemes: ['http'],
  consumes: ['application/json'],
  produces: ['application/json'],
  definitions: {
    User: {
      id: 1,
      first_name: 'string',
      last_name: 'string',
      age: 20,
      created_at: 1700000000,
      updated_at: 1700000000
    }
  }
}

const outputFile = './swagger_output.json'
const endpointsFiles = ['./server.js']

swaggerAutogen(outputFile, endpointsFiles, doc).then(() => {
  console.log('Swagger spec generated')
})