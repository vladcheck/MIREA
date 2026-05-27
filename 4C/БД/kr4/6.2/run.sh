#!/bin/bash
set -eou pipefail

user=$(whoami)
db=db
psql -U "$user" -d "$db" -h localhost -f init.sql 1>/dev/null && echo "Мигрировали"
psql -U "$user" -d "$db" -h localhost -f functions.sql 1>/dev/null && echo "Функции созданы"
psql -U "$user" -d "$db" -h localhost -f procedures.sql 1>/dev/null && echo "Процедуры созданы"
psql -U "$user" -d "$db" -h localhost -f triggers.sql 1>/dev/null && echo "Триггеры созданы"
