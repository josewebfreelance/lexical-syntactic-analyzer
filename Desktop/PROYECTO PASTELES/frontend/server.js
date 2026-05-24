const express = require('express');
const { Client } = require('pg');
const app = express();

app.use(express.json());

const client = new Client({
  connectionString: "postgresql://postgres.hgigtknlxmavbwvwvzlz:Chistosa147@aws-1-us-east-1.pooler.supabase.com:6543/postgres",
  ssl: { rejectUnauthorized: false }
});

client.connect();

// GET todos los pasteles
app.get('/cakes', async (req, res) => {
  const result = await client.query('SELECT * FROM cakes');
  res.json(result.rows);
});

// POST crear un pedido y bajar stock
app.post('/orders', async (req, res) => {
  const { cake_id, quantity, customer_name } = req.body;
  await client.query(
    'INSERT INTO orders (cake_id, quantity, customer_name) VALUES ($1, $2, $3)',
    [cake_id, quantity, customer_name]
  );
  await client.query('UPDATE cakes SET stock = stock - $1 WHERE id = $2', [quantity, cake_id]);
  res.json({ ok: true });
});

app.listen(3000, () => console.log('Servidor en http://localhost:3000'));
