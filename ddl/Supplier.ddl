CREATE TABLE Supplier (
    supplier_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    contact_person VARCHAR(100),
    phone_number VARCHAR(20),
    email VARCHAR(100),
    address TEXT,
    rating DECIMAL(3,2),
    delivery_time_days INT
);

INSERT INTO Supplier (name, contact_person, phone_number, email, address, rating, delivery_time_days)
VALUES ('AgroFeed Ltd.', 'John Doe', '+1234567890', 'contact@agrofeed.com', '123 Farm Lane, Springfield', 4.5, 7);

INSERT INTO Supplier (name, contact_person, phone_number, email, address, rating, delivery_time_days)
VALUES ('GreenGrain Co.', 'Jane Smith', '+0987654321', 'info@greengrain.com', '456 Rural Road, Shelbyville', 4.2, 5);

INSERT INTO Supplier (name, contact_person, phone_number, email, rating, delivery_time_days)
VALUES ('FarmDirect', 'Emily Johnson', '+1122334455', 'sales@farmdirect.com', 4.8, 6);

INSERT INTO Supplier (name, contact_person, phone_number, email, address, rating, delivery_time_days)
VALUES ('Harvest Supply', 'Michael Brown', '+2233445566', 'support@harvestsupply.com', '101 Harvest Ave, Ogdenville', 3.9, 8);

INSERT INTO Supplier (name, contact_person, email, address, rating, delivery_time_days)
VALUES ('Golden Harvest', 'Sarah Connor', 'contact@goldenharvest.com', '222 Gold St, Metropolis', 4.6, 6);

INSERT INTO Supplier (name, contact_person, phone_number, email, address, rating, delivery_time_days)
VALUES ('Fresh Farm Supplies', 'Tom Hardy', '+4455667788', 'sales@freshfarm.com', '333 Greenway, Smalltown', 4.1, 5);

INSERT INTO Supplier (name, contact_person, phone_number, email, address, rating, delivery_time_days)
VALUES ('EcoGrain', 'Alice Walker', '+5566778899', 'info@ecograin.com', '777 Organic St, Greentown', 4.9, 4);

INSERT INTO Supplier (name, contact_person, phone_number, email, address, rating, delivery_time_days)
VALUES ('AgriWorld', 'Robert King', '+6677889900', 'support@agriworld.com', '888 Farmland, Rivertown', 4.3, 7);

INSERT INTO Supplier (name, contact_person, phone_number, email, address, rating, delivery_time_days)
VALUES ('Nature Feed Co.', 'Emma Stone', '+7788990011', 'sales@naturefeed.com', '999 Nature Ln, Woodland', 4.7, 6);

INSERT INTO Supplier (name, contact_person, phone_number, address, rating, delivery_time_days)
VALUES ('ProHarvest', 'Chris Evans', '+8899001122', '111 Harvest Rd, Hilltop', 4.0, 8);

UPDATE Supplier
SET rating = rating + 0.2
WHERE rating < 4.5;

UPDATE Supplier
SET contact_person = CONCAT(contact_person, ' (Verified)')
WHERE email IN (SELECT email FROM Supplier WHERE POSITION('@farm' IN email) > 0);

UPDATE Supplier
SET phone_number = '+1111111111'
WHERE supplier_id IN (SELECT supplier_id FROM Supplier WHERE POSITION('Harvest' IN name) > 0);

UPDATE Supplier
SET delivery_time_days = delivery_time_days - 1
WHERE delivery_time_days > (SELECT AVG(delivery_time_days) FROM Supplier);

UPDATE Supplier
SET email = CONCAT('support+', supplier_id, '@supplier.com')
FROM Supplier s
JOIN (SELECT supplier_id FROM Supplier WHERE email IS NOT NULL) sub ON s.supplier_id = sub.supplier_id;

UPDATE Supplier
SET rating = rating + 0.1
WHERE supplier_id IN (SELECT supplier_id FROM Supplier WHERE delivery_time_days < 6);

UPDATE Supplier
SET address = CONCAT(address, ', Updated')
WHERE supplier_id IN (SELECT supplier_id FROM Supplier WHERE rating > 4.5);

UPDATE Supplier
SET phone_number = '+2222222222'
WHERE supplier_id IN (SELECT supplier_id FROM Supplier WHERE LENGTH(phone_number) < 12);

UPDATE Supplier
SET delivery_time_days = delivery_time_days + 2
WHERE supplier_id IN (SELECT supplier_id FROM Supplier WHERE rating < 4.2);

DELETE FROM Supplier
WHERE rating < 4.0;

DELETE FROM Supplier
WHERE supplier_id IN (SELECT supplier_id FROM Supplier WHERE delivery_time_days > 10);

DELETE FROM Supplier
WHERE supplier_id IN (SELECT supplier_id FROM Supplier WHERE POSITION('Ltd' IN name) > 0);

DELETE FROM Supplier
WHERE email IS NULL;
