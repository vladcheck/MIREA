import express from "express";
import { Pool } from "pg";
import Redis from "ioredis";

const app = express();
app.use(express.json());
app.use((req, res, next) => {
	res.set('X-Server', SERVER_ID);
	next();
});

const SERVER_ID = process.env.SERVER_ID || "backend-1";
const DB_URL = process.env.DATABASE_URL || "postgresql://postgres:postgres@postgres:5432/app_db";
const REDIS_URL = process.env.REDIS_URL || "redis://redis:6379";
const PORT = parseInt(process.env.PORT || "8080", 10);

const pool = new Pool({ connectionString: DB_URL });
const redis = new Redis(REDIS_URL);

const initDB = async () => {
	const users = `CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, first_name VARCHAR(255) NOT NULL, last_name VARCHAR(255) NOT NULL, age INTEGER, created_at TIMESTAMP DEFAULT NOW(), updated_at TIMESTAMP DEFAULT NOW())`;
	const products = `CREATE TABLE IF NOT EXISTS products (id SERIAL PRIMARY KEY, name VARCHAR(255) NOT NULL, description TEXT, price DECIMAL(10,2) NOT NULL, stock INTEGER DEFAULT 0, created_at TIMESTAMP DEFAULT NOW(), updated_at TIMESTAMP DEFAULT NOW())`;
	await pool.query(users);
	await pool.query(products);
	console.log("Database initialized");
};

const setCache = async (key, value, seconds) => {
	await redis.set(key, JSON.stringify(value), "EX", seconds);
};

const getCache = async (key) => {
	const data = await redis.get(key);
	return data ? JSON.parse(data) : null;
};

const deleteCache = async (key) => {
	await redis.del(key);
};

app.get("/health", (req, res) => {
	res.json({ status: "ok", server: SERVER_ID, time: new Date().toISOString() });
});

app.post("/api/users", async (req, res) => {
	const { first_name, last_name, age } = req.body;
	if (!first_name || !last_name)
		return res.status(400).json({ error: "First name and last name are required" });
	try {
		const { rows } = await pool.query(
			"INSERT INTO users (first_name, last_name, age) VALUES ($1, $2, $3) RETURNING *",
			[first_name, last_name, age || null],
		);
		await deleteCache("users_list");
		res.status(201).json(rows[0]);
	} catch (err) {
		console.error(err);
		res.status(500).json({ error: "Failed to create user" });
	}
});

app.get("/api/users", async (req, res) => {
	try {
		const cached = await getCache("users_list");
		if (cached) {
			res.set({ "X-Cache": "HIT", "X-Server": SERVER_ID });
			return res.json(cached);
		}
		const { rows } = await pool.query(
			"SELECT id, first_name, last_name, age, created_at, updated_at FROM users",
		);
		await setCache("users_list", rows, 60);
		res.set({ "X-Cache": "MISS", "X-Server": SERVER_ID });
		res.json(rows);
	} catch (err) {
		console.error(err);
		res.status(500).json({ error: "Failed to get users" });
	}
});

app.get("/api/users/:id", async (req, res) => {
	const id = parseInt(req.params.id, 10);
	if (isNaN(id)) return res.status(400).json({ error: "Invalid user ID" });
	try {
		const cacheKey = `user:${id}`;
		const cached = await getCache(cacheKey);
		if (cached) {
			res.set({ "X-Cache": "HIT", "X-Server": SERVER_ID });
			return res.json(cached);
		}
		const { rows } = await pool.query(
			"SELECT id, first_name, last_name, age, created_at, updated_at FROM users WHERE id = $1",
			[id],
		);
		if (rows.length === 0) return res.status(404).json({ error: "User not found" });
		await setCache(cacheKey, rows[0], 60);
		res.set({ "X-Cache": "MISS", "X-Server": SERVER_ID });
		res.json(rows[0]);
	} catch (err) {
		console.error(err);
		res.status(500).json({ error: "Failed to get user" });
	}
});

app.patch("/api/users/:id", async (req, res) => {
	const id = parseInt(req.params.id, 10);
	if (isNaN(id)) return res.status(400).json({ error: "Invalid user ID" });
	const updates = [];
	const values = [];
	let idx = 1;
	const { first_name, last_name, age } = req.body;
	if (first_name !== undefined) {
		updates.push(`first_name = $${idx}`);
		values.push(first_name);
		idx++;
	}
	if (last_name !== undefined) {
		updates.push(`last_name = $${idx}`);
		values.push(last_name);
		idx++;
	}
	if (age !== undefined) {
		updates.push(`age = $${idx}`);
		values.push(age);
		idx++;
	}
	if (updates.length === 0) return res.status(400).json({ error: "No fields to update" });
	updates.push("updated_at = NOW()");
	values.push(id);
	try {
		await pool.query(`UPDATE users SET ${updates.join(", ")} WHERE id = $${idx}`, values);
		await deleteCache("users_list");
		await deleteCache(`user:${id}`);
		const { rows } = await pool.query(
			"SELECT id, first_name, last_name, age, created_at, updated_at FROM users WHERE id = $1",
			[id],
		);
		res.set({ "X-Server": SERVER_ID });
		res.json(rows[0]);
	} catch (err) {
		console.error(err);
		res.status(500).json({ error: "Failed to update user" });
	}
});

app.delete("/api/users/:id", async (req, res) => {
	const id = parseInt(req.params.id, 10);
	if (isNaN(id)) return res.status(400).json({ error: "Invalid user ID" });
	try {
		const { rowCount } = await pool.query("DELETE FROM users WHERE id = $1", [id]);
		if (rowCount === 0) return res.status(404).json({ error: "User not found" });
		await deleteCache("users_list");
		await deleteCache(`user:${id}`);
		res.status(204).end();
	} catch (err) {
		console.error(err);
		res.status(500).json({ error: "Failed to delete user" });
	}
});

app.post("/api/products", async (req, res) => {
	const { name, description, price, stock } = req.body;
	if (!name) return res.status(400).json({ error: "Name is required" });
	try {
		const { rows } = await pool.query(
			"INSERT INTO products (name, description, price, stock) VALUES ($1, $2, $3, $4) RETURNING *",
			[name, description || "", price || 0, stock || 0],
		);
		await deleteCache("products_list");
		res.status(201).json(rows[0]);
	} catch (err) {
		console.error(err);
		res.status(500).json({ error: "Failed to create product" });
	}
});

app.get("/api/products", async (req, res) => {
	try {
		const cached = await getCache("products_list");
		if (cached) {
			res.set({ "X-Cache": "HIT", "X-Server": SERVER_ID });
			return res.json(cached);
		}
		const { rows } = await pool.query("SELECT * FROM products");
		await setCache("products_list", rows, 600);
		res.set({ "X-Cache": "MISS", "X-Server": SERVER_ID });
		res.json(rows);
	} catch (err) {
		res.status(500).json({ error: "Failed to get products" });
	}
});

app.get("/api/products/:id", async (req, res) => {
	const id = parseInt(req.params.id, 10);
	if (isNaN(id)) return res.status(400).json({ error: "Invalid product ID" });
	try {
		const cacheKey = `product:${id}`;
		const cached = await getCache(cacheKey);
		if (cached) {
			res.set({ "X-Cache": "HIT", "X-Server": SERVER_ID });
			return res.json(cached);
		}
		const { rows } = await pool.query("SELECT * FROM products WHERE id = $1", [id]);
		if (rows.length === 0) return res.status(404).json({ error: "Product not found" });
		await setCache(cacheKey, rows[0], 600);
		res.set({ "X-Cache": "MISS", "X-Server": SERVER_ID });
		res.json(rows[0]);
	} catch (err) {
		res.status(500).json({ error: "Failed to get product" });
	}
});

app.patch("/api/products/:id", async (req, res) => {
	const id = parseInt(req.params.id, 10);
	if (isNaN(id)) return res.status(400).json({ error: "Invalid product ID" });
	const updates = [];
	const values = [];
	let idx = 1;
	const { name, description, price, stock } = req.body;
	if (name !== undefined) {
		updates.push(`name = $${idx}`);
		values.push(name);
		idx++;
	}
	if (description !== undefined) {
		updates.push(`description = $${idx}`);
		values.push(description);
		idx++;
	}
	if (price !== undefined) {
		updates.push(`price = $${idx}`);
		values.push(price);
		idx++;
	}
	if (stock !== undefined) {
		updates.push(`stock = $${idx}`);
		values.push(stock);
		idx++;
	}
	if (updates.length === 0) return res.status(400).json({ error: "No fields to update" });
	updates.push("updated_at = NOW()");
	values.push(id);
	try {
		await pool.query(`UPDATE products SET ${updates.join(", ")} WHERE id = $${idx}`, values);
		await deleteCache("products_list");
		await deleteCache(`product:${id}`);
		const { rows } = await pool.query("SELECT * FROM products WHERE id = $1", [id]);
		res.set({ "X-Server": SERVER_ID });
		res.json(rows[0]);
	} catch (err) {
		res.status(500).json({ error: "Failed to update product" });
	}
});

app.delete("/api/products/:id", async (req, res) => {
	const id = parseInt(req.params.id, 10);
	if (isNaN(id)) return res.status(400).json({ error: "Invalid product ID" });
	try {
		const { rowCount } = await pool.query("DELETE FROM products WHERE id = $1", [id]);
		if (rowCount === 0) return res.status(404).json({ error: "Product not found" });
		await deleteCache("products_list");
		await deleteCache(`product:${id}`);
		res.status(204).end();
	} catch (err) {
		res.status(500).json({ error: "Failed to delete product" });
	}
});

app.listen(PORT, "0.0.0.0", async () => {
	await initDB();
	console.log(`Server ${SERVER_ID} starting on port ${PORT}`);
});
