CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL
);

CREATE TABLE categories (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT UNIQUE NOT NULL
);

CREATE TABLE streaming_platforms (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT UNIQUE NOT NULL
);

CREATE TABLE directors (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT UNIQUE NOT NULL
);

CREATE TABLE movies (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  year INTEGER,
  duration INTEGER,
  category_id INTEGER REFERENCES categories(id),
  streaming_platform_id INTEGER REFERENCES streaming_platforms(id),
  director_id INTEGER REFERENCES directors(id),
  watch_date DATE,
  rating DECIMAL(3,1) CHECK (rating BETWEEN 1 AND 10),
  watched_with TEXT,
  review TEXT,
  favorite BOOLEAN DEFAULT 0,
  rewatchable BOOLEAN DEFAULT 0,
  user_id INTEGER REFERENCES users(id),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);