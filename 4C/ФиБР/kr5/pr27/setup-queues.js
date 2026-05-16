import amqplib from 'amqplib';

async function setupQueues() {
  const connection = await amqplib.connect('amqp://localhost');
  const channel = await connection.createChannel();

  // 1. Создаём Dead Letter Exchange
  await channel.assertExchange('dlx_exchange', 'direct', { durable: true });

  // 2. Создаём Dead Letter Queue
  await channel.assertQueue('dead_letter_queue', { durable: true });

  // 3. Привязываем DLQ к DLX
  await channel.bindQueue('dead_letter_queue', 'dlx_exchange', 'dead');

  // 4. Создаём основную очередь с указанием DLX
  await channel.assertQueue('main_queue', {
    durable: true,
    arguments: {
      'x-dead-letter-exchange': 'dlx_exchange',
      'x-dead-letter-routing-key': 'dead',
      'x-message-ttl': 60000,     // Сообщение живёт 60 секунд
      'x-max-retries': 3,         // (информационно, логика retry — в коде Consumer)
    },
  });

  console.log('Очереди настроены: main_queue → [DLX] → dead_letter_queue');
  await connection.close();
}

await setupQueues();