const { Client } = require('pg');

const client = new Client({
  connectionString: "postgresql://postgres.hgigtknlxmavbwvwvzlz:Chistosa147@aws-1-us-east-1.pooler.supabase.com:6543/postgres",
  ssl: { rejectUnauthorized: false }
});

async function run() {
  await client.connect();
  const res = await client.query('SELECT * FROM cakes');
  console.log(res.rows);
  await client.end();
}

run().catch(console.error);
