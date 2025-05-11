--MERGE
MERGE INTO FeedPurchase AS target
USING (SELECT 1 AS supplier_id, '2025-04-01'::date AS purchase_date) AS source
ON (target.supplier_id = source.supplier_id AND target.purchase_date = source.purchase_date)
WHEN MATCHED THEN
    UPDATE SET quantity_kg = quantity_kg + 50
WHEN NOT MATCHED THEN
    INSERT (supplier_id, purchase_date, quantity_kg, cost, feed_type)
    VALUES (source.supplier_id, source.purchase_date, 50, 300, 'Mixed');
MERGE INTO Employee AS target
USING (SELECT 'Alice' AS first_name, 'Brown' AS last_name) AS source
ON (target.first_name = source.first_name AND target.last_name = source.last_name)
WHEN MATCHED THEN
    UPDATE SET salary = salary + 5000
WHEN NOT MATCHED THEN
    INSERT (first_name, last_name, birth_date, hire_date, position, salary, department, experience_years)
    VALUES (source.first_name, source.last_name, CURRENT_DATE, CURRENT_DATE, 'Consultant', 70000, 'IT', 5);

--CTE (WITH)
WITH RecentFlights AS (
    SELECT * FROM Flight WHERE date > CURRENT_DATE - INTERVAL '30 days'
)
SELECT pigeon_id, distance_km, duration_minutes
FROM RecentFlights
WHERE duration_minutes > 20;
WITH ConsumptionPerPigeon AS (
    SELECT pigeon_id, SUM(quantity_grams) AS total_grams
    FROM FeedConsumption
    GROUP BY pigeon_id
)
SELECT * FROM ConsumptionPerPigeon WHERE total_grams > 500;

--����������� CTE
WITH RECURSIVE EmployeeHierarchy AS (
    SELECT employee_id, first_name, last_name, supervisor_id, 1 AS level
    FROM Employee WHERE supervisor_id IS NULL
    UNION ALL
    SELECT e.employee_id, e.first_name, e.last_name, e.supervisor_id, eh.level + 1
    FROM Employee e
    JOIN EmployeeHierarchy eh ON e.supervisor_id = eh.employee_id
)
SELECT * FROM EmployeeHierarchy;
WITH RECURSIVE ManagerChain AS (
    SELECT manager_id, loft_id, start_date, end_date, 1 AS depth
    FROM LoftManager WHERE end_date IS NULL
    UNION ALL
    SELECT lm.manager_id, lm.loft_id, lm.start_date, lm.end_date, mc.depth + 1
    FROM LoftManager lm
    JOIN ManagerChain mc ON lm.loft_id = mc.loft_id
    WHERE lm.start_date > mc.start_date
)
SELECT * FROM ManagerChain;

--������� �������
SELECT purchase_id, supplier_id, cost,
       RANK() OVER (PARTITION BY feed_type ORDER BY cost DESC) AS cost_rank
FROM FeedPurchase;
SELECT flight_id, pigeon_id, distance_km,
       AVG(distance_km) OVER (PARTITION BY pigeon_id) AS avg_distance
FROM Flight;
