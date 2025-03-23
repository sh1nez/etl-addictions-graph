INSERT INTO Employee (first_name, last_name, birth_date, hire_date, position, salary, phone_number, email, address)
SELECT 
    Supplier.name,
    'Supplier',
    '2000-01-01',
    CURRENT_DATE,
    'Supplier Manager',
    4000,
    phone_number, 
    email, 
    Supplier.address
FROM Supplier;


INSERT INTO Employee (first_name, last_name, birth_date, hire_date, position, salary, department, experience_years)
SELECT 
    Supplier.name,
    'Auto',
    '2000-01-01',
    CURRENT_DATE,
    'Procurement Specialist',
    4500,
    'Procurement',
    delivery_time_days / 10
FROM Supplier;


INSERT INTO Employee (first_name, last_name, birth_date, hire_date, position, salary, phone_number, email)
SELECT 
    contact_person,
    'Auto',
    '2000-01-01', 
    CURRENT_DATE,
    'Supplier Contact',
    3800,
    phone_number,
    email
FROM Supplier WHERE contact_person IS NOT NULL;


INSERT INTO Employee (first_name, last_name, birth_date, hire_date, position, salary)
SELECT 
    Supplier.name,
    'Auto',
    '2000-01-01',
    CURRENT_DATE,
    CASE WHEN rating >= 4.5 THEN 'Senior Supplier'
        WHEN rating >= 3 THEN 'Regular Supplier'
        ELSE 'Junior Supplier' END,
    rating * 1000 + 3000
FROM Supplier;


INSERT INTO Employee (first_name, last_name, birth_date, hire_date, position, salary, department)
SELECT 
    CONCAT('Logistics_', delivery_time_days),
    'Auto',
    '2000-01-01',
    CURRENT_DATE,
    'Logistics Manager',
    4200,
    'Logistics'
FROM Supplier;


INSERT INTO Employee (first_name, last_name, birth_date, hire_date, position, salary, supervisor_id)
SELECT 
    Supplier.name,
    'Auto',
    '2000-01-01',
    CURRENT_DATE,
    'Supply Manager',
    4600,
    (SELECT employee_id FROM Employee ORDER BY RANDOM() LIMIT 1)
FROM Supplier;


INSERT INTO Employee (first_name, last_name, birth_date, hire_date, position, salary, department)
SELECT 
    Supplier.name,
    'Auto',
    '2000-01-01',
    CURRENT_DATE,
    'Supply Chain Expert',
    4300,
    CASE WHEN rating >= 4 THEN 'Premium Suppliers'
        ELSE 'Regular Suppliers' END
FROM Supplier;


INSERT INTO Employee (first_name, last_name, birth_date, hire_date, position, salary, phone_number)
SELECT 
    Supplier.name,
    'Auto',
    '2000-01-01',
    CURRENT_DATE,
    'Call Center Representative',
    3700,
    phone_number
FROM Supplier WHERE phone_number IS NOT NULL;


INSERT INTO Employee (first_name, last_name, birth_date, hire_date, position, salary, email, department)
SELECT 
    Supplier.name,
    'Auto',
    '2000-01-01',
    CURRENT_DATE,
    'IT Support',
    3900,
    email,
    'IT'
FROM Supplier WHERE email LIKE '%@%';


INSERT INTO Employee (first_name, last_name, birth_date, hire_date, salary, position, department, experience_years)
SELECT 
    CONCAT('Intl_', Supplier.name), 
    'Auto', 
    '1990-01-01', 
    CURRENT_DATE, 
    6000, 
    'International Supplier Coordinator', 
    'Global Procurement', 
    CASE 
        WHEN address LIKE '%USA%' THEN 5
        WHEN address LIKE '%Canada%' THEN 4
        WHEN address LIKE '%Europe%' THEN 7
        ELSE 3 
    END
FROM Supplier
WHERE address NOT LIKE '%Local%';