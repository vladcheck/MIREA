#!/bin/bash
set -eou pipefail

user=$(whoami)
db=db
psql -U "$user" -d "$db" -h localhost -v ON_ERROR_STOP=1 -f test.sql
echo "Тесты завершены."
