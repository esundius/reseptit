import random
import sqlite3

db = sqlite3.connect('database.db')
db.execute('DELETE FROM users')
db.execute('DELETE FROM recipes')

user_count = 1000
recipe_count = 10**5

for i in range(1, user_count + 1):
    username = f'user{i}'
    password_hash = f'hash{i}'
    db.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, password_hash))

for i in range(1, recipe_count + 1):
    name = f'Recipe {i}'
    content = f'This is the content of recipe {i}.'
    user_id = random.randint(1, user_count)
    db.execute('INSERT INTO recipes (name, content, user_id) VALUES (?, ?, ?)', (name, content, user_id))

db.commit()
db.close()
print(f'Seeded database with {user_count} users and {recipe_count} recipes.')
