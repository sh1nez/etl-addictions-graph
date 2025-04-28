import networkx as nx
from typing import Optional
from matplotlib import pyplot as plt
from base.storage import GraphStorage
from logger_config import logger  # Добавлен импорт логгера


class GraphVisualizer:
    """Class for visualizing dependency graphs."""

    def render(self, storage: GraphStorage, title: Optional[str] = None):
        try:
            if not storage.nodes:
                logger.warning(
                    "Graph is empty, no dependencies to display"
                )  # Замена print на logger.warning
                return

            G = nx.MultiDiGraph()
            G.add_nodes_from(storage.nodes)
            G.add_edges_from(
                (u, v, {"operation": data["operation"], "color": data["color"]})
                for u, v, data in storage.edges
            )

            logger.debug(
                f"Created graph with {len(storage.nodes)} nodes and {len(storage.edges)} edges"
            )  # Детальное логирование

            plt.figure(figsize=(12, 8))
            pos = nx.spring_layout(G, k=0.5, iterations=50)

            # Подготовка данных для отрисовки
            edge_colors = [data["color"] for _, _, data in G.edges(data=True)]
            edge_labels = {
                (u, v): data["operation"] for u, v, data in G.edges(data=True)
            }

            # Отрисовка основных элементов
            nx.draw(
                G,
                pos,
                with_labels=True,
                node_color="lightblue",
                edge_color=edge_colors,
                font_size=10,
                node_size=2000,
                arrows=True,
                arrowsize=15,
                connectionstyle="arc3,rad=0.1",
            )

            # Добавление подписей к ребрам
            nx.draw_networkx_edge_labels(
                G, pos, edge_labels=edge_labels, font_size=9, label_pos=0.75
            )

            if title:
                plt.title(title)

            plt.tight_layout()
            logger.info(f"Rendering graph: {title or 'Untitled'}")  # Логирование этапа
            plt.show()
            logger.debug("Graph displayed successfully")  # Подтверждение успеха

        except Exception as e:
            logger.error(
                f"Visualization error: {e}", exc_info=True
            )  # Детальный лог ошибки
            logger.warning(
                "You may need to run this in an environment that supports matplotlib display."
            )
