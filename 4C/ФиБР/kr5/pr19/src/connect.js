const { Pool } = require('pg');

const adminPool = new Pool({
  user: process.env.PG_USER || 'postgres',
  host: process.env.PG_HOST || 'localhost',
  database: 'postgres',
  password: process.env.PG_PASSWORD || 'password',
  port: parseInt(process.env.PG_PORT, 10) || 5432,
});

const appPool = new Pool({
  user: process.env.PG_USER || 'postgres',
  host: process.env.PG_HOST || 'localhost',
  database: process.env.PG_DB || 'practice19_db',
  password: process.env.PG_PASSWORD || 'password',
  port: parseInt(process.env.PG_PORT, 10) || 5432,
});

const initDatabase = async () => {
  const dbName = process.env.PG_DB || 'practice19_db';

  // Check if DB exists
  const dbCheck = await adminPool.query(
    'SELECT 1 FROM pg_database WHERE datname = $1',
    [dbName]
  );

  if (dbCheck.rows.length === 0) {
    // CREATE DATABASE cannot be parameterized - sanitize manually
    const safeName = dbName.replace(/[^a-zA-Z0-9_]/g, '_');
    await adminPool.query(`CREATE DATABASE "${safeName}"`);
    console.log(`Database "${safeName}" created`);
  }
  await adminPool.end();
};

const initSchema = async () => {
  await appPool.query(`
    CREATE TABLE IF NOT EXISTS users (
      id SERIAL PRIMARY KEY,
      first_name VARCHAR(100) NOT NULL,
      last_name VARCHAR(100) NOT NULL,
      age INTEGER NOT NULL,
      created_at BIGINT DEFAULT EXTRACT(EPOCH FROM NOW())::BIGINT,
      updated_at BIGINT DEFAULT EXTRACT(EPOCH FROM NOW())::BIGINT
    )
  `);
  console.log('Schema synchronized');
};

module.exports = { pool: appPool, initDatabase, initSchema };
