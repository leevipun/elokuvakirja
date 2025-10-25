from flask import Flask, render_template, request, flash, redirect, session, jsonify, get_flashed_messages
import sqlite3
from werkzeug.security import check_password_hash

app = Flask(__name__, static_url_path='/static')

import users

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template('register.html')
    else:
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        password_conf = request.form.get("password_conf", "")

        if not username or not password:
            flash("Username and password are required")
            return redirect("/register")

        if password != password_conf:
            flash("Passwords do not match")
            return redirect("/register")

        try:
            users.create_user(username, password)
            session["username"] = username
            return redirect("/")
        except sqlite3.IntegrityError:
            flash("Username already exists")
            return redirect("/register")
        
if __name__ == '__main__':
    app.secret_key = 'your_secret_key'
    app.run(debug=True)