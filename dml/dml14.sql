-- Добавление новых заказов из внешнего источника
INSERT INTO orders (order_id, customer_id, order_total, order_date)
SELECT 
    o.id,
    o.client_id,
    o.total_amount,
    o.date_placed
FROM external_orders o
LEFT JOIN orders ol ON o.id = ol.order_id
WHERE ol.order_id IS NULL;