import re
from typing import List
from ..base.parse import SqlAst


class Procedure:
    def __init__(self, name: str, code: str) -> None:
        self.name = name
        self.code = code

    def get_graph_name(self) -> str:
        return f"\\${self.name}\\$"

    @staticmethod
    def __extract_procedure_code(sql: str) -> str:
        sql = sql.split("BEGIN", 1)[1]
        sql = sql.rsplit("END", 1)[0]
        sql = sql.strip()

        return sql

    @staticmethod
    def extract_procedures(sql_code: str) -> List["Procedure"]:
        found = re.findall(
            r"PROCEDURE\s+[\"\'?]?(\w+)[\"\'?]?\s*\(.*?\)\s*[^$]+?\$\$(.*?)\$\$",
            sql_code,
            re.DOTALL,
        )
        if not found:
            return []

        procedures = []

        for i in found:
            procedures.append(Procedure(i[0], Procedure.__extract_procedure_code(i[1])))

        return procedures

    def __repr__(self) -> str:
        return f"{self.name}: '{self.code}'"


class BufferTable:
    def __init__(self, name) -> None:
        self.name = name
        self.write_procedures = set()  # procedures that write into the table
        self.read_procedures = set()  # procedures that read from the table

    @staticmethod
    def find_buffer_tables(
        procedures: List[Procedure], known_buff_tables: List["BufferTable"]
    ) -> List["BufferTable"]:
        buff_tables = dict()
        for table in known_buff_tables:
            buff_tables[table.name] = table

        for proc in procedures:
            ast = SqlAst(proc.code)

            for to_table, from_tables in ast.get_dependencies().items():
                if to_table not in buff_tables:
                    buff_tables[to_table] = BufferTable(to_table)

                for from_table in from_tables:
                    if from_table not in buff_tables:
                        buff_tables[from_table] = BufferTable(from_table)

                    buff_tables[to_table].write_procedures.add(proc)
                    buff_tables[from_table].read_procedures.add(proc)

        real_buff_tables = []
        for _, table in buff_tables.items():
            if len(table.write_procedures) > 0 and len(table.read_procedures) > 0:
                real_buff_tables.append(table)

        return real_buff_tables

    def __repr__(self) -> str:
        return f"{self.name}:\nreaders: {(self.read_procedures)}\nwriters: {self.write_procedures}"
