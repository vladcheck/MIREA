#!/usr/bin/env node
// oxlint-disable no-underscore-dangle
// oxlint-disable no-await-in-loop

const BASE_URL = "http://localhost";

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

async function api(endpoint, method = "GET", body) {
  const res = await fetch(`${BASE_URL}${endpoint}`, {
    method,
    headers: { "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await res.json().catch(() => ({}));
  console.log(`\x1b[1m[${method}] ${endpoint} -> ${res.status}\x1b[0m`);
  console.log(highlightJson(data));
  return { status: res.status, data };
}

async function testLoadBalancing(prefix, label) {
  console.log(`\n\x1b[1m=== Testing ${label} Load Balancing ===\x1b[0m`);
  const servers = new Set();
  for (let i = 0; i < 6; i++) {
    const res = await api(`${prefix}/api`);
    if (res.data?._server_id) {
      servers.add(res.data._server_id);
      console.log(`  Request ${i + 1}: handled by ${res.data._server_id}`);
    }
    await new Promise((r) => setTimeout(r, 100));
  }
  console.log(`\nUnique servers hit: ${[...servers].join(", ")}`);
  return servers.size;
}

async function run() {
  console.log("\x1b[1m=== Load Balancing Demo ===\x1b[0m");

  // Test PostgreSQL backends
  const pgCount = await testLoadBalancing("/pg", "PostgreSQL");

  // Test MongoDB backends
  const mongoCount = await testLoadBalancing("/mongo", "MongoDB");

  console.log("\n\x1b[1m=== Summary ===\x1b[0m");
  console.log(`PostgreSQL backends used: ${pgCount}/3`);
  console.log(`MongoDB backends used: ${mongoCount}/3`);

  if (pgCount >= 2 && mongoCount >= 2) {
    console.log("\x1b[32mLoad balancing is working!\x1b[0m");
  } else {
    console.log("\x1b[33mWarning: Not all backends received traffic. Check nginx config.\x1b[0m");
  }
}

run().catch(console.error);
