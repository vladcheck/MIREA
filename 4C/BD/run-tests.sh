#!/bin/bash

if [ -z "$1" ]; then
    echo "Usage: $0 <path_to_folder> <db_password>"
    exit 1
fi

if [ -z "$2" ]; then
    echo "Usage: $0 <path_to_folder> <db_password>"
    exit 1
fi

TARGET_DIR="$(cd "$1" && pwd)"
LOG_FILE="$TARGET_DIR/logs.txt"
DB_PASSWORD="$2"

if [ ! -d "$TARGET_DIR" ]; then
    echo "Error: Directory $TARGET_DIR does not exist"
    exit 1
fi

export PGPASSWORD="$DB_PASSWORD"

: > "$LOG_FILE"

echo "Starting execution at $(date)" | tee -a "$LOG_FILE"
echo "Target directory: $TARGET_DIR" | tee -a "$LOG_FILE"
echo "---" | tee -a "$LOG_FILE"

cd "$TARGET_DIR" || exit 1

for file in *.sql; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        if [[ ! "$filename" =~ ^[0-9]+\.sql$ ]]; then
            echo "Running migration: $file" | tee -a "$LOG_FILE"
            psql -U postgres -d real_estate_db -f "$file" >> "$LOG_FILE" 2>&1
            if [ $? -ne 0 ]; then
                echo "Error in migration $file" | tee -a "$LOG_FILE"
            fi
        fi
    fi
done

shopt -s nullglob
files=(*.sql)
shopt -u nullglob

ids=""
for file in "${files[@]}"; do
    if [[ "$file" =~ ^([0-9]+)\.sql$ ]]; then
        id="${BASH_REMATCH[1]}"
        if [[ ! " $ids " =~ " $id " ]]; then
            ids="$ids $id"
        fi
    fi
done

for id in $ids; do
    main_file="$id.sql"
    test_file="test/$id.sql"

    if [ -f "$main_file" ]; then
        echo "Running main script: $main_file" | tee -a "$LOG_FILE"
        psql -U postgres -d real_estate_db -f "$main_file" >> "$LOG_FILE" 2>&1
        if [ $? -ne 0 ]; then
            echo "Error in $main_file" | tee -a "$LOG_FILE"
        fi
    fi

    if [ -f "$test_file" ]; then
        echo "Running test script: $test_file" | tee -a "$LOG_FILE"
        psql -U postgres -d real_estate_db -f "$test_file" >> "$LOG_FILE" 2>&1
        if [ $? -ne 0 ]; then
            echo "Error in $test_file" | tee -a "$LOG_FILE"
        fi
    fi
done

echo "---" | tee -a "$LOG_FILE"
echo "Execution finished at $(date)" | tee -a "$LOG_FILE"

unset PGPASSWORD