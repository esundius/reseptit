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

CREATE TABLE reviews (
    id            INTEGER PRIMARY KEY,
    recipe_id     INTEGER,
    user_id       INTEGER,
    rating        INTEGER CHECK (rating >= 1 AND rating <= 5),
    comment       TEXT,
    created       TEXT DEFAULT CURRENT_TIMESTAMP,
    modified      TEXT,
    FOREIGN KEY(recipe_id) REFERENCES recipes(id),
    FOREIGN KEY(user_id) REFERENCES users(id),
    UNIQUE(recipe_id, user_id)
);

CREATE TRIGGER update_modified
AFTER UPDATE ON recipes
FOR EACH ROW
BEGIN
    UPDATE recipes SET modified = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;

CREATE TRIGGER update_review_modified
AFTER UPDATE ON reviews
FOR EACH ROW
BEGIN
    UPDATE reviews SET modified = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;