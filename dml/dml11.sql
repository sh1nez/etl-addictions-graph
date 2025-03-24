-- Обновление статуса клиентов
UPDATE customers
SET status = 'Недействующий'
WHERE last_purchase < NOW() - INTERVAL '1 year';