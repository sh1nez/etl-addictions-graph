CREATE OR REPLACE PROCEDURE "insert_into_buff2" (p_name TEXT, p_value INTEGER)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO buff2 (name, value) VALUES (p_name, p_value);
END;
$$;

CREATE OR REPLACE PROCEDURE "insert_into_buf" (p_name TEXT, p_value INTEGER)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO buff (name, value) VALUES (p_name, p_value);
END;
$$;

CREATE OR REPLACE PROCEDURE select_from_buffs()
LANGUAGE plpgsql
AS $$
BEGIN
    select * from buff;
    select * from buff2;
END;
$$;
