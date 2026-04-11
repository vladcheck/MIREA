#!/bin/bash

# Проверка аргументов командной строки
if [ -z "$1" ]; then
    echo "Usage: $0 <db_password>"
    exit 1
fi

# Инициализация переменных
DB_PASSWORD="$1"
LOG_FILE="function_logs.txt"

# Установка пароля для psql
export PGPASSWORD="$DB_PASSWORD"

# Очистка лог-файла
: > "$LOG_FILE"

# Получение списка функций с суффиксом valekzhanin
FUNCTIONS=$(psql -U postgres -d real_estate_db -t -A -c \
    "SELECT proname FROM pg_proc WHERE proname LIKE '%valekzhanin%';")

# Проверка на пустой результат
if [ -z "$FUNCTIONS" ]; then
    echo "No functions found with suffix 'valekzhanin'"
    unset PGPASSWORD
    exit 0
fi

# Проход по каждой функции
for func_name in $FUNCTIONS; do
    # Получение тела функции
    psql -U postgres -d real_estate_db -t -A -c \
        "SELECT pg_get_functiondef(oid) FROM pg_proc WHERE proname = '$func_name';" \
        >> "$LOG_FILE"
    
    # Добавление разделителя
    echo "---" >> "$LOG_FILE"
done

# Очистка переменной окружения
unset PGPASSWORD

echo "Function bodies exported to $LOG_FILE"