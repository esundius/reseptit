import sqlite3
from flask import Flask
from flask import redirect, render_template, request, session
from werkzeug.security import generate_password_hash, check_password_hash
import db
import config

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route('/')
def index():
    sql = 'SELECT r.id, r.name FROM recipes r'
    recipes = db.query(sql)
    return render_template('index.html', recipes=recipes)

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    sql = 'SELECT password_hash FROM users WHERE username = ?'
    query = db.query(sql, (username,))
    if not query:
        return 'VIRHE: väärä tunnus tai salasana'
    password_hash = query[0][0]

    if check_password_hash(password_hash, password):
        session['username'] = username
        return redirect('/')
    else:
        return 'VIRHE: väärä tunnus tai salasana'

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/create', methods=['POST'])
def create():
    username = request.form['username']
    password1 = request.form['password1']
    password2 = request.form['password2']
    if password1 != password2:
        return 'VIRHE: salasanat eivät ole samat'
    password_hash = generate_password_hash(password1)

    try:
        sql = 'INSERT INTO users (username, password_hash) VALUES (?, ?)'
        db.execute(sql, (username, password_hash))
    except sqlite3.IntegrityError:
        return 'VIRHE: tunnus on jo varattu'
    
    return render_template('create.html')