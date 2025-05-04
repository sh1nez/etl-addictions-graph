import networkx as nx
from typing import Optional
from matplotlib import pyplot as plt
from base.storage import GraphStorage
from logger_config import logger


class GraphVisualizer:
    """Class for visualizing SQL dependency graphs."""

    def __init__(self):
        logger.debug("GraphVisualizer initialized")

    def render(self, storage: GraphStorage, title=None, output_path=None):
        """Render the graph using NetworkX and Matplotlib."""
        G = nx.DiGraph()

        # Add all nodes first
        for node in storage.nodes:
            G.add_node(node)

        # Add edges with attributes
        for source, target, attrs in storage.edges:
            G.add_edge(source, target, **attrs)

        # Create the figure and draw
        plt.figure(figsize=(14, 10))

        # Create layout (hierarchical works well for SQL dependency graphs)
        pos = nx.spring_layout(G, k=0.15, iterations=20)

        # Draw nodes
        nx.draw_networkx_nodes(G, pos, node_size=700, node_color="skyblue", alpha=0.8)

        # Draw node labels
        nx.draw_networkx_labels(G, pos, font_size=10)

        # Draw edges with different styles based on attributes
        edge_normal = [
            (u, v)
            for u, v, d in G.edges(data=True)
            if "style" not in d or d["style"] == "solid"
        ]
        edge_dashed = [
            (u, v)
            for u, v, d in G.edges(data=True)
            if "style" in d and d["style"] == "dashed"
        ]
        edge_dotted = [
            (u, v)
            for u, v, d in G.edges(data=True)
            if "style" in d and d["style"] == "dotted"
        ]

        # Normal edges
        nx.draw_networkx_edges(
            G,
            pos,
            edgelist=edge_normal,
            width=1.5,
            alpha=0.7,
            arrows=True,
            arrowstyle="->",
            arrowsize=15,
        )

        # Dashed edges (internal updates)
        nx.draw_networkx_edges(
            G,
            pos,
            edgelist=edge_dashed,
            width=1.5,
            alpha=0.7,
            arrows=True,
            style="dashed",
            arrowstyle="->",
            arrowsize=15,
        )

        # Dotted edges (recursive)
        nx.draw_networkx_edges(
            G,
            pos,
            edgelist=edge_dotted,
            width=1.5,
            alpha=0.7,
            arrows=True,
            style="dotted",
            arrowstyle="->",
            arrowsize=15,
        )

        # Draw edge labels (operations)
        edge_labels = {(u, v): d["operation"] for u, v, d in G.edges(data=True)}
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)

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

