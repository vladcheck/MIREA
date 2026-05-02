#!/bin/bash
set -euo pipefail nounset

psql -f ./migrations/init.sql -U postgres &> /dev/null

if [ $? -eq 0 ]; then
  echo "Success."
fi