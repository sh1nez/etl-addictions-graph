CREATE TABLE FeedConsumption (
    consumption_id SERIAL PRIMARY KEY,
    pigeon_id INT NOT NULL,
    feed_id INT NOT NULL,
    date DATE NOT NULL,
    quantity_grams DECIMAL(6,2) NOT NULL,
    FOREIGN KEY (pigeon_id) REFERENCES Pigeon(pigeon_id),
    FOREIGN KEY (feed_id) REFERENCES FeedPurchase(purchase_id)
);