import db

def add_tag(name):
    sql = '''INSERT INTO tags (name)
             VALUES (?)'''
    db.execute(sql, (name,))
    return db.last_insert_id()

def delete_tag(tag_id):
    sql = '''DELETE FROM tags
             WHERE id = ?'''
    db.execute(sql, (tag_id,))

def get_all_tags():
    sql = '''SELECT t.id,
                    t.name
             FROM tags t
             ORDER BY t.name ASC'''
    return db.query(sql)

def add_tag_to_recipe(recipe_id, tag_id):
    sql = '''INSERT INTO recipe_tags (recipe_id, tag_id)
             VALUES (?, ?)'''
    db.execute(sql, (recipe_id, tag_id))

def remove_tag_from_recipe(recipe_id, tag_id):
    sql = '''DELETE FROM recipe_tags
             WHERE recipe_id = ? AND
                   tag_id = ?'''
    db.execute(sql, (recipe_id, tag_id))

def get_tags_for_recipe(recipe_id):
    sql = '''SELECT t.id,
                    t.name
             FROM tags t, recipe_tags rt
             WHERE rt.recipe_id = ? AND
                   rt.tag_id = t.id
             ORDER BY t.name ASC'''
    return db.query(sql, (recipe_id,))

def get_recipes_for_tag(tag_id):
    sql = '''SELECT r.id,
                    r.name,
                    r.created,
                    r.modified,
                    r.user_id,
                    u.username,
                    (SELECT AVG(rv.rating) FROM reviews rv WHERE rv.recipe_id = r.id) AS average_rating,
                    (SELECT COUNT(rv.id) FROM reviews rv WHERE rv.recipe_id = r.id) AS review_count
             FROM recipes r, users u, recipe_tags rt
             WHERE rt.tag_id = ? AND
                   rt.recipe_id = r.id AND
                   r.user_id = u.id
             ORDER BY r.name ASC'''
    return db.query(sql, (tag_id,))

def get_recipes_for_tags(tag_ids):
    placeholders = ','.join('?' for _ in tag_ids)
    sql = f'''SELECT DISTINCT r.id,
                             r.name,
                             r.created,
                             r.modified,
                             r.user_id,
                             u.username,
                             (SELECT AVG(rv.rating) FROM reviews rv WHERE rv.recipe_id = r.id) AS average_rating,
                             (SELECT COUNT(rv.id) FROM reviews rv WHERE rv.recipe_id = r.id) AS review_count
              FROM recipes r, users u, recipe_tags rt
              WHERE rt.tag_id IN ({placeholders}) AND
                    rt.recipe_id = r.id AND
                    r.user_id = u.id
              ORDER BY r.name ASC'''
    return db.query(sql, tag_ids)

def get_recipes_for_tag_paginated(tag_id, page, page_size):
    offset = (page - 1) * page_size
    sql = '''SELECT r.id,
                    r.name,
                    r.created,
                    r.modified,
                    r.user_id,
                    u.username,
                    (SELECT AVG(rv.rating) FROM reviews rv WHERE rv.recipe_id = r.id) AS average_rating,
                    (SELECT COUNT(rv.id) FROM reviews rv WHERE rv.recipe_id = r.id) AS review_count
             FROM recipes r, users u, recipe_tags rt
             WHERE rt.tag_id = ? AND
                   rt.recipe_id = r.id AND
                   r.user_id = u.id
             ORDER BY r.name ASC
             LIMIT ? OFFSET ?'''
    return db.query(sql, (tag_id, page_size, offset))

def get_recipe_count_for_tag(tag_id):
    sql = '''SELECT COUNT(*) AS count
             FROM recipe_tags rt
             WHERE rt.tag_id = ?'''
    result = db.query(sql, (tag_id,))
    return result[0]['count'] if result else 0

def search_recipes_filtered_by_tags(query, tag_ids):
    placeholders = ','.join('?' for _ in tag_ids)
    sql = f'''SELECT DISTINCT r.id,
                             r.name,
                             r.created,
                             r.modified,
                             r.user_id,
                             u.username,
                             (SELECT AVG(rv.rating) FROM reviews rv WHERE rv.recipe_id = r.id) AS average_rating,
                             (SELECT COUNT(rv.id) FROM reviews rv WHERE rv.recipe_id = r.id) AS review_count
              FROM recipes r, users u, recipe_tags rt
              WHERE r.user_id = u.id AND
                    (r.name LIKE ? OR r.content LIKE ?) AND
                    rt.recipe_id = r.id AND
                    rt.tag_id IN ({placeholders})
              ORDER BY r.name ASC'''
    params = ['%' + query + '%', '%' + query + '%'] + tag_ids
    results = db.query(sql, params)
    return results if results else None

def search_recipes_filtered_by_tags_paginated(query, tag_ids, page, page_size):
    offset = (page - 1) * page_size
    placeholders = ','.join('?' for _ in tag_ids)
    sql = f'''SELECT DISTINCT r.id,
                             r.name,
                             r.created,
                             r.modified,
                             r.user_id,
                             u.username,
                             (SELECT AVG(rv.rating) FROM reviews rv WHERE rv.recipe_id = r.id) AS average_rating,
                             (SELECT COUNT(rv.id) FROM reviews rv WHERE rv.recipe_id = r.id) AS review_count
              FROM recipes r, users u, recipe_tags rt
              WHERE r.user_id = u.id AND
                    (r.name LIKE ? OR r.content LIKE ?) AND
                    rt.recipe_id = r.id AND
                    rt.tag_id IN ({placeholders})
              ORDER BY r.name ASC
              LIMIT ? OFFSET ?'''
    params = ['%' + query + '%', '%' + query + '%'] + tag_ids + [page_size, offset]
    return db.query(sql, params)

def get_recipe_count_filtered_by_tags(query, tag_ids):
    placeholders = ','.join('?' for _ in tag_ids)
    sql = f'''SELECT COUNT(DISTINCT r.id) AS count
             FROM recipes r, recipe_tags rt
             WHERE (r.name LIKE ? OR r.content LIKE ?) AND
                   rt.recipe_id = r.id AND
                   rt.tag_id IN ({placeholders})'''
    params = ['%' + query + '%', '%' + query + '%'] + tag_ids
    result = db.query(sql, params)
    return result[0]['count'] if result else 0
