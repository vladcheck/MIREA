const express = require("express");
const path = require("path");
const logger = require("./middleware/logger");
const votesRouter = require("./routes/votes");
const optionsRouter = require("./routes/options");

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware для парсинга JSON
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Кастомный middleware для логирования
app.use(logger);

// Раздача статических файлов
app.use(express.static(path.join(__dirname, "public")));

// Маршруты API
app.use("/api/votes", votesRouter);
app.use("/api/options", optionsRouter);

// Главная страница
app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "public", "index.html"));
});

// Обработчик ошибок 404
app.use((req, res) => {
  res.status(404).json({
    success: false,
    message: "Endpoint not found",
  });
});

// Глобальный обработчик ошибок
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({
    success: false,
    message: "Internal server error",
  });
});

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
  console.log(`API available at http://localhost:${PORT}/api/votes`);
  console.log(`Static files served from http://localhost:${PORT}/`);
});
