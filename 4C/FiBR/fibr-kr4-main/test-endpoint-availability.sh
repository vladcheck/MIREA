#!/bin/bash
BASE_URL="http://localhost"
TMP=$(mktemp -d)
trap "rm -rf $TMP" EXIT

echo "Endpoint availability test"
echo "=========================="
echo ""

call() {
  local method="$1" path="$2" body="$3" label="$4"
  if [ -n "$body" ]; then
    curl -s -X "$method" "$BASE_URL$path" -H "Content-Type: application/json" -d "$body" -D "$TMP/h" -o "$TMP/b"
  else
    curl -s -X "$method" "$BASE_URL$path" -D "$TMP/h" -o "$TMP/b"
  fi

  local status=$(awk '/^HTTP/{s=$2} END{print s}' "$TMP/h")
  local server=$(grep -i '^X-Server:' "$TMP/h" | awk '{print $2}' | tr -d '\r')
  local cache=$(grep -i '^X-Cache:' "$TMP/h" | awk '{print $2}' | tr -d '\r')

  printf "%-25s | Status: %-3s | Server: %-10s | Cache: %s\n" "$label" "${status:---}" "${server:-N/A}" "${cache:-N/A}" >&2
  cat "$TMP/b"
}

echo "Creating resources..."
UID=$(call "POST" "/api/users" '{"first_name":"A","last_name":"B","age":20}' "Create User" | sed -n 's/.*"id":\([0-9]*\).*/\1/p' | head -1)
PID=$(call "POST" "/api/products" '{"name":"X","price":10,"stock":5}' "Create Product" | sed -n 's/.*"id":\([0-9]*\).*/\1/p' | head -1)

echo ""
echo "Testing endpoints..."
call "GET" "/health" "" "Health" > /dev/null
call "GET" "/api/users" "" "List Users" > /dev/null
call "GET" "/api/users/$UID" "" "Get User $UID" > /dev/null
call "PATCH" "/api/users/$UID" '{"age":21}' "Update User $UID" > /dev/null
call "DELETE" "/api/users/$UID" "" "Delete User $UID" > /dev/null

call "GET" "/api/products" "" "List Products" > /dev/null
call "GET" "/api/products/$PID" "" "Get Product $PID" > /dev/null
call "PATCH" "/api/products/$PID" '{"price":15}' "Update Product $PID" > /dev/null
call "DELETE" "/api/products/$PID" "" "Delete Product $PID" > /dev/null

echo ""
echo "Done"
