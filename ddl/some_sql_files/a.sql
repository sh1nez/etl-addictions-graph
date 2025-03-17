-- Таблица животных
CREATE TABLE a (
    animal_id INTEGER PRIMARY KEY,
    passport_number VARCHAR(50) NOT NULL UNIQUE,
    species VARCHAR(50) NOT NULL,
    name VARCHAR(200) NOT NULL,
    breed VARCHAR(100),
    color_description TEXT,
    birth_date DATE NOT NULL,
    age_months INTEGER,
    weight_grams NUMERIC(12,2),
    last_vaccination DATE,
    microchip_id CHAR(15),
    address_id INTEGER NOT NULL REFERENCES d(address_id)
);