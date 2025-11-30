import db

def add_recipe(name, content, user_id):
    sql = 'INSERT INTO recipes (name, content, user_id) VALUES (?, ?, ?)'
    db.execute(sql, (name, content, user_id))

def get_all_recipes():
    sql = '''SELECT r.id,
                    r.name,
                    r.created,
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
                    r.created,
                    r.user_id,
                    u.username
             FROM recipes r, users u
             WHERE r.user_id = u.id AND
                   r.id = ?'''
    recipe = db.query(sql, (recipe_id,))
    return recipe[0] if recipe else []

def update_recipe(recipe_id, name, content):
    sql = 'UPDATE recipes SET name = ?, content = ? WHERE id = ?'
    db.execute(sql, [name, content, recipe_id])

def delete_recipe(recipe_id):
    sql = 'DELETE FROM recipes WHERE id = ?'
    db.execute(sql, [recipe_id])

def search_recipes(query):
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
    return results if results else []
