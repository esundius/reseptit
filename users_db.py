import db

def create_user(username, password_hash):
    sql = '''INSERT INTO users (username,
                                password_hash)
             VALUES (?, ?)'''
    db.execute(sql, (username, password_hash))

def get_user(username):
    sql = '''SELECT id,
                    username,
                    password_hash
             FROM users
             WHERE username = ?'''
    result = db.query(sql, (username,))
    return result[0] if result else None

def get_user_recipes(user_id):
    sql = '''SELECT r.id,
                    r.name,
                    r.created,
                    r.modified,
                    r.user_id
             FROM recipes r
             WHERE r.user_id = ?
             ORDER BY r.name ASC'''
    return db.query(sql, (user_id,))

def get_user_recipe_count(user_id):
    sql = '''SELECT COUNT(*) AS count
             FROM recipes r
             WHERE r.user_id = ?'''
    result = db.query(sql, (user_id,))
    return result[0]['count'] if result else 0

def get_user_recipes_paginated(user_id, page, page_size):
    offset = (page - 1) * page_size
    sql = '''SELECT r.id,
                    r.name,
                    r.created,
                    r.modified,
                    r.user_id,
                    (SELECT AVG(rv.rating) FROM reviews rv WHERE rv.recipe_id = r.id) AS average_rating,
                    (SELECT COUNT(rv.id) FROM reviews rv WHERE rv.recipe_id = r.id) AS review_count
             FROM recipes r
             WHERE r.user_id = ?
             ORDER BY r.name ASC
             LIMIT ? OFFSET ?'''
    return db.query(sql, (user_id, page_size, offset))
