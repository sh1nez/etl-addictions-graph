CREATE TABLE FeedPurchase (
    purchase_id SERIAL PRIMARY KEY,
    supplier_id INT NOT NULL,
    purchase_date DATE NOT NULL,
    quantity_kg DECIMAL(6,2) NOT NULL,
    cost DECIMAL(10,2) NOT NULL,
    feed_type VARCHAR(50),
    FOREIGN KEY (supplier_id) REFERENCES Supplier(supplier_id)
);
CREATE PROCEDURE etl_feedpurchase_transforms
AS
BEGIN
INSERT INTO FeedPurchase (supplier_id, purchase_date, quantity_kg, cost, feed_type)
VALUES (1, '2025-03-01', 120.50, 500.00, 'Corn');

INSERT INTO FeedPurchase (supplier_id, purchase_date, quantity_kg, cost, feed_type)
VALUES (2, '2025-03-02', 200.75, 750.00, 'Soybean');

INSERT INTO FeedPurchase (supplier_id, purchase_date, quantity_kg, cost, feed_type)
VALUES (3, '2025-03-03', 300.25, 1200.00, 'Wheat');

INSERT INTO FeedPurchase (supplier_id, purchase_date, quantity_kg, cost, feed_type)
VALUES (4, '2025-03-04', 150.00, 650.00, 'Barley');

INSERT INTO FeedPurchase (supplier_id, purchase_date, quantity_kg, cost, feed_type)
VALUES (5, '2025-03-05', 180.60, 900.00, 'Corn');

INSERT INTO FeedPurchase (supplier_id, purchase_date, quantity_kg, cost, feed_type)
VALUES (6, '2025-03-06', 250.30, 1100.00, 'Soybean');

INSERT INTO FeedPurchase (supplier_id, purchase_date, quantity_kg, cost, feed_type)
VALUES (7, '2025-03-07', 310.45, 1300.00, 'Wheat');

INSERT INTO FeedPurchase (supplier_id, purchase_date, quantity_kg, cost, feed_type)
VALUES (8, '2025-03-08', 190.90, 800.00, 'Barley');

INSERT INTO FeedPurchase (supplier_id, purchase_date, quantity_kg, cost, feed_type)
VALUES (9, '2025-03-09', 270.20, 1150.00, 'Corn');

INSERT INTO FeedPurchase (supplier_id, purchase_date, quantity_kg, cost, feed_type)
VALUES (10, '2025-03-10', 220.40, 980.00, 'Soybean');

INSERT INTO FeedPurchase (supplier_id, purchase_date, quantity_kg, cost, feed_type)
VALUES (11, '2025-03-11', 300.60, 1250.00, 'Wheat');

INSERT INTO FeedPurchase (supplier_id, purchase_date, quantity_kg, cost, feed_type)
VALUES (12, '2025-03-12', 160.80, 720.00, 'Barley');

INSERT INTO FeedPurchase (supplier_id, purchase_date, quantity_kg, cost, feed_type)
VALUES (13, '2025-03-13', 280.90, 1120.00, 'Corn');

INSERT INTO FeedPurchase (supplier_id, purchase_date, quantity_kg, cost, feed_type)
VALUES (14, '2025-03-14', 230.70, 970.00, 'Soybean');

INSERT INTO FeedPurchase (supplier_id, purchase_date, quantity_kg, cost, feed_type)
VALUES (15, '2025-03-15', 320.50, 1350.00, 'Wheat');

INSERT INTO FeedPurchase (supplier_id, purchase_date, quantity_kg, cost, feed_type)
VALUES (16, '2025-03-16', 175.30, 790.00, 'Barley');

INSERT INTO FeedPurchase (supplier_id, purchase_date, quantity_kg, cost, feed_type)
VALUES (17, '2025-03-17', 290.40, 1180.00, 'Corn');

INSERT INTO FeedPurchase (supplier_id, purchase_date, quantity_kg, cost, feed_type)
VALUES (18, '2025-03-18', 210.60, 940.00, 'Soybean');

INSERT INTO FeedPurchase (supplier_id, purchase_date, quantity_kg, cost, feed_type)
VALUES (19, '2025-03-19', 340.75, 1400.00, 'Wheat');

UPDATE FeedPurchase
SET cost = cost * 1.1
WHERE purchase_date < CURRENT_DATE - DATEADD(day, -15, CURRENT_DATE);

UPDATE FeedPurchase
SET feed_type = CONCAT('Premium ', feed_type)
FROM FeedPurchase
JOIN Supplier ON FeedPurchase.supplier_id = Supplier.supplier_id
WHERE Supplier.supplier_id % 2 = 0;

UPDATE FeedPurchase
SET quantity_kg = quantity_kg + (SELECT AVG(quantity_kg) FROM FeedPurchase)
WHERE quantity_kg < (SELECT AVG(quantity_kg) FROM FeedPurchase);

UPDATE FeedPurchase
SET cost = cost * 1.05
WHERE feed_type = 'Wheat';

UPDATE FeedPurchase
SET purchase_date = purchase_date - DATEADD(day, -1, purchase_date)
WHERE purchase_date > CURRENT_DATE - DATEADD(day, -5, CURRENT_DATE);

UPDATE FeedPurchase
SET quantity_kg = quantity_kg + 20
WHERE quantity_kg > 250;

DELETE FROM FeedPurchase
WHERE purchase_date < CURRENT_DATE - DATEADD(day, -25, CURRENT_DATE);

DELETE FROM FeedPurchase
WHERE cost = (SELECT MIN(cost) FROM FeedPurchase);
END
GO
