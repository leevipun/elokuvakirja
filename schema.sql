CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
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
  owner_id INTEGER NOT NULL REFERENCES users(id),
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

CREATE TABLE user_favorites (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  movie_id INTEGER NOT NULL REFERENCES movies(id) ON DELETE CASCADE,
  UNIQUE(user_id, movie_id)
);

-- MOVIES INDEXIT
CREATE INDEX idx_movies_title ON movies(title);
CREATE INDEX idx_movies_owner_id ON movies(owner_id);
CREATE INDEX idx_movies_category_id ON movies(category_id);
CREATE INDEX idx_movies_director_id ON movies(director_id);
CREATE INDEX idx_movies_platform_id ON movies(streaming_platform_id);
CREATE INDEX idx_movies_year ON movies(year);
CREATE INDEX idx_movies_created_at ON movies(created_at);

-- USER_RATINGS INDEXIT
CREATE INDEX idx_user_ratings_movie_id ON user_ratings(movie_id);
CREATE INDEX idx_user_ratings_user_id ON user_ratings(user_id);
CREATE INDEX idx_user_ratings_created_at ON user_ratings(created_at);
CREATE INDEX idx_user_ratings_movie_rating ON user_ratings(movie_id, rating);
CREATE INDEX idx_user_ratings_rating ON user_ratings(rating) WHERE rating IS NOT NULL;

-- USER_FAVORITES INDEXIT
CREATE INDEX idx_user_favorites_user_id ON user_favorites(user_id);
>>>>>>> Stashed changes
