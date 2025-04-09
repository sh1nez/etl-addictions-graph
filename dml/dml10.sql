INSERT INTO monthly_sales (month, total_sales)
SELECT
    DATE_TRUNC('month', order_date) AS month,
    SUM(amount) AS total_sales
FROM orders
WHERE status = 'Выполнен'
GROUP BY DATE_TRUNC('month', order_date);
