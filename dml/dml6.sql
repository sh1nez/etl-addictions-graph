-- Вставка данных из таблицы customers в premium_customers
INSERT INTO premium_customers (customer_id, name, email, discount)
SELECT
    customer_id,
    name,
    LOWER(email) AS email, -- Преобразование email к нижнему регистру
    discount + 5 AS discount -- Увеличение скидки на 5%
FROM customers
WHERE total_purchases > 10000;
