--=============================================================
--             Init quotes DB schema (from scratch)
--           => Do not erase objects if already exists
--=============================================================
-------------------------------
-- Create schema quotes_schema:
-------------------------------
CREATE SCHEMA IF NOT EXISTS quotes_schema;

-----------------
-- Create tables:
-----------------
-- authors table:
CREATE TABLE IF NOT EXISTS quotes_schema.authors (
    author_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    born_date DATE,
    born_location VARCHAR(255),
    url VARCHAR(255) NOT NULL UNIQUE,
    bio TEXT
);
-- quotes table:
CREATE TABLE IF NOT EXISTS quotes_schema.quotes (
    quote_id SERIAL PRIMARY KEY,
    text TEXT,
    author_id INT NOT NULL,
    CONSTRAINT fk_quote_author FOREIGN KEY (author_id) REFERENCES quotes_schema.authors(author_id)
);
-- tags table:
CREATE TABLE IF NOT EXISTS quotes_schema.tags (
    tag_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);
-- quotes_tags table:
CREATE TABLE IF NOT EXISTS quotes_schema.quotes_tags (
    quote_id INT NOT NULL,
    tag_id INT NOT NULL,
    PRIMARY KEY (quote_id, tag_id),
    CONSTRAINT fk_contain_quote FOREIGN KEY (quote_id) REFERENCES quotes_schema.quotes(quote_id),
    CONSTRAINT fk_contain_tag FOREIGN KEY (tag_id) REFERENCES quotes_schema.tags(tag_id)
);