import networkx as nx
from typing import Optional
from matplotlib import pyplot as plt
from base.storage import GraphStorage
from logger_config import logger


class GraphVisualizer:
    """Class for visualizing dependency graphs."""

    def render(self, storage: GraphStorage, title: Optional[str] = None):
        if not storage.nodes:
            logger.warning("Graph is empty, no dependencies to display")
            return

        G = nx.MultiDiGraph()
        G.add_nodes_from(storage.nodes)
        G.add_edges_from(
            (u, v, {"operation": data["operation"], "color": data["color"]})
            for u, v, data in storage.edges
        )

        logger.debug(
            f"Created graph with {len(storage.nodes)} nodes and {len(storage.edges)} edges"
        )

        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(G, k=0.5, iterations=50)

        edge_colors = [data["color"] for _, _, data in G.edges(data=True)]
        edge_labels = {(u, v): data["operation"] for u, v, data in G.edges(data=True)}

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

        nx.draw_networkx_edge_labels(
            G, pos, edge_labels=edge_labels, font_size=9, label_pos=0.75
        )

        if title:
            plt.title(title)

        plt.tight_layout()
        logger.info(f"Rendering graph: {title or 'Untitled'}")
        plt.show()
        logger.debug("Graph displayed successfully")
