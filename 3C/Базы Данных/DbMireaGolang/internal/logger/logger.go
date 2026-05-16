package logger

import (
	"os"
	"strings"
	"time"

	"github.com/daniildddd/DbMireaGolang/config"
	"github.com/rs/zerolog"
)

var Logger zerolog.Logger

func InitLogger() error {
	config.MustLoad()

	logLevelStr := config.GetEnvWithDefault("LOG_LEVEL", "info")
	logLevelStr = strings.Trim(logLevelStr, `"' `)

	// Парсим уровень логирования
	logLevel, err := zerolog.ParseLevel(strings.ToLower(logLevelStr))
	if err != nil {
		logLevel = zerolog.InfoLevel // по умолчанию
	}

	// Создаем папку для логов
	if err := os.MkdirAll("logs", 0755); err != nil {
		return err
	}

	// Открываем файл для записи логов
	logFileName := "logs/app.log"
	file, err := os.OpenFile(logFileName, os.O_CREATE|os.O_WRONLY|os.O_TRUNC, 0666)
	if err != nil {
		return err
	}

	// Настраиваем красивый консольный вывод
	consoleWriter := zerolog.ConsoleWriter{
		Out:        os.Stdout,
		TimeFormat: time.DateTime,
		FormatLevel: func(i interface{}) string {
			var level string
			var color string

			switch i {
			case "debug":
				level = "DBG"
				color = "\033[36m" // голубой
			case "info":
				level = "INF"
				color = "\033[32m" // зеленый
			case "warn":
				level = "WRN"
				color = "\033[33m" // желтый
			case "error":
				level = "ERR"
				color = "\033[31m" // красный
			default:
				level = "???"
				color = "\033[0m" // без цвета
			}

			return color + level + "\033[0m"
		},
		FormatMessage: func(i interface{}) string {
			return "\033[1m" + i.(string) + "\033[0m" // жирный шрифт
		},
	}

	// Мульти-врайтер: и в консоль, и в файл
	multiWriter := zerolog.MultiLevelWriter(consoleWriter, file)

	// Создаем логгер
	Logger = zerolog.New(multiWriter).
		Level(logLevel).
		With().
		Timestamp().
		Logger()

	// Красивое сообщение о запуске
	Logger.Info().
		Str("версия", "1.0.0").
		Str("режим", strings.ToUpper(logLevelStr)).
		Str("лог_файл", logFileName).
		Msg("🚀 Приложение запущено")

	return nil
}

// Упрощенные методы для удобства
func Info(format string, v ...interface{}) {
	Logger.Info().Msgf(format, v...)
}

func Error(format string, v ...interface{}) {
	Logger.Error().Msgf(format, v...)
}

func Debug(format string, v ...interface{}) {
	Logger.Debug().Msgf(format, v...)
}

func Warn(format string, v ...interface{}) {
	Logger.Warn().Msgf(format, v...)
}

func Close() {
	Logger.Info().Msg("🛑 Приложение завершено")
}
