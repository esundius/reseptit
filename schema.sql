CREATE TABLE users (
    id            INTEGER PRIMARY KEY,
    username      TEXT CHECK (username != '') NOT NULL UNIQUE,
    password_hash TEXT CHECK (password_hash != '') NOT NULL,
    created       TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE recipes (
    id            INTEGER PRIMARY KEY,
    name          TEXT NOT NULL,
    content       TEXT,
    image         BLOB,
    image_type    TEXT,
    user_id       INTEGER,
    created       TEXT DEFAULT CURRENT_TIMESTAMP,
    modified      TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TRIGGER update_modified
AFTER UPDATE ON recipes
FOR EACH ROW
BEGIN
    UPDATE recipes SET modified = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;