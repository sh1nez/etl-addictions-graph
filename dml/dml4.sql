-- Создаем таблицу заказов
CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    customer_id INT,
    status VARCHAR(20),
    amount DECIMAL(10, 2)
);

-- Вставляем несколько заказов
INSERT INTO orders (order_id, customer_id, status, amount)
VALUES
    (101, 1, 'В обработке', 1500.00),
    (102, 2, 'В обработке', 2000.00),
    (103, 3, 'Доставлен', 3000.00);

-- Обновляем статус всех заказов на сумму больше 2000 до "Выполнен"
UPDATE orders
SET status = 'Выполнен'
WHERE amount > 2000;
