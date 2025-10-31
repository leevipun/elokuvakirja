import db

def get_platforms():
    sql = "SELECT id, name FROM streaming_platforms"
    results = db.query(sql)
    return results if results else None

def add_platform(platform_name):
    """Lisää uusi alusta"""
    sql = "INSERT INTO streaming_platforms (name) VALUES (?)"
    platform_id = db.execute(sql, [platform_name])
    return platform_id
