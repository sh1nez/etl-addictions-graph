-- Вставка новых клиентов из внешней базы
INSERT INTO customers (customer_id, name, email)
SELECT
    e.external_id,
    e.customer_name,
    e.email_address
FROM external_customers e
LEFT JOIN customers c ON e.external_id = c.customer_id
WHERE c.customer_id IS NULL;
