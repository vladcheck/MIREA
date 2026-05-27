require('dotenv').config()
const express = require('express')
const mongoose = require('mongoose')
const swaggerUi = require('swagger-ui-express')
const userRoutes = require('./routes/users')

let swaggerDocument
try {
  swaggerDocument = require('./swagger_output.json')
} catch {
  console.warn('Swagger output missing. Execute run.sh before starting.')
  swaggerDocument = {}
}

const app = express()
app.use(express.json())

if (swaggerDocument.swagger || swaggerDocument.openapi) {
  app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerDocument))
}

app.use('/api/users', userRoutes)

const PORT = process.env.PORT || 3000
const MONGO_URI = process.env.MONGO_URI || 'mongodb://localhost:27017/'
const DB_NAME = process.env.DB_NAME || 'practice20'

mongoose.connect(`${MONGO_URI}${DB_NAME}`)
  .then(() => {
    console.log('MongoDB connected. Database and collections created on first write.')
    app.listen(PORT, () => {
      console.log(`Server running on http://localhost:${PORT}`)
      console.log(`Swagger running on http://localhost:${PORT}/api-docs`)
    })
  })
  .catch(err => {
    console.error('DB connection failed:', err)
    process.exit(1)
  })
