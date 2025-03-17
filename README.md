# Utility for parsing DDL and generating an ETL ~~dependencies~~ addictions graph.

* ./src - source code
* ./ddl - sql code (pg/mysql/oracle dialects)
* ./test - unit test via pytest


# Install
```python
python -m venv venv
source venv/bin/activate
pip install -r ./requirements.txt
```



# Using uv package manager
uv init
uv add -r requirements.txt 
uv run src/main.py



# sqllineage [github](https://github.com/reata/sqllineage)  [demo](https://reata.github.io/sqllineage/)
source .venv/bin/activate
sqllineage -g -f path_to_sql_file