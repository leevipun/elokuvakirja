CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL
);

CREATE TABLE categories (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT UNIQUE NOT NULL,
  UNIQUE(name)
);

CREATE TABLE movies (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  year INTEGER,
  duration INTEGER,
  category INTEGER REFERENCES categories(id),
  streaming_platform TEXT,
  director TEXT,
  watch_date DATE,
  rating DECIMAL(3,1) CHECK (rating BETWEEN 1 AND 10),
  watched_with TEXT,
  review TEXT,
  favorite BOOLEAN DEFAULT 0,
  rewatchable BOOLEAN DEFAULT 0,
  user_id INTEGER REFERENCES users(id),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);