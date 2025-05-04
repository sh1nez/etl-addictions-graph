CREATE OR REPLACE PROCEDURE Merge_CTE_Window_RECURSIVE()
LANGUAGE SQL
AS $$
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

SELECT purchase_id, supplier_id, cost,
       RANK() OVER (PARTITION BY feed_type ORDER BY cost DESC) AS cost_rank
FROM FeedPurchase;
SELECT flight_id, pigeon_id, distance_km,
       AVG(distance_km) OVER (PARTITION BY pigeon_id) AS avg_distance
FROM Flight;
$$;

CREATE OR REPLACE PROCEDURE MergeLatestFeedPurchase()
LANGUAGE SQL
AS $$
    WITH LatestPurchases AS (
        SELECT supplier_id, MAX(purchase_date) AS latest_date
        FROM FeedPurchase
        GROUP BY supplier_id
    )
    MERGE INTO FeedPurchase AS target
    USING (
        SELECT s.supplier_id, CURRENT_DATE AS purchase_date, 100.00 AS quantity_kg,
               500.00 AS cost, 'Corn' AS feed_type
        FROM Supplier s
        JOIN LatestPurchases lp ON s.supplier_id = lp.supplier_id
    ) AS src
    ON target.supplier_id = src.supplier_id AND target.purchase_date = src.purchase_date
    WHEN MATCHED THEN
        UPDATE SET cost = src.cost
    WHEN NOT MATCHED THEN
        INSERT (supplier_id, purchase_date, quantity_kg, cost, feed_type)
        VALUES (src.supplier_id, src.purchase_date, src.quantity_kg, src.cost, src.feed_type);
$$;

CREATE OR REPLACE PROCEDURE MergeRecentFlightUpdates()
LANGUAGE SQL
AS $$
    MERGE INTO Flight AS target
    USING (
        SELECT *,
               RANK() OVER (PARTITION BY pigeon_id ORDER BY date DESC) AS rnk
        FROM Flight
    ) AS src
    ON target.flight_id = src.flight_id AND src.rnk = 1
    WHEN MATCHED THEN
        UPDATE SET altitude_meters = COALESCE(src.altitude_meters, 100)
    WHEN NOT MATCHED THEN
        INSERT (pigeon_id, date, distance_km, duration_minutes, altitude_meters)
        VALUES (src.pigeon_id, src.date, src.distance_km, src.duration_minutes, src.altitude_meters);
$$;

-- CTE + оконная функция для Employee
CREATE OR REPLACE PROCEDURE BoostTopEmployees()
LANGUAGE SQL
AS $$
    WITH RankedEmployees AS (
        SELECT *, DENSE_RANK() OVER (PARTITION BY department ORDER BY salary DESC) AS dept_rank
        FROM Employee
    )
    UPDATE Employee
    SET salary = r.salary * 1.1
    FROM RankedEmployees r
    WHERE Employee.employee_id = r.employee_id AND dept_rank = 1;
$$;

CREATE OR REPLACE PROCEDURE AnalyzeLoftManagerHierarchy()
LANGUAGE SQL
AS $$
    WITH RECURSIVE ManagerHierarchy AS (
        SELECT manager_id, 1 AS level
        FROM LoftManager
        WHERE end_date IS NULL
        UNION ALL
        SELECT lm.manager_id, mh.level + 1
        FROM LoftManager lm
        JOIN ManagerHierarchy mh ON lm.manager_id = mh.manager_id
    )
    SELECT manager_id,
           COUNT(*) OVER (PARTITION BY level) AS level_count
    FROM ManagerHierarchy;
$$;
