import networkx as nx
from typing import Optional
from matplotlib import pyplot as plt
from base.storage import GraphStorage
from logger_config import logger


class GraphVisualizer:
    def render(self, storage: GraphStorage, title: Optional[str] = None):
        if not storage.nodes:
            logger.warning("Graph is empty, no dependencies to display.")
            return

        logger.debug("Инициализация визуализации графа.")
        G = nx.DiGraph()
        G.add_nodes_from(storage.nodes)
        G.add_edges_from(storage.edges)

        logger.debug(
            f"Добавлено {len(storage.nodes)} узлов и {len(storage.edges)} рёбер."
        )

        plt.figure(figsize=(10, 6))

        try:
            logger.debug("Расчёт позиционирования узлов с помощью spring_layout.")
            pos = nx.spring_layout(G, k=1.2, iterations=100, scale=3, seed=42)

            colors = nx.get_edge_attributes(G, "color").values()
            labels = nx.get_edge_attributes(G, "operation")

            logger.debug("Отрисовка графа.")
            nx.draw(
                G,
                pos,
                with_labels=True,
                node_color="lightblue",
                edge_color=colors,
                font_size=9,
                node_size=2200,
            )
            nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)

            if title:
                plt.title(title)
                logger.debug(f"Заголовок графа: {title}")

            plt.tight_layout()
            plt.show()
            logger.info("Graph rendered successfully.")

        except Exception as e:
            logger.error(f"Error visualizing graph: {e}")
            logger.debug(
                "Check if matplotlib display is supported in your environment."
            )
