CREATE TABLE FeedPurchase (
    purchase_id SERIAL PRIMARY KEY,
    supplier_id INT NOT NULL,
    purchase_date DATE NOT NULL,
    quantity_kg DECIMAL(6,2) NOT NULL,
    cost DECIMAL(10,2) NOT NULL,
    feed_type VARCHAR(50),
    FOREIGN KEY (supplier_id) REFERENCES Supplier(supplier_id)
);

CREATE OR REPLACE PROCEDURE insert_feedpurchase(
    p_supplier_id INT,
    p_purchase_date DATE,
    p_quantity_kg DECIMAL(6,2),
    p_cost DECIMAL(10,2),
    p_feed_type VARCHAR(50)
)
LANGUAGE SQL
AS $$
    INSERT INTO FeedPurchase (supplier_id, purchase_date, quantity_kg, cost, feed_type)
    VALUES (p_supplier_id, p_purchase_date, p_quantity_kg, p_cost, p_feed_type);
$$;

CREATE OR REPLACE PROCEDURE update_cost_increase()
LANGUAGE SQL
AS $$
    UPDATE FeedPurchase
    SET cost = cost * 1.1
    WHERE purchase_date < CURRENT_DATE - INTERVAL '15 day';
$$;

CREATE OR REPLACE PROCEDURE update_feed_type_premium()
LANGUAGE SQL
AS $$
    UPDATE FeedPurchase
    SET feed_type = CONCAT('Premium ', feed_type)
    FROM Supplier
    WHERE FeedPurchase.supplier_id = Supplier.supplier_id
      AND Supplier.supplier_id % 2 = 0;
$$;

CREATE OR REPLACE PROCEDURE update_quantity_by_avg()
LANGUAGE SQL
AS $$
    UPDATE FeedPurchase
    SET quantity_kg = quantity_kg + (
        SELECT AVG(quantity_kg) FROM FeedPurchase
    )
    WHERE quantity_kg < (
        SELECT AVG(quantity_kg) FROM FeedPurchase
    );
$$;

CREATE OR REPLACE PROCEDURE update_cost_wheat()
LANGUAGE SQL
AS $$
    UPDATE FeedPurchase
    SET cost = cost * 1.05
    WHERE feed_type = 'Wheat';
$$;

CREATE OR REPLACE PROCEDURE shift_purchase_date()
LANGUAGE SQL
AS $$
    UPDATE FeedPurchase
    SET purchase_date = purchase_date - INTERVAL '1 day'
    WHERE purchase_date > CURRENT_DATE - INTERVAL '5 day';
$$;

CREATE OR REPLACE PROCEDURE increase_large_quantity()
LANGUAGE SQL
AS $$
    UPDATE FeedPurchase
    SET quantity_kg = quantity_kg + 20
    WHERE quantity_kg > 250;
$$;

CREATE OR REPLACE PROCEDURE delete_old_feedpurchase()
LANGUAGE SQL
AS $$
    DELETE FROM FeedPurchase
    WHERE purchase_date < CURRENT_DATE - INTERVAL '25 day';
$$;

CREATE OR REPLACE PROCEDURE delete_min_cost()
LANGUAGE SQL
AS $$
    DELETE FROM FeedPurchase
    WHERE cost = (SELECT MIN(cost) FROM FeedPurchase);
$$;
