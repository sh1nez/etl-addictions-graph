UPDATE employees
SET salary = 
    CASE 
        WHEN department = 'IT' THEN salary * 1.15
        WHEN department = 'HR' THEN salary * 1.10
        ELSE salary * 1.05
    END;