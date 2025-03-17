-- Удаление старых данных
DELETE FROM b 
WHERE processing_time < CURRENT_TIMESTAMP - INTERVAL '1 YEAR';

-- Обновление данных
UPDATE b
SET weight_class = 
    SPLIT_PART(weight_class, '_', 1) || '_EXTRA_HEAVY'
WHERE CAST(SPLIT_PART(weight_class, '_', 1) AS INTEGER) > 50;

-- Вставка в таблицу c
INSERT INTO c (
    animal_uid,
    full_identity,
    species_type,
    breed_class,
    age_category,
    weight_class,
    color_info,
    birth_decade,
    vaccination_status,
    full_address,
    geo_hash,
    country_code,
    processing_date
)
SELECT
    b.animal_uid,
    b.full_title || ' (' || d.country_code || '-' || d.postal_code || ')',
    b.species_type,
    b.breed_class,
    b.age_category,
    b.weight_class,
    b.color_code || '_' || b.color_intensity,
    FLOOR(b.birth_year / 10) * 10 || 's',
    CASE b.vaccinated_status WHEN TRUE THEN 'YES' ELSE 'NO' END,
    d.country_name || ', ' || d.city || ', ул. ' || d.street || ' ' || d.house_number || 
        COALESCE(', ' || d.district, ''),
    b.geo_hash,
    d.country_code,
    CURRENT_DATE
FROM b
JOIN d ON CAST(SPLIT_PART(b.geo_hash, '|', 1) AS NUMERIC) = d.latitude
   AND CAST(SPLIT_PART(b.geo_hash, '|', 2) AS NUMERIC) = d.longitude;