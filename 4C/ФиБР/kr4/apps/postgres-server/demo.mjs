#!/usr/bin/env node
// oxlint-disable no-magic-numbers
// oxlint-disable prefer-template
// oxlint-disable no-ternary
// oxlint-disable sort-keys
// oxlint-disable prefer-destructuring

const BASE_URL = "http://localhost:3000";

function highlightJson(obj) {
  const json = JSON.stringify(obj, null, 2);
  return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+-]?\d+)?)/g, (match) => {
    let color = "\x1b[36m";
    if (/^"/.test(match)) {
      color = /:$/.test(match) ? "\x1b[33m" : "\x1b[32m";
    } else if (/true|false/.test(match)) {
      color = "\x1b[35m";
    } else if (/null/.test(match)) {
      color = "\x1b[31m";
    }
    return color + match + "\x1b[0m";
  });
}

async function api(method, path, body) {
  const res = await fetch(`${BASE_URL}${path}`, {
    method,
    headers: { "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await res.json().catch(() => ({}));
  console.log(`\n\x1b[1m[${method}] ${path} -> ${res.status}\x1b[0m`);
  console.log(highlightJson(data));
  return { status: res.status, data };
}

async function run() {
  await api("GET", "/");
  await api("GET", "/api");

  const created = await api("POST", "/api/users", {
    first_name: "Demo",
    last_name: "User",
    age: 20,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  });

  const id = created.data.id;

  await api("GET", "/api/users");
  await api("GET", `/api/users/${id}`);
  await api("PATCH", `/api/users/${id}`, { age: 25 });
  await api("DELETE", `/api/users/${id}`);
  await api("GET", "/api/users");
}

run().catch(console.error);
