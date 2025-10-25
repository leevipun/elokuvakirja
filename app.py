from flask import Flask, render_template, request, flash, redirect, session, jsonify, get_flashed_messages
import sqlite3
from werkzeug.security import check_password_hash

app = Flask(__name__, static_url_path='/static')

@app.route('/')
def index():
    return render_template('index.html')