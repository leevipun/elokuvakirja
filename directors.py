import db

def get_directors():
    sql = "SELECT id, name FROM directors"
    results = db.query(sql)
    return results if results else None


def add_director(director_name):
    """Lisää uusi ohjaaja"""
    sql = "INSERT INTO directors (name) VALUES (?)"
    director_id = db.execute(sql, [director_name])
    return director_id