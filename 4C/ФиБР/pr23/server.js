const express = require('express');
const app = express();
const port = process.env.PORT || 3000;
const serverId = process.env.SERVER_ID || 'unknown';

const users = {
  "1000": {},
  "1001": {}
}

app.get('/', (req, res) => {
  return res.json({
    server: serverId,
    port: parseInt(port)
  });
});

app.get('/users', (_, res) => {
  res.json(users);
})

app.get('/users/:id', (req, res) => {
  const { id } = req.body;
  if (!users[id]) {
    return res.status(404);
  }
  const user = users[id];
  return res.json(user);
})

app.delete('/users/:id', (req, res) => {
  const { id } = req.body;
  if (!users[id]) {
    return res.status(404);
  }
  const user = users[id];
  delete users[id];
  return res.json(user);
})

app.get('/health', (req, res) => {
  return res.status(200).send('OK');
});

app.listen(port, () => {
  console.log(`Server ${serverId} running on port ${port}`);
});