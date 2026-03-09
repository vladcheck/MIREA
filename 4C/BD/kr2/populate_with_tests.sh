#!/bin/bash
set -e

for folder in 2*/; do
  if [ -d "$folder" ]; then
    (
      cd "$folder"
      if ! [ -d test ]; then
        mkdir test
      fi

      for f in *.{sql,pgsql}; do
        if [ -f "$f" ] && ! [[ $(echo "$f" | grep "schema") ]]; then
          touch "test/test_$f"
          echo "Created ${folder}test/test_$f"
        fi
      done
    )
  fi
done