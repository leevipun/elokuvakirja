from werkzeug.security import check_password_hash, generate_password_hash

import db 

def create_user(username, password):
    password_hash = generate_password_hash(password)
    sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
    return db.execute(sql, [username, password_hash])