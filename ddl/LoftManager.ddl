CREATE TABLE LoftManager (
    loft_id INT NOT NULL,
    manager_id INT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    role_description TEXT,
    PRIMARY KEY (loft_id, manager_id),
    FOREIGN KEY (loft_id) REFERENCES PigeonLoft(loft_id),
    FOREIGN KEY (manager_id) REFERENCES Manager(manager_id)
);
CREATE PROCEDURE etl_loftmanager_transforms
AS
BEGIN
	INSERT INTO LoftManager (loft_id, manager_id, start_date, end_date, role_description)
    SELECT l.loft_id, m.manager_id, SYSDATETIME(), NULL, 'Assigned'
    FROM PigeonLoft l
    JOIN Manager m ON l.manager_id = m.manager_id;

    UPDATE LoftManager
    SET role_description = 'Primary Manager'
    WHERE role_description IS NULL;

	UPDATE LoftManager
    SET end_date = SYSDATETIME()
    WHERE start_date < DATEADD(day, 365, SYSDATETIME());

    DELETE FROM LoftManager
    WHERE end_date IS NOT NULL AND end_date < DATEADD(day, 180, SYSDATETIME());

    INSERT INTO LoftManager (loft_id, manager_id, start_date, end_date, role_description)
    SELECT l.loft_id, m.manager_id, SYSDATETIME(), NULL, 'New Assignment'
    FROM PigeonLoft l
    JOIN Manager m ON m.department = 'Logistics'
    WHERE l.manager_id IS NULL;

	update LoftManager
	set role_description = CAST('Backup' as text)
    WHERE CAST(role_description as varchar) = 'New Assignment';

    DELETE FROM LoftManager
    WHERE manager_id NOT IN (SELECT manager_id FROM Manager);

    UPDATE LoftManager
    SET role_description = UPPER(CAST(role_description as varchar));

    DELETE FROM LoftManager
    WHERE CAST(role_description as varchar) = 'Temporary';
END
GO
