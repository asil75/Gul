SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  tg_id BIGINT UNIQUE,
  role TEXT,
  phone TEXT,
  is_blocked INT DEFAULT 0
);

CREATE TABLE IF NOT EXISTS ratings (
  id SERIAL PRIMARY KEY,
  courier_tg_id BIGINT,
  shop_tg_id BIGINT,
  order_id BIGINT,
  rating INT CHECK (rating >= 1 AND rating <= 5),
  comment TEXT,
  created_at TEXT
);

CREATE TABLE IF NOT EXISTS orders (
  id SERIAL PRIMARY KEY,
  shop_tg_id BIGINT,
  courier_tg_id BIGINT,
  from_address TEXT,
  shop_contact TEXT,
  to_address TEXT,
  to_apt TEXT,
  client_name TEXT,
  client_phone TEXT,
  price DOUBLE PRECISION,
  status TEXT,
  log TEXT,
  created_at TEXT,
  return_for BIGINT DEFAULT NULL,
  paid_to_courier INT DEFAULT 0,
  paid_at TEXT DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS courier_messages (
  id SERIAL PRIMARY KEY,
  order_id BIGINT,
  courier_tg_id BIGINT,
  message_id BIGINT,
  created_at TEXT
);

CREATE TABLE IF NOT EXISTS payments (
  id SERIAL PRIMARY KEY,
  order_id BIGINT,
  shop_tg_id BIGINT,
  courier_tg_id BIGINT,
  amount DOUBLE PRECISION,
  paid_at TEXT
);
"""