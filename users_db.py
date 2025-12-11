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
                    r.created
             FROM recipes r
             WHERE r.user_id = ?
             ORDER BY r.name ASC'''
    return db.query(sql, (user_id,))
