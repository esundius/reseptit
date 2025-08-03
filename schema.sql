CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT CHECK (username != '') NOT NULL UNIQUE,
    password_hash TEXT CHECK (password_hash != '') NOT NULL,
    created TEXT DEFAULT CURRENT_TIMESTAMP
)