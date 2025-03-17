CREATE TABLE FeedPurchase (
    purchase_id SERIAL PRIMARY KEY,
    supplier_id INT NOT NULL,
    purchase_date DATE NOT NULL,
    quantity_kg DECIMAL(6,2) NOT NULL,
    cost DECIMAL(10,2) NOT NULL,
    feed_type VARCHAR(50),
    FOREIGN KEY (supplier_id) REFERENCES Supplier(supplier_id)
);