import db

def add_review(recipe_id, user_id, rating, comment=None):
    sql = '''INSERT INTO reviews (recipe_id,
                                  user_id,
                                  rating,
                                  comment)
             VALUES (?, ?, ?, ?)'''
    db.execute(sql, (recipe_id, user_id, rating, comment))

def get_reviews_for_recipe_paginated(recipe_id, page=1, page_size=10):
    sql = '''SELECT rv.id,
                    rv.recipe_id,
                    rv.user_id,
                    rv.rating,
                    rv.comment,
                    rv.created,
                    rv.modified,
                    u.username
             FROM reviews rv, users u
             WHERE rv.user_id = u.id AND
                   rv.recipe_id = ?
             ORDER BY rv.created DESC
             LIMIT ? OFFSET ?'''
    offset = (page - 1) * page_size
    return db.query(sql, (recipe_id, page_size, offset))

def get_reviews_for_recipe_count(recipe_id):
    sql = '''SELECT COUNT(*) AS count
             FROM reviews rv
             WHERE rv.recipe_id = ?'''
    result = db.query(sql, (recipe_id,))
    return result[0]['count'] if result else 0

def get_average_rating_for_recipe(recipe_id):
    sql = '''SELECT AVG(rv.rating) AS average_rating,
                    COUNT(rv.id) AS review_count
             FROM reviews rv
             WHERE rv.recipe_id = ?'''
    result = db.query(sql, (recipe_id,))
    if result and result[0]['review_count'] > 0:
        return {
            'average_rating': result[0]['average_rating'],
            'review_count': result[0]['review_count']
        }
    else:
        return {
            'average_rating': None,
            'review_count': 0
        }

def get_user_review_for_recipe(user_id, recipe_id):
    sql = '''SELECT id,
                    rating,
                    comment,
                    created,
                    modified
             FROM reviews
             WHERE user_id = ? AND
                   recipe_id = ?'''
    result = db.query(sql, (user_id, recipe_id))
    return result[0] if result else None

def get_user_reviews(user_id):
    sql = '''SELECT rv.id,
                    rv.recipe_id,
                    rv.rating,
                    rv.comment,
                    rv.created,
                    rv.modified,
                    r.name AS recipe_name
             FROM reviews rv, recipes r
             WHERE rv.recipe_id = r.id AND
                   rv.user_id = ?
             ORDER BY rv.created DESC
             LIMIT 10'''
    return db.query(sql, (user_id,))

def get_user_review_count(user_id):
    sql = '''SELECT COUNT(*) AS count
             FROM reviews
             WHERE user_id = ?'''
    result = db.query(sql, (user_id,))
    return result[0]['count'] if result else 0

def get_user_reviews_paginated(user_id, page=1, page_size=10):
    offset = (page - 1) * page_size
    sql = '''SELECT rv.id,
                    rv.recipe_id,
                    rv.rating,
                    rv.comment,
                    rv.created,
                    rv.modified,
                    r.name AS recipe_name
             FROM reviews rv, recipes r
             WHERE rv.recipe_id = r.id AND
                   rv.user_id = ?
             ORDER BY rv.created DESC
             LIMIT ? OFFSET ?'''
    return db.query(sql, (user_id, page_size, offset))

def update_review(review_id, rating, comment=None):
    sql = '''UPDATE reviews
             SET rating = ?,
                 comment = ?
             WHERE id = ?'''
    db.execute(sql, (rating, comment, review_id))

def delete_review(review_id):
    sql = '''DELETE FROM reviews
             WHERE id = ?'''
    db.execute(sql, (review_id,))
