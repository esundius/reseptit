import math
import time
import sqlite3
from flask import Flask
from flask import redirect, render_template, request, session, flash, make_response, g
from werkzeug.security import generate_password_hash, check_password_hash
import markupsafe
import reviews_db
import users_db
import recipes_db
import config

app = Flask(__name__)
app.secret_key = config.secret_key

@app.before_request
def before_request():
    g.start_time = time.time()

@app.after_request
def after_request(response):
    duration = time.time() - g.start_time
    #response.headers.set('X-Response-Time', f'{duration:.5f}s')
    print(f'{request.method} {request.path} completed in {duration:.5f}s')
    return response

@app.route('/')
@app.route('/<int:page>')
def index(page=1):
    page_size = 10
    recipe_count = recipes_db.get_recipe_count()
    page_count = math.ceil(recipe_count / page_size)
    page_count = max(page_count, 1)

    if page < 1:
        return redirect('/1')
    if page > page_count:
        return redirect(f'/{page_count}')
    
    recipes = recipes_db.get_recipes(page, page_size)
    return render_template('index.html.j2', page=page, page_count=page_count, recipes=recipes)

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
        return render_template('register.html.j2', username='')

    if request.method == 'POST':
        username = request.form['username']
        password1 = request.form['password1']
        password2 = request.form['password2']

        if not username or not password1 or not password2:
            flash('ERROR: All fields are required!')
            return render_template('register.html.j2', username=username)

        if password1 != password2:
            flash('ERROR: The passwords do not match!')
            return render_template('register.html.j2', username=username)
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
    require_login()

    if request.method == 'GET':
        return render_template('add_recipe.html.j2')

    if request.method == 'POST':
        name = request.form['name']
        content = request.form['content']
        file = request.files.get('image')
        image = None
        image_type = None
        error_found = False

        if file:
            if not allowed_image(file.filename):
                flash('ERROR: Invalid image file type.')
                file = None
                error_found = True
            else:
                image = file.read()
                image_type = file.filename.rsplit('.', 1)[1].lower()
                if len(image) > config.max_image_size:
                    flash(f'ERROR: Image file size exceeds the maximum limit of {config.max_image_size / (1024 * 1024)} MB.')
                    file, image = None, None
                    error_found = True
        if not name:
            flash('ERROR: Recipe name is required.')
            error_found = True
        if len(name) > 100:
            flash('ERROR: Recipe name is too long (maximum 100 characters).')
            name = name[:100]
            error_found = True
        if len(content) > 5000:
            flash('ERROR: Recipe content is too long (maximum 5000 characters).')
            content = content[:5000]
            error_found = True
        if error_found:
            return render_template('add_recipe.html.j2', name=name, content=content, image=image)
        
        recipes_db.add_recipe(session['user_id'], name, content, image, image_type)
        return redirect('/')

@app.route('/recipe/<int:recipe_id>')
@app.route('/recipe/<int:recipe_id>/<int:page>')
def show_recipe(recipe_id, page=1):
    recipe = recipes_db.get_recipe_by_id(recipe_id)
    if not recipe:
        flash('ERROR: Recipe not found.')
        return redirect('/')
    
    page_size = 10
    if page < 1:
        page = 1
    reviews_count = reviews_db.get_reviews_for_recipe_count(recipe_id)
    page_count = math.ceil(reviews_count / page_size)
    page_count = max(page_count, 1)
    if page > page_count:
        page = page_count
    reviews = reviews_db.get_reviews_for_recipe_paginated(recipe_id, page, page_size)
    
    user_review = None
    if 'user_id' in session:
        user_review = reviews_db.get_user_review_for_recipe(session['user_id'], recipe_id)
    
    return render_template('recipe.html.j2', recipe=recipe, reviews=reviews, page=page, page_count=page_count, reviews_count=reviews_count, user_review=user_review)

@app.route('/search')
@app.route('/search/<int:page>')
def search(page=1):
    query = request.args.get('query')
    recipes = []
    if page < 1:
        page = 1
    page_size = 10
    if query:
        recipe_count = recipes_db.get_search_recipe_count(query)
        page_count = math.ceil(recipe_count / page_size)
        page_count = max(page_count, 1)
        if page > page_count:
            page = page_count
        recipes = recipes_db.search_recipes_paginated(query, page, page_size)
    else:
        page_count = 1
    return render_template('search.html.j2', query=query, recipes=recipes, page=page, page_count=page_count)

@app.route('/edit/<int:recipe_id>', methods=['GET', 'POST'])
def edit_recipe(recipe_id):
    require_login()

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
        name = request.form['name']
        content = request.form['content']
        file = request.files.get('image')
        image = None
        image_type = None
        error_found = False

        if file:
            if not allowed_image(file.filename):
                flash('ERROR: Invalid image file type.')
                file = None
                error_found = True
            else:
                image = file.read()
                image_type = file.filename.rsplit('.', 1)[1].lower()
                if len(image) > config.max_image_size:
                    flash(f'ERROR: Image file size exceeds the maximum limit of {config.max_image_size / (1024 * 1024)} MB.')
                    file, image, image_type = None, None, None
                    error_found = True
        if not name:
            flash('ERROR: Recipe name is required.')
            error_found = True
        if len(name) > 100:
            flash('ERROR: Recipe name is too long (maximum 100 characters).')
            name = name[:100]
            error_found = True
        if len(content) > 5000:
            flash('ERROR: Recipe content is too long (maximum 5000 characters).')
            content = content[:5000]
            error_found = True
        if error_found:
            return render_template('edit_recipe.html.j2', recipe={'id': recipe_id, 'name': name, 'content': content, 'image': image})

        if 'save' in request.form:
            recipes_db.update_recipe(recipe_id, name, content, image, image_type)
        return redirect('/recipe/' + str(recipe_id))

@app.route('/remove/<int:recipe_id>', methods=['GET', 'POST'])
def remove_recipe(recipe_id):
    require_login()

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

@app.route('/user/<username>')
@app.route('/user/<username>/<int:page>')
def show_user(username, page=1):
    user = users_db.get_user(username)
    if not user:
        flash('ERROR: User not found.')
        return redirect('/')
    if page < 1:
        page = 1
    page_size = 10
    recipe_count = users_db.get_user_recipe_count(user['id'])
    page_count = math.ceil(recipe_count / page_size)
    page_count = max(page_count, 1)
    if page > page_count:
        page = page_count
    recipes = users_db.get_user_recipes_paginated(user['id'], page, page_size)
    return render_template('user.html.j2', username=username, recipes=recipes, page=page, page_count=page_count, recipe_count=recipe_count)

@app.route('/add_review/<int:recipe_id>', methods=['POST'])
def add_review(recipe_id):
    require_login()

    recipe = recipes_db.get_recipe_by_id(recipe_id)
    if not recipe:
        flash('ERROR: Recipe not found.')
        return redirect('/')

    if recipe['user_id'] == session['user_id']:
        flash('ERROR: You cannot review your own recipe.')
        return redirect('/recipe/' + str(recipe_id))

    rating = int(request.form['rating'])
    comment = request.form['comment']
    if rating < 1 or rating > 5:
        flash('ERROR: Rating must be between 1 and 5.')
        return redirect('/recipe/' + str(recipe_id))
    if len(comment) > 1000:
        flash('ERROR: Comment is too long (maximum 1000 characters).')
        comment = comment[:1000]

    existing_review = reviews_db.get_user_review_for_recipe(session['user_id'], recipe_id)
    if existing_review:
        flash('ERROR: You have already reviewed this recipe.')
        return redirect('/recipe/' + str(recipe_id))

    reviews_db.add_review(recipe_id, session['user_id'], rating, comment)
    flash('Your review has been added.')
    return redirect('/recipe/' + str(recipe_id))

@app.route('/edit_review/<int:recipe_id>', methods=['POST'])
def edit_review(recipe_id):
    require_login()

    recipe = recipes_db.get_recipe_by_id(recipe_id)
    if not recipe:
        flash('ERROR: Recipe not found.')
        return redirect('/')

    existing_review = reviews_db.get_user_review_for_recipe(session['user_id'], recipe_id)
    if not existing_review:
        flash('ERROR: You have not reviewed this recipe yet.')
        return redirect('/recipe/' + str(recipe_id))

    rating = int(request.form['rating'])
    comment = request.form['comment']
    if rating < 1 or rating > 5:
        flash('ERROR: Rating must be between 1 and 5.')
        return redirect('/recipe/' + str(recipe_id))
    if len(comment) > 1000:
        flash('ERROR: Comment is too long (maximum 1000 characters).')
        comment = comment[:1000]

    if rating == existing_review['rating'] and comment == existing_review['comment']:
        return redirect('/recipe/' + str(recipe_id))

    reviews_db.update_review(existing_review['id'], rating, comment)
    flash('Your review has been updated.')
    return redirect('/recipe/' + str(recipe_id))

@app.route('/delete_review/<int:recipe_id>', methods=['POST'])
def delete_review(recipe_id):
    require_login()

    recipe = recipes_db.get_recipe_by_id(recipe_id)
    if not recipe:
        flash('ERROR: Recipe not found.')
        return redirect('/')

    existing_review = reviews_db.get_user_review_for_recipe(session['user_id'], recipe_id)
    if not existing_review:
        flash('ERROR: You have not reviewed this recipe yet.')
        return redirect('/recipe/' + str(recipe_id))

    reviews_db.delete_review(existing_review['id'])
    flash('Your review has been deleted.')
    return redirect('/recipe/' + str(recipe_id))

@app.route('/image/<int:recipe_id>')
def serve_image(recipe_id):
    image_data = recipes_db.get_recipe_image(recipe_id)
    if not image_data:
        flash('ERROR: Image not found.')
        return redirect('/')
    
    image, image_type = image_data['image'], image_data['image_type']
    response = make_response(bytes(image))
    response.headers.set('Content-Type', f'image/{image_type}')
    return response

def require_login():
    if 'user_id' not in session:
        flash('ERROR: You must be logged in to view this page.')
        return redirect('/login')

def allowed_image(filename):
    return ('.' in filename and
            filename.rsplit('.', 1)[1].lower() in config.ALLOWED_IMAGE_EXTENSIONS)

@app.template_filter()
def show_lines(content):
    content = str(markupsafe.escape(content))
    content = content.replace('\r\n', '<br />').replace('\r', '<br />').replace('\n', '<br />')
    return markupsafe.Markup(content)
