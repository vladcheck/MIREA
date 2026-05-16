import "dotenv";
import express from 'express'
import amqp from 'amqplib'
import { Kafka } from 'kafkajs';

const kafka = new Kafka({
  clientId: process.env.CLIENT_ID,
  brokers: ['localhost:9092'],
});


const producer = kafka.producer();

const app = express()

app.use(express.json())

const QUEUE = 'tasks'

let channel = null;

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

async function sendEvent(topic, event) {
  await producer.connect();

  await producer.send({
    topic,
    messages: [
      {
        key: event.userId,          // Ключ гарантирует порядок событий одного пользователя
        value: JSON.stringify(event),
      },
    ],
  });

  console.log(`[Kafka Producer] Событие отправлено в топик "${topic}"`);
  await producer.disconnect();
}

await sendEvent('user-events', {
  userId: 'user-42',
  action: 'purchase',
  productId: 'prod-100',
  amount: 1500,
  timestamp: new Date().toISOString(),
});

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