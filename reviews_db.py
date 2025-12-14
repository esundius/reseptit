import db

def add_review(recipe_id, user_id, rating, comment=None):
    sql = '''INSERT INTO reviews (recipe_id,
                                  user_id,
                                  rating,
                                  comment)
             VALUES (?, ?, ?, ?)'''
    db.execute(sql, (recipe_id, user_id, rating, comment))

def get_reviews_for_recipe(recipe_id):
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
             ORDER BY rv.created DESC'''
    return db.query(sql, (recipe_id,))

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
             ORDER BY rv.created DESC'''
    return db.query(sql, (user_id,))
