-- Обновление адресов для клиентов
UPDATE customers
SET address = a.new_address
FROM address_updates a
WHERE customers.customer_id = a.customer_id AND a.update_date >= NOW() - INTERVAL '1 month';
