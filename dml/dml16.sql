-- Обновление цен на товары
UPDATE products
SET price = price * 1.05
WHERE category_id IN (SELECT category_id FROM categories WHERE name = 'Electronics');
