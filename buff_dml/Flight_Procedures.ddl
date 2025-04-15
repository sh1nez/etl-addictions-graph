CREATE TABLE Flight (
    flight_id SERIAL PRIMARY KEY,
    pigeon_id INT NOT NULL,
    date TIMESTAMP NOT NULL,
    distance_km DECIMAL(6,2) NOT NULL,
    duration_minutes INT NOT NULL,
    altitude_meters INT,
    FOREIGN KEY (pigeon_id) REFERENCES Pigeon(pigeon_id)
);

CREATE OR REPLACE PROCEDURE update_Flight(
    p_increment INT
)
LANGUAGE SQL
AS $$
    UPDATE Flight
    SET altitude_meters = altitude_meters + p_increment
    WHERE altitude_meters IS NOT NULL;
$$;

CREATE OR REPLACE PROCEDURE insert_Flight(
    p_min_speed DECIMAL,
    p_distance DECIMAL,
    p_duration INT,
    p_altitude INT
)
LANGUAGE SQL
AS $$
    INSERT INTO Flight (pigeon_id, distance_km, duration_minutes, altitude_meters)
    SELECT pigeon_id, p_distance, p_duration, p_altitude
    FROM Pigeon
    WHERE flying_speed > p_min_speed;
$$;

CREATE OR REPLACE PROCEDURE delete_Flight(
    p_days INT
)
LANGUAGE SQL
AS $$
    DELETE FROM Flight
    WHERE date < CURRENT_TIMESTAMP - INTERVAL '1 day' * p_days;
$$;

CREATE OR REPLACE PROCEDURE update_select_Flight(
  p_health_status TEXT
)
LANGUAGE SQL
AS $$
    UPDATE Flight
    SET duration_minutes = duration_minutes + 10
    WHERE pigeon_id IN (
        SELECT pigeon_id
        FROM VetCheck
        WHERE health_status = p_health_status
    );
$$;
