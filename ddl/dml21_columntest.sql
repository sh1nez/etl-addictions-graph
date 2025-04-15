UPDATE demo_table
SET AGE=30 ,CITY='MOSCOW'
WHERE CITY='MOSKVA';

SELECT * from demo_table2;

INSERT INTO demo_table3 SELECT a, b, c from source_table;

INSERT INTO demo_table4 SELECT * from source_table;

DELETE FROM demo_table5;

DELETE FROM FeedPurchase
WHERE purchase_date < CURRENT_DATE - DATEADD(day, -25, CURRENT_DATE);

DELETE FROM FeedPurchase
WHERE cost = (SELECT MIN(cost) FROM FeedPurchase);

MERGE INTO target_table
USING source_table
ON source_table.id = target_table.id
WHEN MATCHED THEN
    UPDATE SET target_table.name = source_table.name
WHEN NOT MATCHED THEN
    INSERT (id, name) VALUES (source_table.id, source_table.name);