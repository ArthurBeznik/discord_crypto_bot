-- schema.sql

CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    crypto VARCHAR(100) NOT NULL,
    threshold FLOAT NOT NULL
);
