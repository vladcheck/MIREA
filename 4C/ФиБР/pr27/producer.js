import express from 'express'
import amqp from 'amqplib'

const app = express()

app.use(express.json())

const QUEUE = 'tasks'

let channel

async function connectQueue() {
  const connection = await amqp.connect('amqp://localhost')

  channel = await connection.createChannel()

  await channel.assertQueue(QUEUE, {
    durable: true,
    deadLetterExchange: '',
    deadLetterRoutingKey: 'dead-letter-queue'
  })

  await channel.assertQueue('dead-letter-queue', {
    durable: true
  })

  console.log('Connected to RabbitMQ')
}

connectQueue()

app.post('/tasks', async (req, res) => {
  const task = {
    ...req.body,
    retries: 0
  }

  channel.sendToQueue(
    QUEUE,
    Buffer.from(JSON.stringify(task)),
    {
      persistent: true
    }
  )

  console.log('Task added:', task)

  res.json({
    message: 'Task added to queue',
    task
  })
})

app.listen(3000, () => {
  console.log('Producer API running on port 3000')
})