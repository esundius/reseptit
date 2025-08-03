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

    sql = 'SELECT id, password_hash FROM users WHERE username = ?'
    result = db.query(sql, (username,))
    if not result:
        return 'VIRHE: väärä tunnus tai salasana'
    user_id = result[0]['id']
    password_hash = result[0]['password_hash']

    if check_password_hash(password_hash, password):
        session['user_id'] = user_id
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

@app.route('/add_recipe', methods=['POST'])
def add_recipe():
    name = request.form['name']
    content = request.form['content']
    user_id = session['user_id']
    sql = 'INSERT INTO recipes (name, content, user_id) VALUES (?, ?, ?)'
    db.execute(sql, (name, content, user_id))
    return redirect('/')

@app.route('/recipe/<int:recipe_id>')
def show_recipe(recipe_id):
    sql = '''SELECT r.id, r.name, r.content, r.created, r.user_id, u.username
             FROM recipes r, users u
             WHERE r.user_id = u.id AND r.id = ?'''
    result = db.query(sql, (recipe_id,))
    return render_template('recipe.html', recipe=result)