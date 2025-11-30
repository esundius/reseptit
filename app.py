import sqlite3
from flask import Flask
from flask import redirect, render_template, request, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import users
import db
import config

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route('/')
def index():
    sql = 'SELECT r.id, r.name FROM recipes r'
    recipes = db.query(sql)
    return render_template('index.html.j2', recipes=recipes)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html.j2')

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = users.get_user(username)
        if not user or not check_password_hash(user['password_hash'], password):
            flash('ERROR: User not found or wrong password')
            return render_template('login.html.j2')
        
        session['user_id'] = user['id']
        session['username'] = username
        flash('Hello, ' + username + '! You have successfully logged in.')
        return redirect('/')

@app.route('/logout')
def logout():
    del session['username']
    del session['user_id']
    return redirect('/')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html.j2')
    
    if request.method == 'POST':
        username = request.form['username']
        password1 = request.form['password1']
        password2 = request.form['password2']

        if password1 != password2:
            flash('ERROR: The passwords do not match!')
            return render_template('register.html.j2')
        password_hash = generate_password_hash(password1)

        try:
            users.create_user(username, password_hash)
            flash('User created successfully, please log in')
            return redirect('/login')
        except sqlite3.IntegrityError:
            flash('ERROR: User name already taken')

        return render_template('register.html.j2')

@app.route('/add_recipe', methods=['GET', 'POST'])
def add_recipe():
    if request.method == 'GET':
        return render_template('add_recipe.html.j2')
    
    if request.method == 'POST':
        name = request.form['name']
        content = request.form['content']
        user_id = session['user_id']
        sql = 'INSERT INTO recipes (name, content, user_id) VALUES (?, ?, ?)'
        db.execute(sql, (name, content, user_id))
        return redirect('/')

@app.route('/recipe/<int:recipe_id>')
def show_recipe(recipe_id):
    sql = '''SELECT r.id,
                    r.name,
                    r.content,
                    r.created,
                    r.user_id,
                    u.username
             FROM recipes r, users u
             WHERE r.user_id = u.id AND
                   r.id = ?'''
    result = db.query(sql, (recipe_id,))[0]
    return render_template('recipe.html.j2', recipe=result)

@app.route('/search')
def search():
    query = request.args.get('query')
    results = []
    if query:
        sql = '''SELECT r.id,
                        r.name,
                        r.created,
                        r.user_id,
                        u.username
                 FROM recipes r, users u
                 WHERE r.user_id = u.id AND
                       r.name LIKE ?
                 ORDER BY r.name ASC'''
        results = db.query(sql, ['%' + query + '%'])
    return render_template('search.html.j2', query=query, results=results)

@app.route('/edit/<int:recipe_id>', methods=['GET', 'POST'])
def edit_recipe(recipe_id):
    sql = '''SELECT r.id,
                    r.name,
                    r.content,
                    r.created,
                    r.user_id,
                    u.username
             FROM recipes r, users u
             WHERE r.user_id = u.id AND
                   r.id = ?'''
    recipe = db.query(sql, (recipe_id,))[0]

    if request.method == 'GET':
        return render_template('edit_recipe.html.j2', recipe=recipe)
    
    if request.method == 'POST':
        if 'save' in request.form:
            name = request.form['name']
            content = request.form['content']
            sql = '''UPDATE recipes SET name = ?, content = ? WHERE id = ?'''
            db.execute(sql, [name, content, recipe_id])
        return redirect('/recipe/' + str(recipe_id))

@app.route('/remove/<int:recipe_id>', methods=['GET', 'POST'])
def remove_recipe(recipe_id):
    sql = '''SELECT r.id,
                    r.name,
                    r.content,
                    r.created,
                    r.user_id,
                    u.username
             FROM recipes r, users u
             WHERE r.user_id = u.id AND
                   r.id = ?'''
    recipe = db.query(sql, (recipe_id,))[0]

    if request.method == 'GET':
        return render_template('remove_recipe.html.j2', recipe=recipe)
    
    if request.method == 'POST':
        if 'continue' in request.form:
            sql = '''DELETE FROM recipes WHERE id = ?'''
            db.execute(sql, [recipe_id])
        return redirect('/')

