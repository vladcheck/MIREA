import amqp from 'amqplib'

const QUEUE = 'tasks'
const DLQ = 'dead-letter-queue'

async function startWorker() {
  const connection = await amqp.connect('amqp://localhost')

  const channel = await connection.createChannel()

  await channel.assertQueue(QUEUE, {
    durable: true
  })

  await channel.assertQueue(DLQ, {
    durable: true
  })

  channel.prefetch(1)

  console.log(`Worker started: PID${process.pid}`)

  channel.consume(QUEUE, async (msg) => {
    if (!msg) return

    const task = JSON.parse(msg.content.toString())

    console.log(`Worker ${process.pid} processing:`, task)

    try {
      await processTask(task)

      console.log(`Task completed by ${process.pid}`)

      channel.ack(msg)
    } catch (error) {
      console.error(`Task failed in worker ${process.pid}: ${error}`)

      task.retries += 1

      if (task.retries >= 3) {
        console.log('Sending task to DLQ')

        channel.sendToQueue(
          DLQ,
          Buffer.from(JSON.stringify(task)),
          {
            persistent: true
          }
        )

        channel.ack(msg)
      } else {
        const delay = 1000 * Math.pow(2, task.retries)

        console.log(`Retry in ${delay} ms`)

        setTimeout(() => {
          channel.sendToQueue(
            QUEUE,
            Buffer.from(JSON.stringify(task)),
            {
              persistent: true
            }
          )

          channel.ack(msg)
        }, delay)
      }
    }
  })
}

startWorker()