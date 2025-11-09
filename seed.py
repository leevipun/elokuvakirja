"""
Seed script to populate the database with test data for performance testing.
This script generates a large amount of realistic movie data.
"""

import sqlite3
import random
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
import os

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
    """Get database connection"""
    con = sqlite3.connect("database.db")
    con.execute("PRAGMA foreign_keys = ON")
    return con

def clear_database():
    """Clear existing data from tables (keeping schema)"""
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
        con.commit()
        print("✓ Database cleared")
    finally:
        con.close()

def seed_users(num_users=50):
    """Generate test users"""
    con = get_connection()
    cursor = con.cursor()
    
    users = []
    for i in range(num_users):
        username = f"user_{i+1}"
        password_hash = generate_password_hash(f"password{i+1}")
        created_at = datetime.now() - timedelta(days=random.randint(1, 365))
        
        cursor.execute(
            "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
            (username, password_hash, created_at)
        )
        users.append((cursor.lastrowid, username))
    
    con.commit()
    con.close()
    print(f"✓ Created {num_users} users")
    return users

def seed_categories():
    """Generate categories"""
    con = get_connection()
    cursor = con.cursor()
    
    for category in CATEGORIES:
        try:
            cursor.execute(
                "INSERT INTO categories (name) VALUES (?)",
                (category,)
            )
        except sqlite3.IntegrityError:
            pass
    
    con.commit()
    con.close()
    print(f"✓ Created {len(CATEGORIES)} categories")

def seed_platforms():
    """Generate streaming platforms"""
    con = get_connection()
    cursor = con.cursor()
    
    for platform in PLATFORMS:
        try:
            cursor.execute(
                "INSERT INTO streaming_platforms (name) VALUES (?)",
                (platform,)
            )
        except sqlite3.IntegrityError:
            pass
    
    con.commit()
    con.close()
    print(f"✓ Created {len(PLATFORMS)} streaming platforms")

def seed_directors():
    """Generate directors"""
    con = get_connection()
    cursor = con.cursor()
    
    for director in DIRECTORS:
        try:
            cursor.execute(
                "INSERT INTO directors (name) VALUES (?)",
                (director,)
            )
        except sqlite3.IntegrityError:
            pass
    
    con.commit()
    con.close()
    print(f"✓ Created {len(DIRECTORS)} directors")

def seed_movies(num_movies=1000):
    """Generate test movies"""
    con = get_connection()
    cursor = con.cursor()
    
    # Get all categories, platforms, directors for random selection
    cursor.execute("SELECT id FROM categories")
    categories = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT id FROM streaming_platforms")
    platforms = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT id FROM directors")
    directors = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT id FROM users")
    users = [row[0] for row in cursor.fetchall()]
    
    for i in range(num_movies):
        title = f"{random.choice(MOVIE_TITLES)} ({i+1})"
        year = random.randint(1980, 2024)
        duration = random.randint(80, 180)
        owner_id = random.choice(users)
        category_id = random.choice(categories) if random.random() > 0.2 else None
        platform_id = random.choice(platforms) if random.random() > 0.2 else None
        director_id = random.choice(directors) if random.random() > 0.2 else None
        created_at = datetime.now() - timedelta(days=random.randint(1, 365))
        
        cursor.execute(
            """INSERT INTO movies 
            (title, year, duration, owner_id, category_id, streaming_platform_id, director_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (title, year, duration, owner_id, category_id, platform_id, director_id, created_at)
        )
    
    con.commit()
    con.close()
    print(f"✓ Created {num_movies} movies")

def seed_ratings(num_ratings=5000):
    """Generate test ratings and reviews"""
    con = get_connection()
    cursor = con.cursor()
    
    # Get all users and movies
    cursor.execute("SELECT id FROM users")
    users = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT id FROM movies")
    movies = [row[0] for row in cursor.fetchall()]
    
    ratings_added = 0
    attempts = 0
    max_attempts = num_ratings * 2  # Allow some duplicates to be skipped
    
    while ratings_added < num_ratings and attempts < max_attempts:
        user_id = random.choice(users)
        movie_id = random.choice(movies)
        rating = round(random.uniform(1, 5), 1)
        watch_date = datetime.now() - timedelta(days=random.randint(1, 365))
        watched_with = random.choice(WATCH_WITH) if random.random() > 0.3 else None
        review = random.choice(REVIEWS) if random.random() > 0.3 else None
        watched = random.choice([0, 1])
        created_at = datetime.now() - timedelta(days=random.randint(1, 365))
        
        try:
            cursor.execute(
                """INSERT INTO user_ratings 
                (user_id, movie_id, rating, watch_date, watched_with, review, watched, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (user_id, movie_id, rating, watch_date, watched_with, review, watched, created_at)
            )
            ratings_added += 1
        except sqlite3.IntegrityError:
            # Skip duplicate ratings for same user/movie combination
            pass
        
        attempts += 1
    
    con.commit()
    con.close()
    print(f"✓ Created {ratings_added} user ratings and reviews")

def seed_favorites(num_favorites=500):
    """Generate test favorite marks"""
    con = get_connection()
    cursor = con.cursor()
    
    # Get all users and movies
    cursor.execute("SELECT id FROM users")
    users = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT id FROM movies")
    movies = [row[0] for row in cursor.fetchall()]
    
    favorites_added = 0
    attempts = 0
    max_attempts = num_favorites * 2
    
    while favorites_added < num_favorites and attempts < max_attempts:
        user_id = random.choice(users)
        movie_id = random.choice(movies)
        
        try:
            cursor.execute(
                """INSERT INTO user_favorites (user_id, movie_id)
                VALUES (?, ?)""",
                (user_id, movie_id)
            )
            favorites_added += 1
        except sqlite3.IntegrityError:
            # Skip duplicate favorites
            pass
        
        attempts += 1
    
    con.commit()
    con.close()
    print(f"✓ Created {favorites_added} favorite marks")

def main():
    """Main seed function"""
    print("\n" + "="*50)
    print("DATABASE SEEDING STARTED")
    print("="*50 + "\n")
    
    # Configuration
    num_users = 2000
    num_movies = 4000000
    num_ratings = 7000000
    num_favorites = 500
    
    try:
        # Check if database exists
        if os.path.exists("database.db"):
            response = input("Database already exists. Clear it? (y/n): ")
            if response.lower() == 'y':
                clear_database()
            else:
                print("Seeding cancelled.")
                return
        
        # Seed in order
        seed_categories()
        seed_platforms()
        seed_directors()
        users = seed_users(num_users)
        seed_movies(num_movies)
        seed_ratings(num_ratings)
        seed_favorites(num_favorites)
        
        print("\n" + "="*50)
        print("SEEDING COMPLETED SUCCESSFULLY!")
        print("="*50)
        print(f"\nSummary:")
        print(f"  • Users: {num_users}")
        print(f"  • Movies: {num_movies}")
        print(f"  • User Ratings: {num_ratings}")
        print(f"  • Favorites: {num_favorites}")
        print(f"  • Categories: {len(CATEGORIES)}")
        print(f"  • Platforms: {len(PLATFORMS)}")
        print(f"  • Directors: {len(DIRECTORS)}")
        print("\nYou can now test the application with:")
        print("  Username: user_1 to user_2000")
        print("  Password: password1 to password2000")
        print("\n" + "="*50 + "\n")
        
    except Exception as e:
        print(f"\n✗ Error during seeding: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
