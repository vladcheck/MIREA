import "dotenv";
import { Kafka } from 'kafkajs';

const kafka = new Kafka({
  clientId: process.env.CLIENT_ID,
  brokers: ['localhost:9092'],
});

const consumer = kafka.consumer({ groupId: 'analytics-service' });

async function startConsumer() {
  await consumer.connect();
  await consumer.subscribe({ topic: 'user-events', fromBeginning: false });

  await consumer.run({
    eachMessage: async ({ topic, partition, message }) => {
      const event = JSON.parse(message.value.toString());
      console.log(`[Kafka Consumer] Получено из ${topic}[${partition}]:`, event);

      // Обработка события
      await processUserEvent(event);
    },
  });
}

async function processUserEvent(event) {
  console.log(`Аналитика: пользователь ${event.userId} выполнил ${event.action}`);
}

await startConsumer();