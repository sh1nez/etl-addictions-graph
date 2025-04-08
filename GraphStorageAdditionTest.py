def test_process_sql_insert_into_select_from_table():
    storage = GraphStorage()
    sql = "INSERT INTO orders SELECT * FROM temp_orders;"
    process_sql(sql, storage)
    assert storage.get_dependencies("orders") == {"temp_orders"}

def test_process_sql_update_from_table():
    storage = GraphStorage()
    sql = "UPDATE users SET name = 'test' FROM logs WHERE users.id = logs.user_id;"
    process_sql(sql, storage)
    assert storage.get_dependencies("users") == {"logs"}

def test_process_sql_select_into():
    storage = GraphStorage()
    sql = "SELECT * INTO backup FROM active_users;"
    process_sql(sql, storage)
    assert storage.get_dependencies("backup") == {"active_users"}

def test_process_sql_select_without_target():
    storage = GraphStorage()
    sql = "SELECT * FROM products;"
    process_sql(sql, storage)
    assert storage.get_dependencies("result") == {"products"}

def test_process_sql_nested_query():
    storage = GraphStorage()
    sql = "SELECT * FROM (SELECT id FROM employees);"
    process_sql(sql, storage)
    assert storage.get_dependencies("result") == {"employees"}

def test_sql_ast_select_into():
    sql = "SELECT * INTO backup FROM active_users;"
    ast = SQLAST(sql)
    assert ast.target_tables == ["backup"]
    assert ast.source_tables == {"active_users"}

def test_sql_ast_simple_select():
    sql = "SELECT * FROM products;"
    ast = SQLAST(sql)
    assert ast.target_tables == ["result"] 
    assert ast.source_tables == {"products"}

def test_sql_ast_nested_subquery():
    sql = "SELECT * FROM (SELECT id FROM employees);"
    ast = SQLAST(sql)
    assert ast.source_tables == {"employees"}
