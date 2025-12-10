import sqlite3
from flask import Flask
from flask import redirect, render_template, request, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import users_db
import recipes_db
import config

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route('/')
def index():
    recipes = recipes_db.get_all_recipes()
    return render_template('index.html.j2', recipes=recipes)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html.j2')

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = users_db.get_user(username)
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
            users_db.create_user(username, password_hash)
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
        recipes_db.add_recipe(request.form['name'], request.form['content'], session['user_id'])
        return redirect('/')

@app.route('/recipe/<int:recipe_id>')
def show_recipe(recipe_id):
    recipe = recipes_db.get_recipe_by_id(recipe_id)
    if not recipe:
        flash('ERROR: Recipe not found.')
        return redirect('/')
    return render_template('recipe.html.j2', recipe=recipe)

@app.route('/search')
def search():
    query = request.args.get('query')
    results = []
    if query:
        results = recipes_db.search_recipes(query)
    return render_template('search.html.j2', query=query, results=results)

@app.route('/edit/<int:recipe_id>', methods=['GET', 'POST'])
def edit_recipe(recipe_id):
    recipe = recipes_db.get_recipe_by_id(recipe_id)
    if not recipe:
        flash('ERROR: Recipe not found.')
        return redirect('/')
    if 'user_id' not in session or session['user_id'] != recipe['user_id']:
        flash('ERROR: You do not have permission to edit this recipe.')
        return redirect('/recipe/' + str(recipe_id))

    if request.method == 'GET':
        return render_template('edit_recipe.html.j2', recipe=recipe)

    if request.method == 'POST':
        if 'save' in request.form:
            recipes_db.update_recipe(recipe_id, request.form['name'], request.form['content'])
        return redirect('/recipe/' + str(recipe_id))

@app.route('/remove/<int:recipe_id>', methods=['GET', 'POST'])
def remove_recipe(recipe_id):
    recipe = recipes_db.get_recipe_by_id(recipe_id)
    if not recipe:
        flash('ERROR: Recipe not found.')
        return redirect('/')
    if 'user_id' not in session or session['user_id'] != recipe['user_id']:
        flash('ERROR: You do not have permission to remove this recipe.')
        return redirect('/recipe/' + str(recipe_id))

    if request.method == 'GET':
        return render_template('remove_recipe.html.j2', recipe=recipe)

    if request.method == 'POST':
        if 'continue' in request.form:
            recipes_db.delete_recipe(recipe_id)
        return redirect('/')
