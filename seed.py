import random
import sqlite3

db = sqlite3.connect('database.db')
db.execute('DELETE FROM users')
db.execute('DELETE FROM recipes')

user_count = 5000
recipe_count = 10**5
tag_count = 100

for i in range(1, user_count + 1):
    username = f'user{i}'
    password_hash = f'hash{i}'
    db.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, password_hash))

for i in range(1, tag_count + 1):
    tag_name = f'Tag{i}'
    db.execute('INSERT INTO tags (name) VALUES (?)', (tag_name,))

for i in range(1, recipe_count + 1):
    name = f'Recipe {i}'
    content = f'''This is the content of recipe {i}.
    It has multiple lines. Enjoy cooking!
    Ingredients:
    - Ingredient 1
    - Ingredient 2
    Instructions:
    1. Step one
    2. Step two
    3. Step three
    '''
    user_id = random.randint(1, user_count)
    db.execute('INSERT INTO recipes (name, content, user_id) VALUES (?, ?, ?)', (name, content, user_id))

    # Randomly assign tags to the recipe
    assigned_tags = random.sample(range(1, tag_count + 1), k=random.randint(0, 5))
    for tag_id in assigned_tags:
        db.execute('INSERT INTO recipe_tags (recipe_id, tag_id) VALUES (?, ?)', (i, tag_id))

    # Randomly create reviews for the recipe
    for j in range (1, user_count + 1):
        if random.random() < 0.1:  # 10% chance of review
            rating = random.randint(1, 5)
            comment = f'This is a review by user {j} for recipe {name}.'
            db.execute('INSERT INTO reviews (recipe_id, user_id, rating, comment) VALUES (?, ?, ?, ?)', (i, j, rating, comment))

db.commit()
db.close()
print(f'Seeded database with {user_count} users and {recipe_count} recipes, including reviews.')
