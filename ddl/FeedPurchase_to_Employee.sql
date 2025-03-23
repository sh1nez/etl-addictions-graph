INSERT INTO Employee (first_name, last_name, birth_date, hire_date, salary, position)
SELECT
       CONCAT('Supplier', supplier_id),
       'Auto', 
       '2000-01-01',
       purchase_date,
       cost / 10,
       'Supplier Manager'
FROM FeedPurchase;


INSERT INTO Employee (first_name, last_name, birth_date, hire_date, salary, position)
SELECT
       CONCAT('Buyer', purchase_id),
       'Auto',
       '2000-01-01',
       purchase_date,
       3000,
       CASE WHEN quantity_kg > 1000 THEN 'Bulk Buyer' 
            WHEN cost > 5000 THEN 'Senior Buyer' 
            ELSE 'Regular Buyer' END
FROM FeedPurchase;


INSERT INTO Employee (first_name, last_name, birth_date, hire_date, salary, position, department, experience_years)
SELECT
       CONCAT('Staff', purchase_id),
       'Auto',
       '2000-01-01',
       purchase_date,
       3500,
       'Supply Worker',
       'Supply Chain',
       quantity_kg / 500
FROM FeedPurchase;


INSERT INTO Employee (first_name, last_name, birth_date, hire_date, salary, experience_years, position)
SELECT
       CONCAT('DateBased', purchase_id),
       'Auto',
       '2000-01-01',
       purchase_date,
       3200, 
       EXTRACT(YEAR FROM purchase_date) - 2000, 
       CASE WHEN EXTRACT(YEAR FROM purchase_date) < 2015 THEN 'Senior Staff' ELSE 'Junior Staff' END
FROM FeedPurchase;


INSERT INTO Employee (first_name, last_name, birth_date, hire_date, salary, position, email, phone_number)
SELECT
       CONCAT('Contact', supplier_id),
       'Auto',
       '2000-01-01',
       CURRENT_DATE,
       3300,
       'Contact Manager',
       CONCAT('supplier', supplier_id, '@company.com'),
       CONCAT('+7-555-', SUBSTRING(supplier_id FROM LENGTH(supplier_id) - 3 FOR 4))
FROM FeedPurchase;


INSERT INTO Employee (first_name, last_name, birth_date, hire_date, salary, position, supervisor_id)
SELECT
       CONCAT('ManagerLinked', supplier_id),
       'Auto',
       '2000-01-01',
       CURRENT_DATE,
       3400,
       'Staff Member',
       (SELECT employee_id FROM Employee ORDER BY RANDOM() LIMIT 1)
FROM FeedPurchase;


INSERT INTO Employee (first_name, last_name, birth_date, hire_date, salary, position)
SELECT
       CONCAT('Feed', purchase_id),
       'Auto',
       '2000-01-01',
       CURRENT_DATE,
       3600,
       CASE WHEN feed_type = 'Grain' THEN 'Grain Specialist'
            WHEN feed_type = 'Hay' THEN 'Hay Manager'
            ELSE 'General Supplier' END
FROM FeedPurchase;


INSERT INTO Employee (first_name, last_name, birth_date, hire_date, salary, position)
SELECT
       CONCAT('SalaryBased', purchase_id),
       'Auto',
       '2000-01-01',
       CURRENT_DATE,
       GREATEST(cost / 100 * 1.5, 3000),
       'Financial Analyst'
FROM FeedPurchase;


INSERT INTO Employee (first_name, last_name, birth_date, hire_date, salary, position, department)
SELECT
       CONCAT('DateGroup', EXTRACT(YEAR FROM purchase_date), EXTRACT(MONTH FROM purchase_date)),
       'Auto',
       '2000-01-01',
       MIN(purchase_date), 
       3100,
       'Procurement Officer',
       'Monthly Procurement'
FROM FeedPurchase
GROUP BY EXTRACT(YEAR FROM purchase_date), EXTRACT(MONTH FROM purchase_date);


INSERT INTO Employee (first_name, last_name, birth_date, hire_date, salary, position, experience_years, supervisor_id)
SELECT
       CONCAT('SupplierRep', supplier_id),
       'Auto',
       '2000-01-01',
       CURRENT_DATE,
       3700,
       'Supplier Representative',
       SUM(quantity_kg) / 1000,
       (SELECT employee_id FROM Employee ORDER BY cost DESC LIMIT 1)
FROM FeedPurchase
GROUP BY supplier_id;