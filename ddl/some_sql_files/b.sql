-- Таблица трансформированных данных
CREATE TABLE b (
    animal_uid VARCHAR(36) PRIMARY KEY,
    original_animal_id INTEGER NOT NULL,
    full_title VARCHAR(300) NOT NULL,
    species_type VARCHAR(50) NOT NULL,
    breed_class VARCHAR(100) NOT NULL,
    age_category VARCHAR(20) NOT NULL,
    weight_class VARCHAR(20) NOT NULL,
    color_code CHAR(6) NOT NULL,
    color_intensity VARCHAR(10),
    birth_year INTEGER NOT NULL,
    vaccinated_status BOOLEAN NOT NULL,
    geo_hash VARCHAR(20) NOT NULL,
    processing_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);