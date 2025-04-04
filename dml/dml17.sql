-- Вставка отсутствующих категорий из списка
INSERT INTO categories (category_id, category_name)
SELECT
    l.id,
    l.name
FROM list_of_categories l
LEFT JOIN categories c ON l.id = c.category_id
WHERE c.category_id IS NULL;
