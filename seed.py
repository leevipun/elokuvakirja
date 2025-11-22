"""
Seed script to populate the database with test data for performance testing.
This script generates a large amount of realistic movie data.
"""

import sqlite3
import random
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
import os
import sys

# Sample data for realistic generation
MOVIE_TITLES = [
    "The Shawshank Redemption", "The Godfather", "The Dark Knight", "Pulp Fiction",
    "Forrest Gump", "Inception", "The Matrix", "Interstellar", "Gladiator",
    "Titanic", "Avatar", "The Avengers", "Iron Man", "Captain America", "Thor",
    "Black Panther", "Wonder Woman", "Aquaman", "The Flash", "Deadpool",
    "Logan", "X-Men", "Fantastic Four", "Doctor Strange", "Spider-Man",
    "Jurassic Park", "The Lion King", "Frozen", "Toy Story", "Finding Nemo",
    "The Incredibles", "Inside Out", "Coco", "Moana", "Encanto",
    "The Notebook", "Titanic", "La La Land", "The Fault in Our Stars", "When Harry Met Sally",
    "Parasite", "Minari", "Squid Game", "Everything Everywhere All at Once", "Past Lives",
    "The Silence of the Lambs", "The Usual Suspects", "Memories of Murder", "Zodiac", "Se7en",
    "Oppenheimer", "Barbie", "Killers of the Flower Moon", "Elemental", "Dungeons & Dragons",
]

DIRECTORS = [
    "Steven Spielberg", "Christopher Nolan", "Martin Scorsese", "Quentin Tarantino",
    "Francis Ford Coppola", "Stanley Kubrick", "Ang Lee", "Denis Villeneuve",
    "Ridley Scott", "James Cameron", "Peter Jackson", "Guillermo del Toro",
    "The Coen Brothers", "David Fincher", "Darren Aronofsky", "Joel Coen",
    "Bong Joon-ho", "Akira Kurosawa", "Ingmar Bergman", "Stanley Donen",
    "Spike Lee", "Barry Jenkins", "Ari Aster", "Robert Eggers", "A.A. Milne",
    "Tim Burton", "Wes Anderson", "Paul Thomas Anderson", "Jeff Nichols", "Brady Corbet",
]

CATEGORIES = [
    "Action", "Adventure", "Animation", "Biography", "Comedy", "Crime", "Documentary",
    "Drama", "Family", "Fantasy", "Film-Noir", "History", "Horror", "Music", "Mystery",
    "Romance", "Sci-Fi", "Sport", "Thriller", "War", "Western", "Anime", "Bollywood",
]

PLATFORMS = [
    "Netflix", "Amazon Prime Video", "Disney+", "Hulu", "HBO Max", "Apple TV+",
    "Paramount+", "Peacock", "Disney Plus", "Vimeo", "Tubi", "Pluto TV", "Crunchyroll",
    "Sonarr", "Kodi", "Plex", "YouTube", "Streaming Cinema", "Screening Room", "iTunes",
]

WATCH_WITH = [
    "Alone", "Family", "Friends", "Partner", "Colleagues", "Friends & Family",
    "Girlfriend", "Boyfriend", "Wife", "Husband", "Kids", "Parents", "Siblings",
    "Date", "Group", "Movie Night", "Cinema",
]

REVIEWS = [
    "Absolutely fantastic!",
    "Really enjoyed this one.",
    "Not bad, could be better.",
    "Masterpiece!",
    "Waste of time.",
    "Better than I expected.",
    "Disappointing ending.",
    "Best movie ever!",
    "Average.",
    "Would watch again.",
    "Great cinematography.",
    "Excellent performance.",
    "Could have been shorter.",
    "Highly recommend!",
    "Not my style.",
    "Incredible storytelling.",
    "Emotional rollercoaster.",
    "Thought-provoking.",
    "Action-packed!",
    "Couldn't stop watching.",
]

def get_connection():
    """Get database connection with max optimizations"""
    con = sqlite3.connect("database.db", timeout=60)
    con.execute("PRAGMA foreign_keys = OFF")  # Disable during seeding
    con.execute("PRAGMA journal_mode = WAL")
    con.execute("PRAGMA synchronous = OFF")  # DANGEROUS but fastest for seeding
    con.execute("PRAGMA cache_size = -128000")  # 128MB cache
    con.execute("PRAGMA temp_store = MEMORY")
    con.execute("PRAGMA query_only = FALSE")
    return con

def disable_all_triggers(con):
    """Disable all triggers for faster bulk insert"""
    cursor = con.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='trigger'")
    triggers = cursor.fetchall()
    for trigger in triggers:
        try:
            cursor.execute(f"DROP TRIGGER IF EXISTS {trigger[0]}")
        except:
            pass
    con.commit()

def recreate_triggers_from_schema(con):
    """Recreate triggers from schema"""
    cursor = con.cursor()
    # Read and execute schema with triggers
    with open("schema.sql", "r") as f:
        schema = f.read()
    
    # Extract only trigger statements
    trigger_statements = [stmt.strip() for stmt in schema.split(";") if "TRIGGER" in stmt and stmt.strip()]
    
    for trigger_sql in trigger_statements:
        if trigger_sql:
            try:
                cursor.execute(trigger_sql)
            except:
                pass
    con.commit()

def clear_database():
    """Clear existing data from tables"""
    con = get_connection()
    cursor = con.cursor()
    
    try:
        cursor.execute("DELETE FROM user_favorites")
        cursor.execute("DELETE FROM user_ratings")
        cursor.execute("DELETE FROM movies")
        cursor.execute("DELETE FROM users")
        cursor.execute("DELETE FROM categories")
        cursor.execute("DELETE FROM streaming_platforms")
        cursor.execute("DELETE FROM directors")
        cursor.execute("DELETE FROM user_stats")
        cursor.execute("DELETE FROM movie_rating_stats")
        con.commit()
        print("✓ Database cleared")
    finally:
        con.close()

def progress_bar(current, total, label=""):
    """Display a simple progress bar"""
    pct = (current / total) * 100
    filled = int(50 * current / total)
    bar = "█" * filled + "░" * (50 - filled)
    sys.stdout.write(f"\r{label} [{bar}] {pct:.1f}% ({current}/{total})")
    sys.stdout.flush()

def seed_users(num_users=50):
    """Generate test users"""
    con = get_connection()
    cursor = con.cursor()
    
    users_data = []
    for i in range(num_users):
        username = f"user_{i+1}"
        password_hash = generate_password_hash(f"password{i+1}")
        created_at = datetime.now() - timedelta(days=random.randint(1, 365))
        users_data.append((username, password_hash, created_at))
    
    cursor.executemany(
        "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
        users_data
    )
    
    con.commit()
    cursor.execute("SELECT id FROM users")
    user_ids = [row[0] for row in cursor.fetchall()]
    con.close()
    
    print(f"\n✓ Created {num_users} users")
    return user_ids

def seed_categories():
    """Generate categories"""
    con = get_connection()
    cursor = con.cursor()
    
    cursor.executemany(
        "INSERT OR IGNORE INTO categories (name) VALUES (?)",
        [(cat,) for cat in CATEGORIES]
    )
    
    con.commit()
    con.close()
    print(f"✓ Created {len(CATEGORIES)} categories")

def seed_platforms():
    """Generate streaming platforms"""
    con = get_connection()
    cursor = con.cursor()
    
    cursor.executemany(
        "INSERT OR IGNORE INTO streaming_platforms (name) VALUES (?)",
        [(platform,) for platform in PLATFORMS]
    )
    
    con.commit()
    con.close()
    print(f"✓ Created {len(PLATFORMS)} platforms")

def seed_directors():
    """Generate directors"""
    con = get_connection()
    cursor = con.cursor()
    
    cursor.executemany(
        "INSERT OR IGNORE INTO directors (name) VALUES (?)",
        [(director,) for director in DIRECTORS]
    )
    
    con.commit()
    con.close()
    print(f"✓ Created {len(DIRECTORS)} directors")

def seed_movies(num_movies=1000, user_ids=None):
    """Generate test movies with batch inserts"""
    if not user_ids:
        con = get_connection()
        cursor = con.cursor()
        cursor.execute("SELECT id FROM users")
        user_ids = [row[0] for row in cursor.fetchall()]
        con.close()
    
    con = get_connection()
    cursor = con.cursor()
    
    cursor.execute("SELECT id FROM categories")
    categories = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT id FROM streaming_platforms")
    platforms = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT id FROM directors")
    directors = [row[0] for row in cursor.fetchall()]
    
    batch_size = 50000
    movies_data = []
    
    for i in range(num_movies):
        title = f"{random.choice(MOVIE_TITLES)} ({i+1})"
        year = random.randint(1980, 2024)
        duration = random.randint(80, 180)
        owner_id = random.choice(user_ids)
        category_id = random.choice(categories) if random.random() > 0.2 else None
        platform_id = random.choice(platforms) if random.random() > 0.2 else None
        director_id = random.choice(directors) if random.random() > 0.2 else None
        created_at = datetime.now() - timedelta(days=random.randint(1, 365))
        
        movies_data.append((title, year, duration, owner_id, category_id, platform_id, director_id, created_at))
        
        if len(movies_data) >= batch_size:
            cursor.executemany(
                """INSERT INTO movies 
                (title, year, duration, owner_id, category_id, streaming_platform_id, director_id, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                movies_data
            )
            con.commit()
            progress_bar(i + 1, num_movies, f"Creating movies")
            movies_data = []
    
    if movies_data:
        cursor.executemany(
            """INSERT INTO movies 
            (title, year, duration, owner_id, category_id, streaming_platform_id, director_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            movies_data
        )
        con.commit()
    
    con.close()
    print(f"\n✓ Created {num_movies} movies")

def seed_ratings(num_ratings=5000, user_ids=None, movie_ids=None):
    """Generate test ratings with efficient duplicate avoidance"""
    if not user_ids:
        con = get_connection()
        cursor = con.cursor()
        cursor.execute("SELECT id FROM users")
        user_ids = [row[0] for row in cursor.fetchall()]
        cursor.execute("SELECT id FROM movies")
        movie_ids = [row[0] for row in cursor.fetchall()]
        con.close()
    
    con = get_connection()
    cursor = con.cursor()
    
    # Pre-generate unique pairs in memory
    seen = set()
    ratings_data = []
    attempts = 0
    max_attempts = num_ratings * 2
    
    print(f"Generating {num_ratings} unique ratings...")
    while len(ratings_data) < num_ratings and attempts < max_attempts:
        user_id = random.choice(user_ids)
        movie_id = random.choice(movie_ids)
        
        if (user_id, movie_id) not in seen:
            seen.add((user_id, movie_id))
            rating = round(random.uniform(1, 5), 1)
            watch_date = (datetime.now() - timedelta(days=random.randint(1, 365))).date()
            watched_with = random.choice(WATCH_WITH) if random.random() > 0.3 else None
            watched = random.choice([0, 1])
            review = random.choice(REVIEWS) if random.random() > 0.5 else None
            created_at = datetime.now() - timedelta(days=random.randint(1, 365))
            
            ratings_data.append((user_id, movie_id, rating, watch_date, watched_with, watched, review, created_at))
        
        attempts += 1
        if attempts % 100000 == 0:
            progress_bar(len(ratings_data), num_ratings, "Generating ratings")
    
    print(f"\n")
    
    # Batch insert in very large chunks
    batch_size = 100000
    for i in range(0, len(ratings_data), batch_size):
        batch = ratings_data[i:i+batch_size]
        cursor.executemany(
            """INSERT INTO user_ratings 
            (user_id, movie_id, rating, watch_date, watched_with, watched, review, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            batch
        )
        con.commit()
        progress_bar(i + len(batch), len(ratings_data), "Inserting ratings")
    
    con.close()
    print(f"\n✓ Created {len(ratings_data)} ratings")

def seed_favorites(num_favorites=500, user_ids=None, movie_ids=None):
    """Generate test favorite marks"""
    if not user_ids:
        con = get_connection()
        cursor = con.cursor()
        cursor.execute("SELECT id FROM users")
        user_ids = [row[0] for row in cursor.fetchall()]
        cursor.execute("SELECT id FROM movies")
        movie_ids = [row[0] for row in cursor.fetchall()]
        con.close()
    
    con = get_connection()
    cursor = con.cursor()
    
    seen = set()
    favorites_data = []
    attempts = 0
    max_attempts = num_favorites * 3
    
    while len(favorites_data) < num_favorites and attempts < max_attempts:
        user_id = random.choice(user_ids)
        movie_id = random.choice(movie_ids)
        
        if (user_id, movie_id) not in seen:
            seen.add((user_id, movie_id))
            favorites_data.append((user_id, movie_id))
        
        attempts += 1
    
    cursor.executemany(
        "INSERT INTO user_favorites (user_id, movie_id) VALUES (?, ?)",
        favorites_data
    )
    con.commit()
    con.close()
    
    print(f"✓ Created {len(favorites_data)} favorites")

def populate_user_stats():
    """Populate user_stats in one efficient batch operation"""
    con = get_connection()
    con.execute("PRAGMA foreign_keys = ON")
    cursor = con.cursor()
    
    print("Calculating user statistics...")
    
    cursor.execute(
        """INSERT OR REPLACE INTO user_stats (
            user_id, 
            total_movies_watched, 
            avg_rating, 
            total_favorites, 
            total_watch_hours, 
            total_ratings_given, 
            total_reviews_written, 
            updated_at
        )
        SELECT 
            ur.user_id,
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
        GROUP BY ur.user_id"""
    )
    
    con.commit()
    con.close()
    print("✓ User statistics calculated")

def main():
    """Main seed function"""
    print("\n" + "="*60)
    print("DATABASE SEEDING - OPTIMIZED FOR PERFORMANCE")
    print("="*60 + "\n")
    
    # RECOMMENDED: These numbers complete in ~5-10 minutes
    num_users = 100          # Increase if needed
    num_movies = 50000       # Adjust this
    num_ratings = 500000     # Adjust this
    num_favorites = 1000     # Adjust this
    
    print("Current configuration:")
    print(f"  • Users: {num_users}")
    print(f"  • Movies: {num_movies}")
    print(f"  • Ratings: {num_ratings}")
    print(f"  • Favorites: {num_favorites}")
    print(f"\nEstimated time: 5-10 minutes\n")
    
    try:
        if os.path.exists("database.db"):
            response = input("Database already exists. Clear it? (y/n): ")
            if response.lower() == 'y':
                clear_database()
            else:
                print("Seeding cancelled.")
                return
        
        # Seed basic data
        seed_categories()
        seed_platforms()
        seed_directors()
        user_ids = seed_users(num_users)
        seed_movies(num_movies, user_ids)
        
        # Get movie IDs
        con = get_connection()
        cursor = con.cursor()
        cursor.execute("SELECT id FROM movies")
        movie_ids = [row[0] for row in cursor.fetchall()]
        con.close()
        
        # Seed ratings and favorites
        seed_ratings(num_ratings, user_ids, movie_ids)
        seed_favorites(num_favorites, user_ids, movie_ids)
        
        # Recreate triggers and calculate stats
        con = get_connection()
        recreate_triggers_from_schema(con)
        con.close()
        
        populate_user_stats()
        
        print("\n" + "="*60)
        print("SEEDING COMPLETED SUCCESSFULLY! ✓")
        print("="*60)
        print(f"\nSummary:")
        print(f"  • Users: {num_users}")
        print(f"  • Movies: {num_movies}")
        print(f"  • Ratings: {num_ratings}")
        print(f"  • Favorites: {num_favorites}")
        print(f"\nTest credentials:")
        print(f"  Username: user_1 to user_{num_users}")
        print(f"  Password: password1 to password{num_users}")
        print("\n" + "="*60 + "\n")
        
    except Exception as e:
        print(f"\n✗ Error during seeding: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
