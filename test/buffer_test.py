__all__ = []

import pytest

from src.base.storage import BuffWrite, Edge
from src.func.buff_tables import (
    Procedure,
    BufferTable,
)


@pytest.mark.usefixtures("writer_proc", "reader_proc")
class TestBuffer:
    @pytest.fixture
    def writer_proc(self):
        return Procedure("writer", "INSERT INTO buffer_table SELECT * FROM source;")

    @pytest.fixture
    def reader_proc(self):
        return Procedure("reader", "SELECT * FROM buffer_table;")

    def test_graph_name(self, writer_proc):
        assert writer_proc.get_graph_name() == r"\$writer\$"

    def test_proc_repr(self, reader_proc):
        assert "reader" in repr(reader_proc)

    def test_procedure_extraction(self):
        sql_code = """
        CREATE PROCEDURE sample_proc()
        LANGUAGE SQL
        AS $$
        BEGIN
            INSERT INTO buffer_table SELECT * FROM source;
        END;
        $$;
        """
        procs = Procedure.extract_procedures(sql_code)
        assert len(procs) == 1
        assert procs[0].name == "sample_proc"
        assert "INSERT INTO buffer_table" in procs[0].code

    def test_buffer_table_identification(self, writer_proc, reader_proc):
        procedures = [writer_proc, reader_proc]
        buff_tables, _ = BufferTable.find_buffer_tables(procedures, [])
        names = {t.name for t in buff_tables}
        assert "buffer_table" in names

    def test_dependency_edges(self, writer_proc, reader_proc):
        procedures = [writer_proc, reader_proc]
        buff_tables, _ = BufferTable.find_buffer_tables(procedures, [])
        deps = BufferTable.build_dependencies(buff_tables, [])

        buffer_name = "buffer_table"
        writer_name = writer_proc.get_graph_name()
        reader_name = reader_proc.get_graph_name()

        write_edges = deps.get(buffer_name, set())
        read_edges = deps.get(reader_name, set())

        has_write = any(
            edge.source == writer_name and edge.target == buffer_name
            for edge in write_edges
        )
        has_read = any(
            edge.source == buffer_name and edge.target == reader_name
            for edge in read_edges
        )
        assert has_write
        assert has_read

    def test_procedure_repr(self, writer_proc):
        text = repr(writer_proc)
        assert "writer" in text
        assert "INSERT INTO buffer_table" in text

    def test_edge_repr_normal(self):
        edge = Edge("A", "B", BuffWrite())
        assert repr(edge) == "Edge(A -> B, BuffWrite, normal)"

    def test_buffer_table_repr(self, writer_proc, reader_proc):
        procedures = [writer_proc, reader_proc]
        buff_tables, _ = BufferTable.find_buffer_tables(procedures, [])
        for table in buff_tables:
            text = repr(table)
            assert table.name in text
            for proc in table.read_procedures.union(table.write_procedures):
                assert proc.name in text
