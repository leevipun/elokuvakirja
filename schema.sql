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
  review TEXT,
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

-- MATERIALISOIMATTU RATING-TILASTOTAULU (nopeutus)
CREATE TABLE movie_rating_stats (
  movie_id INTEGER PRIMARY KEY REFERENCES movies(id) ON DELETE CASCADE,
  average_rating REAL,
  total_ratings INTEGER DEFAULT 0,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_movie_rating_stats_average ON movie_rating_stats(average_rating) WHERE average_rating IS NOT NULL;

-- MATERIALISOIMATTU USER-STATS TAULU (käyttäjän tilastot)
CREATE TABLE user_stats (
  user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  total_movies_watched INTEGER DEFAULT 0,
  avg_rating REAL DEFAULT NULL,
  total_favorites INTEGER DEFAULT 0,
  total_watch_hours REAL DEFAULT 0,
  total_ratings_given INTEGER DEFAULT 0,
  total_reviews_written INTEGER DEFAULT 0,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_stats_updated_at ON user_stats(updated_at);

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

-- TRIGGERIT RATING-TILASTOJEN PÄIVITTÄMISEEN
CREATE TRIGGER update_movie_stats_after_insert
AFTER INSERT ON user_ratings
FOR EACH ROW
BEGIN
  INSERT OR REPLACE INTO movie_rating_stats (movie_id, average_rating, total_ratings, updated_at)
  SELECT 
    NEW.movie_id,
    CASE WHEN COUNT(rating) > 0 THEN AVG(CAST(rating AS FLOAT)) ELSE NULL END,
    COUNT(rating),
    CURRENT_TIMESTAMP
  FROM user_ratings
  WHERE movie_id = NEW.movie_id AND rating IS NOT NULL;
  
  -- Update user stats
  INSERT OR REPLACE INTO user_stats (
    user_id, total_movies_watched, avg_rating, total_favorites, 
    total_watch_hours, total_ratings_given, total_reviews_written, updated_at
  )
  SELECT 
    NEW.user_id,
    COUNT(DISTINCT ur.movie_id),
    CASE WHEN COUNT(ur.rating) > 0 THEN AVG(CAST(ur.rating AS FLOAT)) ELSE NULL END,
    COUNT(DISTINCT uf.movie_id),
    COALESCE(SUM(m.duration) / 60.0, 0),
    COUNT(CASE WHEN ur.rating IS NOT NULL THEN 1 END),
    COUNT(CASE WHEN ur.review IS NOT NULL AND ur.review != '' THEN 1 END),
    CURRENT_TIMESTAMP
  FROM user_ratings ur
  LEFT JOIN user_favorites uf ON ur.user_id = uf.user_id
  LEFT JOIN movies m ON ur.movie_id = m.id
  WHERE ur.user_id = NEW.user_id;
END;

CREATE TRIGGER update_movie_stats_after_update
AFTER UPDATE ON user_ratings
FOR EACH ROW
BEGIN
  INSERT OR REPLACE INTO movie_rating_stats (movie_id, average_rating, total_ratings, updated_at)
  SELECT 
    NEW.movie_id,
    CASE WHEN COUNT(rating) > 0 THEN AVG(CAST(rating AS FLOAT)) ELSE NULL END,
    COUNT(rating),
    CURRENT_TIMESTAMP
  FROM user_ratings
  WHERE movie_id = NEW.movie_id AND rating IS NOT NULL;
  
  -- Update user stats
  INSERT OR REPLACE INTO user_stats (
    user_id, total_movies_watched, avg_rating, total_favorites, 
    total_watch_hours, total_ratings_given, total_reviews_written, updated_at
  )
  SELECT 
    NEW.user_id,
    COUNT(DISTINCT ur.movie_id),
    CASE WHEN COUNT(ur.rating) > 0 THEN AVG(CAST(ur.rating AS FLOAT)) ELSE NULL END,
    COUNT(DISTINCT uf.movie_id),
    COALESCE(SUM(m.duration) / 60.0, 0),
    COUNT(CASE WHEN ur.rating IS NOT NULL THEN 1 END),
    COUNT(CASE WHEN ur.review IS NOT NULL AND ur.review != '' THEN 1 END),
    CURRENT_TIMESTAMP
  FROM user_ratings ur
  LEFT JOIN user_favorites uf ON ur.user_id = uf.user_id
  LEFT JOIN movies m ON ur.movie_id = m.id
  WHERE ur.user_id = NEW.user_id;
END;

CREATE TRIGGER update_movie_stats_after_delete
AFTER DELETE ON user_ratings
FOR EACH ROW
BEGIN
  INSERT OR REPLACE INTO movie_rating_stats (movie_id, average_rating, total_ratings, updated_at)
  SELECT 
    OLD.movie_id,
    CASE WHEN COUNT(rating) > 0 THEN AVG(CAST(rating AS FLOAT)) ELSE NULL END,
    COUNT(rating),
    CURRENT_TIMESTAMP
  FROM user_ratings
  WHERE movie_id = OLD.movie_id AND rating IS NOT NULL;
  
  -- Update user stats
  INSERT OR REPLACE INTO user_stats (
    user_id, total_movies_watched, avg_rating, total_favorites, 
    total_watch_hours, total_ratings_given, total_reviews_written, updated_at
  )
  SELECT 
    OLD.user_id,
    COUNT(DISTINCT ur.movie_id),
    CASE WHEN COUNT(ur.rating) > 0 THEN AVG(CAST(ur.rating AS FLOAT)) ELSE NULL END,
    COUNT(DISTINCT uf.movie_id),
    COALESCE(SUM(m.duration) / 60.0, 0),
    COUNT(CASE WHEN ur.rating IS NOT NULL THEN 1 END),
    COUNT(CASE WHEN ur.review IS NOT NULL AND ur.review != '' THEN 1 END),
    CURRENT_TIMESTAMP
  FROM user_ratings ur
  LEFT JOIN user_favorites uf ON ur.user_id = uf.user_id
  LEFT JOIN movies m ON ur.movie_id = m.id
  WHERE ur.user_id = OLD.user_id;
END;

-- Trigger for favorites updates
CREATE TRIGGER update_user_stats_after_favorite_insert
AFTER INSERT ON user_favorites
FOR EACH ROW
BEGIN
  INSERT OR REPLACE INTO user_stats (
    user_id, total_movies_watched, avg_rating, total_favorites, 
    total_watch_hours, total_ratings_given, total_reviews_written, updated_at
  )
  SELECT 
    NEW.user_id,
    COUNT(DISTINCT ur.movie_id),
    CASE WHEN COUNT(ur.rating) > 0 THEN AVG(CAST(ur.rating AS FLOAT)) ELSE NULL END,
    COUNT(DISTINCT uf.movie_id),
    COALESCE(SUM(m.duration) / 60.0, 0),
    COUNT(CASE WHEN ur.rating IS NOT NULL THEN 1 END),
    COUNT(CASE WHEN ur.review IS NOT NULL AND ur.review != '' THEN 1 END),
    CURRENT_TIMESTAMP
  FROM user_ratings ur
  LEFT JOIN user_favorites uf ON ur.user_id = uf.user_id
  LEFT JOIN movies m ON ur.movie_id = m.id
  WHERE ur.user_id = NEW.user_id;
END;

CREATE TRIGGER update_user_stats_after_favorite_delete
AFTER DELETE ON user_favorites
FOR EACH ROW
BEGIN
  INSERT OR REPLACE INTO user_stats (
    user_id, total_movies_watched, avg_rating, total_favorites, 
    total_watch_hours, total_ratings_given, total_reviews_written, updated_at
  )
  SELECT 
    OLD.user_id,
    COUNT(DISTINCT ur.movie_id),
    CASE WHEN COUNT(ur.rating) > 0 THEN AVG(CAST(ur.rating AS FLOAT)) ELSE NULL END,
    COUNT(DISTINCT uf.movie_id),
    COALESCE(SUM(m.duration) / 60.0, 0),
    COUNT(CASE WHEN ur.rating IS NOT NULL THEN 1 END),
    COUNT(CASE WHEN ur.review IS NOT NULL AND ur.review != '' THEN 1 END),
    CURRENT_TIMESTAMP
  FROM user_ratings ur
  LEFT JOIN user_favorites uf ON ur.user_id = uf.user_id
  LEFT JOIN movies m ON ur.movie_id = m.id
  WHERE ur.user_id = OLD.user_id;
END;
