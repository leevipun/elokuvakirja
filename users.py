from werkzeug.security import generate_password_hash

import db


def create_user(username, password):
    password_hash = generate_password_hash(password)
    sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
    return db.execute(sql, [username, password_hash])


def get_user(username):
    sql = "SELECT id, username, password_hash, created_at FROM users WHERE username = ?"
    result = db.query(sql, [username])
    return result[0] if result else None
