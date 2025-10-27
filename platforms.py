import db

def get_platforms():
    sql = "SELECT id, name FROM streaming_platforms"
    results = db.query(sql)
    return results if results else None

def get_movie_platforms(movie_id):
    """Hae elokuvan kaikki alustat"""
    sql = """SELECT sp.id, sp.name 
             FROM streaming_platforms sp
             JOIN platform_movies pm ON sp.id = pm.platform_id
             WHERE pm.movie_id = ?"""
    results = db.query(sql, [movie_id])
    return results if results else []

def add_platform(platform_name):
    """Lisää uusi alusta"""
    sql = "INSERT INTO streaming_platforms (name) VALUES (?)"
    platform_id = db.execute(sql, [platform_name])
    return platform_id

