CREATE TABLE FeedConsumption (
    consumption_id Serial PRIMARY KEY,
    pigeon_id INT NOT NULL,
    feed_id INT NOT NULL,
    date DATE NOT NULL,
    quantity_grams DECIMAL(6,2) NOT NULL,
    FOREIGN KEY (pigeon_id) REFERENCES Pigeon(pigeon_id),
    FOREIGN KEY (feed_id) REFERENCES FeedPurchase(purchase_id)
);
CREATE OR REPLACE PROCEDURE update_FeedConsumption(
    p_days INT,
    p_multiplier DECIMAL
)
LANGUAGE SQL
AS $$
    UPDATE FeedConsumption
    SET quantity_grams = FLOOR(quantity_grams * p_multiplier)
    WHERE date >= CURRENT_DATE - p_days;
$$;

CREATE OR REPLACE PROCEDURE delete_FeedConsumption(
    p_min_quantity DECIMAL
)
LANGUAGE SQL
AS $$
    DELETE FROM FeedConsumption
    WHERE quantity_grams < p_min_quantity;
$$;

CREATE OR REPLACE PROCEDURE insert_FeedConsumption(
    p_min DECIMAL,
    p_max DECIMAL,
    p_quantity DECIMAL
)
LANGUAGE SQL
AS $$
    INSERT INTO FeedConsumption (pigeon_id, feed_id, date, quantity_grams)
    SELECT pigeon_id, feed_id, CURRENT_DATE, p_quantity
    FROM FeedConsumption
    WHERE quantity_grams BETWEEN p_min AND p_max;
$$;
