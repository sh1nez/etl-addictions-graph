INSERT INTO b (
    animal_uid,
    original_animal_id,
    full_title,
    species_type,
    breed_class,
    age_category,
    weight_class,
    color_code,
    color_intensity,
    birth_year,
    vaccinated_status,
    geo_hash
)
SELECT 
    GEN_RANDOM_UUID()::VARCHAR(36),
    a.animal_id,
    UPPER(SUBSTRING(a.name FROM 1 FOR POSITION(' ' IN a.name))) || ' [' || a.passport_number || ']',
    REPLACE(a.species, ' ', '_'),
    COALESCE(a.breed, 'UNKNOWN_BREED'),
    CASE
        WHEN a.age_months < 12 THEN 'JUVENILE'
        WHEN a.age_months BETWEEN 12 AND 120 THEN 'ADULT'
        ELSE 'SENIOR'
    END,
    (FLOOR(a.weight_grams / 1000) || 'kg_' || 
        CASE 
            WHEN MOD(a.weight_grams, 1000) > 500 THEN 'HEAVY' 
            ELSE 'LIGHT' 
        END)::VARCHAR(20),
    COALESCE(SUBSTRING(a.color_description FROM '#([0-9A-Fa-f]{6})'), '000000'),
    CASE
        WHEN a.color_description ILIKE '%dark%' THEN 'DARK'
        WHEN a.color_description ILIKE '%light%' THEN 'LIGHT'
        ELSE 'MEDIUM'
    END,
    EXTRACT(YEAR FROM a.birth_date),
    a.last_vaccination IS NOT NULL,
    d.latitude::VARCHAR || '|' || d.longitude::VARCHAR
FROM a
JOIN d ON a.address_id = d.address_id
WHERE 
    d.validation_status
    AND a.weight_grams IS NOT NULL
    AND a.color_description IS NOT NULL;