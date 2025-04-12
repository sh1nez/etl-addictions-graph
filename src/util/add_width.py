from src.util.request_counter import get_analiz
from src.base.storage import GraphStorage
from collections import defaultdict


def width_to_storage(file_path: str = "./ddl/Pigeon_etl.sql"):
    edge_widths = get_analiz(file_path)

    storage = GraphStorage()
    storage.set_edge_widths(edge_widths)

    # Добавьте зависимости в storage
    dependencies = defaultdict(list)
    # Заполните dependencies данными
    storage.add_dependencies(dependencies)


if __name__ == "__main__":
    width_to_storage()
