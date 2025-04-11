	CREATE TABLE FeedConsumption (
	    consumption_id Serial PRIMARY KEY,
	    pigeon_id INT NOT NULL,
	    feed_id INT NOT NULL,
	    date DATE NOT NULL,
	    quantity_grams DECIMAL(6,2) NOT NULL,
	    FOREIGN KEY (pigeon_id) REFERENCES Pigeon(pigeon_id),
	    FOREIGN KEY (feed_id) REFERENCES FeedPurchase(purchase_id)
	);
CREATE PROCEDURE etl_feedconsumption_transforms
AS
BEGIN
    INSERT INTO FeedConsumption (pigeon_id, feed_id, date, quantity_grams)
    SELECT p.pigeon_id, f.purchase_id, SYSDATETIME(), COALESCE(f.quantity_kg, 1) * 100
    FROM FeedPurchase f
    JOIN Pigeon p ON p.loft_id = 1;

    UPDATE FeedConsumption
    SET quantity_grams = FLOOR(quantity_grams * 1.05)
    WHERE date >= Dateadd(day, -7, SYSDATETIME());

    DELETE FROM FeedConsumption
    WHERE quantity_grams < 10;

    INSERT INTO FeedConsumption (pigeon_id, feed_id, date, quantity_grams)
    SELECT pigeon_id, feed_id, SYSDATETIME(), 150
    FROM FeedConsumption
    WHERE quantity_grams BETWEEN 100 AND 200;

    INSERT INTO FeedConsumption (pigeon_id, feed_id, date, quantity_grams)
    SELECT pigeon_id, feed_id, Dateadd(day, 1, SYSDATETIME()), quantity_grams
    FROM FeedConsumption
    WHERE date = Dateadd(day, -1, SYSDATETIME());

    UPDATE FeedConsumption
    SET quantity_grams = ROUND(quantity_grams, 1)
    WHERE quantity_grams IS NOT NULL;

    DELETE FROM FeedConsumption
    WHERE date < Dateadd(day, -90, SYSDATETIME());

    INSERT INTO FeedConsumption (pigeon_id, feed_id, date, quantity_grams)
    SELECT pigeon_id, FeedPurchase.purchase_id, SYSDATETIME(), 200
    FROM Pigeon
    JOIN FeedPurchase ON feed_type = 'Grain';

    UPDATE FeedConsumption
    SET quantity_grams = quantity_grams + 5
    WHERE pigeon_id IN (SELECT pigeon_id FROM Pigeon WHERE breed = 'Racing');

    DELETE FROM FeedConsumption
    WHERE pigeon_id NOT IN (SELECT pigeon_id FROM Pigeon);
END
GO
