CREATE TABLE d (
    address_id INTEGER PRIMARY KEY,
    country_code CHAR(2) NOT NULL,
    country_name VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL,
    district VARCHAR(100),
    street VARCHAR(200) NOT NULL,
    house_number VARCHAR(20) NOT NULL,
    postal_code VARCHAR(20),
    latitude NUMERIC(12,8),
    longitude NUMERIC(12,8),
    validation_status BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);