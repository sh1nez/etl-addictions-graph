UPDATE orders
SET status = 'Отменен'
WHERE order_id IN (
    SELECT order_id
    FROM orders
    WHERE status = 'В обработке'
    AND created_at < NOW() - INTERVAL '3 days'
);