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
    FOREIGN KEY(recipe_id) REFERENCES recipes(id) ON DELETE CASCADE,
    FOREIGN KEY(user_id) REFERENCES users(id),
    UNIQUE(recipe_id, user_id)
);

CREATE TABLE tags (
    id            INTEGER PRIMARY KEY,
    name          TEXT NOT NULL UNIQUE
);

CREATE TABLE recipe_tags (
    recipe_id     INTEGER,
    tag_id        INTEGER,
    FOREIGN KEY(recipe_id) REFERENCES recipes(id) ON DELETE CASCADE,
    FOREIGN KEY(tag_id) REFERENCES tags(id) ON DELETE CASCADE,
    UNIQUE(recipe_id, tag_id)
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

CREATE INDEX idx_recipe_name ON recipes(name);
CREATE INDEX idx_tag_name ON tags(name);
CREATE INDEX idx_recipe_tags_tag_id ON recipe_tags(tag_id);
CREATE INDEX idx_recipe_tags_recipe_id ON recipe_tags(recipe_id);
CREATE INDEX idx_reviews_recipe_id ON reviews(recipe_id);
CREATE INDEX idx_reviews_user_id ON reviews(user_id);
CREATE INDEX idx_recipes_user_id ON recipes(user_id);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_recipes_created ON recipes(created);
CREATE INDEX idx_reviews_created ON reviews(created);
CREATE INDEX idx_tags_name ON tags(name);
CREATE INDEX idx_recipe_tags_recipe_tag ON recipe_tags(recipe_id, tag_id);
CREATE INDEX idx_reviews_recipe_user ON reviews(recipe_id, user_id);