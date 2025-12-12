import db

def add_recipe(user_id, name, content=None, image=None, image_type=None):
    sql = '''INSERT INTO recipes (name,
                                  content,
                                  image,
                                  image_type,
                                  user_id)
             VALUES (?, ?, ?, ?, ?)'''
    db.execute(sql, (name, content, image, image_type, user_id))

def get_all_recipes():
    sql = '''SELECT r.id,
                    r.name,
                    r.created,
                    r.modified,
                    r.user_id,
                    u.username
             FROM recipes r, users u
             WHERE r.user_id = u.id
             ORDER BY r.name ASC'''
    return db.query(sql)

def get_recipe_by_id(recipe_id):
    sql = '''SELECT r.id,
                    r.name,
                    r.content,
                    r.image IS NOT NULL AS has_image,
                    r.created,
                    r.modified,
                    r.user_id,
                    u.username
             FROM recipes r, users u
             WHERE r.user_id = u.id AND
                   r.id = ?'''
    recipe = db.query(sql, (recipe_id,))
    return recipe[0] if recipe else None

def get_recipe_image(recipe_id):
    sql = '''SELECT image,
                    image_type
             FROM recipes
             WHERE id = ?'''
    result = db.query(sql, (recipe_id,))
    return result[0] if result else None

def update_recipe(recipe_id, name, content=None, image=None, image_type=None):
    sql = '''UPDATE recipes
             SET name = ?,
                 content = ?,
                 image = ?,
                 image_type = ?
             WHERE id = ?'''
    db.execute(sql, [name, content, image, image_type, recipe_id])

def delete_recipe(recipe_id):
    sql = '''DELETE FROM recipes
             WHERE id = ?'''
    db.execute(sql, [recipe_id])

def search_recipes(query):
    sql = '''SELECT r.id,
                    r.name,
                    r.created,
                    r.modified,
                    r.user_id,
                    u.username
             FROM recipes r, users u
             WHERE r.user_id = u.id AND
                   r.name LIKE ?
             ORDER BY r.name ASC'''
    results = db.query(sql, ['%' + query + '%'])
    return results if results else None
