-- Таблица результатов
CREATE TABLE c (
    record_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    animal_uid VARCHAR(36) NOT NULL REFERENCES b(animal_uid),
    full_identity VARCHAR(500) NOT NULL,
    species_type VARCHAR(50) NOT NULL,
    breed_class VARCHAR(100) NOT NULL,
    age_category VARCHAR(20) NOT NULL,
    weight_class VARCHAR(20) NOT NULL,
    color_info VARCHAR(100) NOT NULL,
    birth_decade VARCHAR(6) NOT NULL,
    vaccination_status VARCHAR(3) NOT NULL,
    full_address VARCHAR(700) NOT NULL,
    geo_hash VARCHAR(20) NOT NULL,
    country_code CHAR(2) NOT NULL,
    processing_date DATE NOT NULL
);