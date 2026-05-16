async function processWithRetry(message, processor, options = {}) {
  const {
    maxRetries = 5,
    baseDelayMs = 1000,
    maxDelayMs = 30000,
  } = options;

  let attempt = 0;

  while (attempt <= maxRetries) {
    try {
      await processor(message);
      console.log(`[Retry] Успешно обработано за ${attempt + 1} попытку(и)`);
      return;
    } catch (err) {
      attempt++;

      if (attempt > maxRetries) {
        console.error(`[Retry] Исчерпаны все ${maxRetries} попытки. Сообщение отправляется в DLQ.`);
        throw err;  // Пробрасываем ошибку — Consumer направит в DLQ
      }

      // Экспоненциальная задержка с джиттером
      const exponentialDelay = Math.min(baseDelayMs * 2 ** (attempt - 1), maxDelayMs);
      const jitter = Math.random() * 1000;
      const delay = exponentialDelay + jitter;

      console.warn(`[Retry] Попытка ${attempt}/${maxRetries} провалилась: ${err.message}. Повтор через ${Math.round(delay)}ms`);
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
}

// Использование
await processWithRetry(
  { to: 'user@example.com', subject: 'Test' },
  async (msg) => {
    // Имитация нестабильного внешнего сервиса
    if (Math.random() < 0.7) throw new Error('Email service unavailable');
    console.log(`Email отправлен на ${msg.to}`);
  }
);