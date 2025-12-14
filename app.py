import math
import time
import sqlite3
from flask import Flask, abort
from flask import redirect, render_template, request, session, flash, make_response, g
from werkzeug.security import generate_password_hash, check_password_hash
import markupsafe
import reviews_db
import users_db
import recipes_db
import tags_db
import config

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

@app.before_request
def before_request():
    g.start_time = time.time()

@app.after_request
def after_request(response):
    duration = time.time() - g.start_time
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
        next_page = request.referrer
        if 'register' in next_page:
            next_page = '/'
        return render_template('login.html.j2', next_page=next_page)

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        next_page = request.form['next_page']

        user = users_db.get_user(username)
        if not user or not check_password_hash(user['password_hash'], password):
            flash('ERROR: User not found or wrong password')
            return render_template('login.html.j2', next_page=next_page)

        session['user_id'] = user['id']
        session['username'] = username
        session['csrf_token'] = config.CSRF_TOKEN_KEY
        flash('Hello, ' + username + '! You have successfully logged in.')
        return redirect(next_page)

@app.route('/logout')
def logout():
    print(f'referrer: {request.referrer}')
    del session['username']
    del session['user_id']
    secure_pages = ['add_recipe', 'edit', 'remove', 'add_review', 'edit_review', 'delete_review']
    
    if not request.referrer or any(page in request.referrer for page in secure_pages):
        return redirect('/')
    else:
        return redirect(request.referrer)

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
        check_csrf_token()
        name = request.form['name']
        content = request.form['content']
        file = request.files.get('image')
        tags = request.form['tags'].casefold().replace(',', ' ').split()
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
                if len(image) > config.MAX_IMAGE_SIZE:
                    flash(f'ERROR: Image file size exceeds the maximum limit of {config.MAX_IMAGE_SIZE / (1024 * 1024)} MB.')
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
        
        recipe_id = recipes_db.add_recipe(session['user_id'], name, content, image, image_type)

        existing_tags = tags_db.get_all_tags()
        tag_name_to_id = {tag['name']: tag['id'] for tag in existing_tags}
        for tag in tags:
            if tag not in tag_name_to_id:
                tag_name_to_id[tag] = tags_db.add_tag(tag)
            try:
                tags_db.add_tag_to_recipe(recipe_id, tag_name_to_id[tag])
            except sqlite3.IntegrityError:
                pass  # Tag already added to recipe, ignore

        flash('Recipe added successfully.')
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
    all_tags = tags_db.get_all_tags()
    tag_name_to_id = {tag['name']: tag['id'] for tag in all_tags}
    query = request.args.get('query')
    selected_tags = request.args.getlist('tags')
    if selected_tags:
        tag_ids = [tag_name_to_id[tag] for tag in selected_tags if tag in tag_name_to_id]
    else:
        tag_ids = [tag_name_to_id[tag] for tag in tag_name_to_id]

    print(f'Search query: {query}, selected tags: {selected_tags}, tag IDs: {tag_ids}')
    recipes = []
    if page < 1:
        page = 1
    page_size = 10
    page_count = 1
    recipe_count = 0
    if query or selected_tags:
        recipe_count = tags_db.get_recipe_count_filtered_by_tags(query, tag_ids)
        page_count = math.ceil(recipe_count / page_size)
        page_count = max(page_count, 1)
        if page > page_count:
            page = page_count
        recipes = tags_db.search_recipes_filtered_by_tags_paginated(query, tag_ids, page, page_size)
    return render_template('search.html.j2', query=query, recipes=recipes, page=page, page_count=page_count, all_tags=all_tags, recipe_count=recipe_count)

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
        check_csrf_token()
        name = request.form['name']
        content = request.form['content']
        file = request.files.get('image')
        tags = request.form['tags'].casefold().replace(',', ' ').split()
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
                if len(image) > config.MAX_IMAGE_SIZE:
                    flash(f'ERROR: Image file size exceeds the maximum limit of {config.MAX_IMAGE_SIZE / (1024 * 1024)} MB.')
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
            existing_tags = tags_db.get_all_tags()
            tag_name_to_id = {tag['name']: tag['id'] for tag in existing_tags}
            tags_before = tags_db.get_tags_for_recipe(recipe_id)
            tag_names_before = [tag['name'] for tag in tags_before]
            for tag in tag_names_before:
                if tag not in tags:
                    tags_db.remove_tag_from_recipe(recipe_id, tag_name_to_id[tag])
                    if not tags_db.is_tag_used(tag_name_to_id[tag]):
                        tags_db.delete_tag(tag_name_to_id[tag])
            for tag in tags:
                if tag not in tag_name_to_id:
                    tag_name_to_id[tag] = tags_db.add_tag(tag)
                try:
                    tags_db.add_tag_to_recipe(recipe_id, tag_name_to_id[tag])
                except sqlite3.IntegrityError:
                    pass  # Tag already added to recipe, ignore
            flash('Recipe updated successfully.')
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
        check_csrf_token()
        if 'continue' in request.form:
            used_tags = tags_db.get_tags_for_recipe(recipe_id)
            recipes_db.delete_recipe(recipe_id)
            for tag in used_tags:
                if not tags_db.is_tag_used(tag['id']):
                    tags_db.delete_tag(tag['id'])
            flash('Recipe removed successfully.')
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
    user_reviews = reviews_db.get_user_reviews(user['id'])
    return render_template('user.html.j2', username=username, recipes=recipes, page=page, page_count=page_count, recipe_count=recipe_count, user_reviews=user_reviews)

@app.route('/add_review/<int:recipe_id>', methods=['POST'])
def add_review(recipe_id):
    require_login()
    check_csrf_token()

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
    check_csrf_token()

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
    check_csrf_token()

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

def check_csrf_token():
    form_token = request.form.get('csrf_token')
    session_token = session.get('csrf_token')
    if not form_token or not session_token or form_token != session_token:
        flash('ERROR: Invalid CSRF token.')
        abort(403)
