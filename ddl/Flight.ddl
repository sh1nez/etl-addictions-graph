	CREATE TABLE Flight (
	    flight_id SERIAL PRIMARY KEY,
	    pigeon_id INT NOT NULL,
	    date TIMESTAMP NOT NULL,
	    distance_km DECIMAL(6,2) NOT NULL,
	    duration_minutes INT NOT NULL,
	    altitude_meters INT,
	    FOREIGN KEY (pigeon_id) REFERENCES Pigeon(pigeon_id)
	);
CREATE PROCEDURE etl_flight_transforms
AS
BEGIN
	INSERT INTO Flight (pigeon_id, distance_km, duration_minutes, altitude_meters)
    SELECT pigeon_id, 5.5, 30, 150
    FROM Pigeon;

    UPDATE Flight
    SET altitude_meters = altitude_meters + 50
    WHERE altitude_meters IS NOT NULL;

    DELETE FROM Flight
    WHERE duration_minutes < 5;

    INSERT INTO Flight (pigeon_id, distance_km, duration_minutes, altitude_meters)
    SELECT pigeon_id, CEILING(distance_km), ROUND(duration_minutes + 5, -2), altitude_meters
    FROM Flight;

    UPDATE Flight
    SET distance_km = ROUND(distance_km, 2)
    WHERE distance_km IS NOT NULL;

    INSERT INTO Flight (pigeon_id, distance_km, duration_minutes, altitude_meters)
    SELECT pigeon_id, 10, 40, 300
    FROM Pigeon
    WHERE flying_speed > 40;

    DELETE FROM Flight
    WHERE date < DATEADD(day, 30, CURRENT_TIMESTAMP);

    INSERT INTO Flight (pigeon_id, distance_km, duration_minutes, altitude_meters)
    SELECT pigeon_id, 15, 60, 400
    FROM Pigeon
    WHERE breed = 'High Flyer';

    UPDATE Flight
    SET duration_minutes = SQRT(duration_minutes) + 10
    WHERE pigeon_id IN (SELECT pigeon_id FROM VetCheck WHERE cast(health_status as varchar(50)) = 'Excellent');

    DELETE FROM Flight
    WHERE altitude_meters IS NULL;
END
GO
