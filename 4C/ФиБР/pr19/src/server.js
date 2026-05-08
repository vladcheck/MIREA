require('dotenv').config();
const express = require('express');
const swaggerUi = require('swagger-ui-express');
const swaggerDoc = require('../swagger-output.json');
const { pool, initDatabase, initSchema } = require('./connect');

const app = express();
app.use(express.json());

// Swagger UI
app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerDoc));

app.post('/api/users', async (req, res) => {
  const { first_name, last_name, age } = req.body;
  const unixTime = Math.floor(Date.now() / 1000);
  try {
    const result = await pool.query(
      'INSERT INTO users (first_name, last_name, age, created_at, updated_at) VALUES ($1, $2, $3, $4, $4) RETURNING *',
      [first_name, last_name, age, unixTime]
    );
    res.status(201).json(result.rows[0]);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.get('/api/users', async (req, res) => {
  try {
    const result = await pool.query('SELECT * FROM users');
    res.json(result.rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.get('/api/users/:id', async (req, res) => {
  try {
    const result = await pool.query('SELECT * FROM users WHERE id = $1', [req.params.id]);
    if (result.rows.length === 0) return res.status(404).json({ error: 'Not found' });
    res.json(result.rows[0]);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.patch('/api/users/:id', async (req, res) => {
  const { first_name, last_name, age } = req.body;
  const setClauses = [];
  const values = [];
  let idx = 1;

  if (first_name !== undefined) { setClauses.push(`first_name = $${idx++}`); values.push(first_name); }
  if (last_name !== undefined) { setClauses.push(`last_name = $${idx++}`); values.push(last_name); }
  if (age !== undefined) { setClauses.push(`age = $${idx++}`); values.push(age); }

  if (setClauses.length === 0) return res.status(400).json({ error: 'No fields to update' });

  const unixTime = Math.floor(Date.now() / 1000);
  setClauses.push(`updated_at = $${idx++}`);
  values.push(unixTime);
  values.push(req.params.id);

  const query = `UPDATE users SET ${setClauses.join(', ')} WHERE id = $${idx} RETURNING *`;
  try {
    const result = await pool.query(query, values);
    if (result.rows.length === 0) return res.status(404).json({ error: 'Not found' });
    res.json(result.rows[0]);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.delete('/api/users/:id', async (req, res) => {
  try {
    const result = await pool.query('DELETE FROM users WHERE id = $1 RETURNING *', [req.params.id]);
    if (result.rows.length === 0) return res.status(404).json({ error: 'Not found' });
    res.json({ message: 'Deleted', data: result.rows[0] });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

const start = async () => {
  await initDatabase();
  await initSchema();
  app.listen(process.env.PORT || 3000, () => {
    console.log('Listening on port ' + (process.env.PORT || 3000));
    console.log('Swagger docs: http://localhost:' + (process.env.PORT || 3000) + '/api-docs');
  });
};

start();