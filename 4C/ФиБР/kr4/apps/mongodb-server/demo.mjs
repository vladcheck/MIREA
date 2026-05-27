#!/usr/bin/env node
// oxlint-disable no-magic-numbers
// oxlint-disable prefer-template
// oxlint-disable no-ternary
// oxlint-disable max-statements

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
    body: body ? JSON.stringify(body) : undefined,
    headers: { "Content-Type": "application/json" },
    method,
  });
  const data = await res.json().catch(() => ({}));
  console.log(`\n\x1b[1m[${method}] ${path} -> ${res.status}\x1b[0m`);
  console.log(highlightJson(data));
  return { data, status: res.status };
}

async function run() {
  // Health checks
  await api("GET", "/");
  await api("GET", "/api");

  // Create a user (MongoDB uses _id, not id)
  const created = await api("POST", "/api/users", {
    age: 20,
    first_name: "Demo",
    last_name: "User",
  });

  // oxlint-disable-next-line no-underscore-dangle
  const id = created.data._id;
  if (!id) {
    console.error("Failed to extract _id from created user");
    return;
  }

  // List all users
  await api("GET", "/api/users");

  // Get single user by _id
  await api("GET", `/api/users/${id}`);

  // Update user
  await api("PATCH", `/api/users/${id}`, { age: 25 });

  // Delete user
  await api("DELETE", `/api/users/${id}`);

  // Verify deletion
  await api("GET", "/api/users");
}

run().catch(console.error);
