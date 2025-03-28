-- Создаем таблицу товаров
CREATE TABLE products (
    product_id INT PRIMARY KEY,
    name VARCHAR(100),
    stock INT,
    price DECIMAL(10, 2)
);

-- Вставляем товары
INSERT INTO products (product_id, name, stock, price)
VALUES
    (1, 'Телефон', 10, 25000.00),
    (2, 'Ноутбук', 5, 50000.00),
    (3, 'Наушники', 50, 5000.00);

-- Повышаем цену на 5% для товаров, у которых stock < 10
UPDATE products
SET price = price * 1.05
WHERE stock < 10;