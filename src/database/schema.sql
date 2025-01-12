-- schema.sql

CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    crypto VARCHAR(100) NOT NULL,
    threshold FLOAT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS predictions (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    crypto VARCHAR(100) NOT NULL,
    prediction_date DATE NOT NULL,
    predicted_price DECIMAL(18, 8) NOT NULL,
    actual_price DECIMAL(18, 8) DEFAULT NULL,
    accuracy DECIMAL(5, 4) DEFAULT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS trades (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    position_size BIGINT NOT NULL,
    leverage BIGINT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);