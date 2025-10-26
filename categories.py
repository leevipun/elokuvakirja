import db

def get_categories():
    sql = "SELECT id, name FROM categories"
    results = db.query(sql)
    return results if results else None

def get_movie_categories(movie_id):
    """Hae elokuvan kaikki kategoriat"""
    sql = """SELECT c.id, c.name, mc.type
             FROM categories c
             JOIN movie_categories mc ON c.id = mc.category_id
             WHERE mc.movie_id = ?
             ORDER BY mc.type = 'primary' DESC"""
    results = db.query(sql, [movie_id])
    return results if results else []

def get_category_movies(category_id):
    """Hae kategorian kaikki elokuvat"""
    sql = """SELECT m.id, m.title, m.year, m.rating, mc.type
             FROM movies m
             JOIN movie_categories mc ON m.id = mc.movie_id
             WHERE mc.category_id = ?
             ORDER BY mc.type = 'primary' DESC, m.title"""
    results = db.query(sql, [category_id])
    return results if results else []

def remove_movie_category(movie_id, category_id):
    """Poista elokuva-kategoria relaatio"""
    sql = "DELETE FROM movie_categories WHERE movie_id = ? AND category_id = ?"
    db.execute(sql, [movie_id, category_id])
    return True


def add_category(category_name):
    """Lisää uusi kategoria"""
    sql = "INSERT INTO categories (name) VALUES (?)"
    category_id = db.execute(sql, [category_name])
    return category_id
    