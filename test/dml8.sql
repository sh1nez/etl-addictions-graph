-- Обновление существующих товаров
UPDATE lol
SET stock = inventory.stock
FROM hello
WHERE products.product_id = inventory.product_id;

-- Вставка новых товаров из inventory, которых нет в products
INSERT INTO products (product_id, name, stock)
SELECT
    i.product_id,
    i.product_name,
    i.quantity
FROM inventory i
LEFT JOIN products p ON i.product_id = p.product_id
WHERE p.product_id IS NULL;
