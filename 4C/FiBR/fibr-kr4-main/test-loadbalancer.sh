#!/bin/bash
echo "Test nginx"
echo ""
REQUESTS=10
TEMP_FILE=$(mktemp)

for ((i=1; i<=REQUESTS; i++)); do
  RESPONSE=$(curl -s http://localhost/health 2>/dev/null)
  if [ $? -eq 0 ]; then
    SERVER_ID=$(echo "$RESPONSE" | grep -o '"server":"[^"]*"' | head -1 | cut -d'"' -f4)
    if [ -n "$SERVER_ID" ]; then
      echo "$SERVER_ID" >> "$TEMP_FILE"
      echo "Query $i : Server = $SERVER_ID"
    else
      echo "Query $i : Error - Invalid response"
    fi
  else
    echo "Query $i : Error - Connection failed"
  fi
  sleep 0.2
done

echo ""
echo "Result"
if [ -s "$TEMP_FILE" ]; then
  sort "$TEMP_FILE" | uniq -c | sort -rn | while read COUNT SERVER_ID; do
    PERCENT=$(awk "BEGIN {printf \"%.2f\", ($COUNT / $REQUESTS) * 100}")
    echo "$SERVER_ID : $COUNT queries ($PERCENT%)"
  done
else
  echo "No successful queries"
fi
rm -f "$TEMP_FILE"
