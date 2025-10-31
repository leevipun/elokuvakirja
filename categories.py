import db

def get_categories():
    sql = "SELECT id, name FROM categories"
    results = db.query(sql)
    return results if results else None

def add_category(category_name):
    """Lisää uusi kategoria"""
    sql = "INSERT INTO categories (name) VALUES (?)"
    category_id = db.execute(sql, [category_name])
    return category_id
