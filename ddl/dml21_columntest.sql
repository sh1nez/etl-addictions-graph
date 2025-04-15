-- UPDATE demo_table
-- SET AGE=30 ,CITY='MOSCOW'
-- WHERE CITY='MOSKVA';

-- SELECT * from demo_table2;

-- INSERT INTO demo_table3 SELECT a, b, c from source_demo_table;

-- INSERT INTO demo_table4 SELECT * from source_demo_table;

-- DELETE FROM demo_table5;

-- DELETE FROM demot_table6
-- WHERE purchase_date < CURRENT_DATE - DATEADD(day, -25, CURRENT_DATE);

-- DELETE FROM demot_table6
-- WHERE cost = (SELECT MIN(cost) FROM demot_table6);

-- MERGE INTO demo_table7
-- USING demo_table8
-- ON demo_table8.id = demo_table7.id
-- WHEN MATCHED THEN
--     UPDATE SET demo_table7.name = demo_table8.name
-- WHEN NOT MATCHED THEN
--     INSERT (id, name) VALUES (demo_table8.id, demo_table8.name);
