const logger = (req, res, next) => {
  const timestamp = new Date().toISOString();
  const method = req.method;
  const url = req.url;
  const ip = req.ip || req.connection.remoteAddress;

  console.log(`[${timestamp}] ${method} ${url} - IP: ${ip}`);

  // Логируем тело запроса для POST/PUT
  if (method === "POST" || method === "PUT") {
    console.log("Request body:", req.body);
  }

  // Сохраняем время начала обработки запроса
  const start = Date.now();

  // Обрабатываем ответ
  const originalSend = res.send;
  res.send = function (body) {
    const duration = Date.now() - start;
    console.log(
      `[${timestamp}] ${method} ${url} - ${res.statusCode} (${duration}ms)`
    );
    console.log("Response body:", body);
    return originalSend.call(this, body);
  };

  next();
};

module.exports = logger;
