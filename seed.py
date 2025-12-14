import random
import sqlite3

db = sqlite3.connect('database.db')
db.execute('DELETE FROM users')
db.execute('DELETE FROM recipes')

USER_COUNT = 5000
RECIPE_COUNT = 10**5
TAG_COUNT = 100

for i in range(1, USER_COUNT + 1):
    USERNAME = f'user{i}'
    PASSWORD_HASH = f'hash{i}'
    sql = 'INSERT INTO users (username, password_hash) VALUES (?, ?)'
    db.execute(sql, (USERNAME, PASSWORD_HASH))

for i in range(1, TAG_COUNT + 1):
    TAG_NAME = f'Tag{i}'
    db.execute('INSERT INTO tags (name) VALUES (?)', (TAG_NAME,))

for i in range(1, RECIPE_COUNT + 1):
    NAME = f'Recipe {i}'
    CONTENT = f'''This is the content of recipe {i}.
    It has multiple lines. Enjoy cooking!
    Ingredients:
    - Ingredient 1
    - Ingredient 2
    Instructions:
    1. Step one
    2. Step two
    3. Step three
    '''
    user_id = random.randint(1, USER_COUNT)
    sql = 'INSERT INTO recipes (name, content, user_id) VALUES (?, ?, ?)'
    db.execute(sql, (NAME, CONTENT, user_id))

    # Randomly assign tags to the recipe
    assigned_tags = random.sample(range(1, TAG_COUNT + 1), k=random.randint(0, 5))
    for tag_id in assigned_tags:
        db.execute('INSERT INTO recipe_tags (recipe_id, tag_id) VALUES (?, ?)', (i, tag_id))

    # Randomly create reviews for the recipe
    for j in range (1, USER_COUNT + 1):
        if random.random() < 0.1:  # 10% chance of review
            rating = random.randint(1, 5)
            COMMENT = f'This is a review by user {j} for recipe {NAME}.'
            sql = 'INSERT INTO reviews (recipe_id, user_id, rating, comment) VALUES (?, ?, ?, ?)'
            db.execute(sql, (i, j, rating, COMMENT))

db.commit()
db.close()
print(f'Seeded database with {USER_COUNT} users and {RECIPE_COUNT} recipes, including reviews.')
