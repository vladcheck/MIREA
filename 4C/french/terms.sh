#!/bin/zsh
set -euo pipefail

INPUT="./terms.csv"

if [[ ! -f "$INPUT" ]]; then
    echo "Error: $INPUT not found" >&2
    exit 1
fi

while IFS= read -r line || [[ -n "$line" ]]; do
    line="${line%$'\r'}"
    [[ -z "$line" ]] && continue
    unit="${line%%,*}"
    echo "$line" >> "${unit}.csv"
done < "$INPUT"