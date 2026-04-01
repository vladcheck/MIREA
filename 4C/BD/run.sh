#!/bin/zsh

if [ -z "$1" ]; then
    echo "Usage: $0 <db_password>"
    exit 1
fi

DB_PASSWORD="$1"
export PGPASSWORD="$DB_PASSWORD"
psql -U postgres -d real_estate_db
unset PGPASSWORD