import networkx as nx
from typing import Optional
from matplotlib import pyplot as plt
from base.storage import GraphStorage
from logger_config import logger


class GraphVisualizer:
    """Class for visualizing SQL dependency graphs."""

    def __init__(self):
        logger.debug("GraphVisualizer initialized")

    def render(
        self, storage: GraphStorage, title: Optional[str] = None, output_path=None
    ):
        """Render the graph using NetworkX and Matplotlib."""
        if not storage.nodes:
            logger.warning("Graph is empty, no dependencies to display")
            return
        G = nx.MultiDiGraph()
        G.add_nodes_from(storage.nodes)
        G.add_edges_from(storage.edges)

        plt.figure(figsize=(14, 10))
        try:
            pos = nx.spring_layout(G, k=0.15, iterations=50)

            # debug multi digraph
            # logger.debug({(u, v, k): d for u, v, k, d in G.edges(keys=True,data=True)})

            # debug self-loops
            # self_loops = {
            #     (u, v, k): d
            #     for (u, v, k), d in G.edges(keys=True,data=True)
            #     if u == v
            # }
            # logger.debug(self_loops)

            # Получаем цвета рёбер
            edge_colors = [
                data["color"] for u, v, k, data in G.edges(keys=True, data=True)
            ]

            # Получаем стиль рёбер, иначе solid по умолчанию
            edge_style = [
                data.get("style", "solid")
                for u, v, k, data in G.edges(keys=True, data=True)
            ]

            # насколько одна связь отдаляется от другой
            step = 0.2
            # максимальное количество отображаемых связей между двумя нодами
            multi_edge_lim = 10
            connectionstyle = [
                f"arc3,rad={(-1)**(i+1)*((i+1)//2*step)}" for i in range(multi_edge_lim)
            ]

            # Отрисовка графа
            nx.draw(
                G,
                pos,
                with_labels=True,
                node_color="lightblue",
                edge_color=edge_colors,
                font_size=10,
                node_size=2000,
                arrows=True,
                arrowstyle="->",
                arrowsize=15,
                connectionstyle=connectionstyle,
                style=edge_style,
            )

            # Draw edge labels (operations)
            edge_labels = {
                (u, v, k): d["operation"]
                for u, v, k, d in G.edges(keys=True, data=True)
            }
            nx.draw_networkx_edge_labels(
                G,
                pos,
                edge_labels=edge_labels,
                font_size=8,
                connectionstyle=connectionstyle,
            )

            # Set title
            plt.title(title or "SQL Dependency Graph")
            plt.axis("off")

            # Save or show
            if output_path:
                plt.savefig(output_path, format="png", dpi=300, bbox_inches="tight")
                logger.info(f"Graph saved to {output_path}")
            else:
                plt.tight_layout()
                plt.show()

            plt.close()
            logger.debug("Graph rendering completed")
        except Exception as e:
            logger.error(
                f"Error visualizing graph: {e}\nYou may need to run this in an environment that supports matplotlib display."
            )
