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
  review TEXT,
  rewatchable BOOLEAN DEFAULT 0,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_ratings (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL REFERENCES users(id),
  movie_id INTEGER NOT NULL REFERENCES movies(id),
  rating DECIMAL(2,1) CHECK (rating BETWEEN 1 AND 5),
  watched BOOLEAN DEFAULT 0,
  watch_date DATE,
  watched_with TEXT,
  favorite BOOLEAN DEFAULT 0,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(user_id, movie_id)
);