import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from typing import Optional
from base.storage import GraphStorage
from base.visualize import GraphVisualizer
from logger_config import logger


class ColumnVisualizer(GraphVisualizer):
    """Class for visualizing dependency graphs in column mode."""

    def render(
        self,
        storage: GraphStorage,
        title: Optional[str] = None,
        save_path: Optional[str] = None,
        figsize: tuple = (20, 16),
        seed: Optional[int] = 42,
        central_spread: float = 2.0,
        peripheral_spread: float = 1.5,
        transform_spread: float = 7,  # Новый параметр для transform_only
        transform_node_color: str = "lightcoral",  # Новый параметр для цвета узлов
        mode: Optional[str] = "full",
    ):
        if not storage.nodes:
            logger.warning("Graph is empty, no dependencies to display")
            return

        G_full = nx.MultiDiGraph()
        G_full.add_nodes_from(storage.nodes)
        G_full.add_edges_from(
            (
                u,
                v,
                {
                    "operation": data.get("operation", "UNKNOWN"),
                    "color": data.get("color", "black"),
                    "style": data.get("style", "solid"),
                    "columns": data.get("columns", None),
                },
            )
            for u, v, data in storage.edges
        )
        logger.debug(
            f"Created full graph with {len(G_full.nodes())} nodes and {len(G_full.edges())} edges"
        )

        central_nodes = [
            n
            for n in G_full.nodes()
            if G_full.in_degree(n) > 0 and G_full.out_degree(n) > 0
        ]
        peripheral_nodes = [n for n in G_full.nodes() if n not in central_nodes]
        logger.debug(
            f"Central nodes: {len(central_nodes)}, Peripheral nodes: {len(peripheral_nodes)}"
        )

        if mode == "transform_only":
            if not central_nodes:
                logger.warning("No central nodes found for transform_only mode")
                return
            G = G_full.subgraph(central_nodes).copy()
            logger.debug(
                f"Created subgraph with {len(G.nodes())} nodes for transform_only mode"
            )
        elif mode == "full":
            G = G_full
        else:
            logger.error(
                f"Unknown visualization mode: {mode}. Supported modes: 'full', 'transform_only'"
            )
            return

        if mode == "full":
            if not central_nodes:
                logger.warning("No central nodes found, using all nodes as central")
                central_nodes = list(G.nodes())
                peripheral_nodes = []
            if not peripheral_nodes:
                logger.warning("No peripheral nodes found, using spring layout")
                if seed is not None:
                    np.random.seed(seed)
                pos = nx.spring_layout(G, k=0.2, iterations=150, seed=seed)
            else:
                if seed is not None:
                    np.random.seed(seed)
                pos = nx.shell_layout(G, nlist=[central_nodes, peripheral_nodes])

                if len(central_nodes) > 1:
                    central_subgraph = G.subgraph(central_nodes)
                    central_pos = nx.spring_layout(
                        central_subgraph,
                        k=central_spread / np.sqrt(len(central_nodes)),
                        iterations=50,
                        seed=seed,
                    )
                    for node in central_nodes:
                        pos[node] = central_pos[node]

                for node in peripheral_nodes:
                    x, y = pos[node]
                    norm = np.sqrt(x**2 + y**2)
                    if norm > 0:
                        pos[node] = (x * peripheral_spread, y * peripheral_spread)
        else:  # mode == "transform_only"
            # Настройка расположения для transform_only
            if seed is not None:
                np.random.seed(seed)
            pos = nx.spring_layout(G, k=transform_spread, iterations=150, seed=seed)

        node_sizes = [1200 if n in central_nodes else 800 for n in G.nodes()]
        node_colors = [
            transform_node_color if mode == "transform_only" else "lightblue"
            for n in G.nodes()
        ]
        edge_colors = [data["color"] for u, v, k, data in G.edges(keys=True, data=True)]
        edge_styles = [data["style"] for u, v, k, data in G.edges(keys=True, data=True)]
        edge_labels = {
            (u, v, k): data["operation"]
            for u, v, k, data in G.edges(keys=True, data=True)
        }

        plt.figure(figsize=figsize)
        fig = plt.gcf()
        ax = plt.gca()

        try:
            step = 0.1
            multi_edge_lim = 10
            connectionstyle = [
                f"arc3,rad={(-1)**(i+1)*((i+1)//2*step)}" for i in range(multi_edge_lim)
            ]

            nx.draw(
                G,
                pos,
                with_labels=True,
                node_color=node_colors,
                edge_color=edge_colors,
                style=edge_styles,
                node_size=node_sizes,
                font_size=8,
                arrows=True,
                arrowsize=15,
                connectionstyle=connectionstyle,
            )
            label_list = nx.draw_networkx_edge_labels(
                G,
                pos,
                edge_labels=edge_labels,
                font_size=7,
                connectionstyle=connectionstyle,
            )
            for txt in label_list.values():
                txt.set_picker(5)

            last_ann = None

            def on_pick(event):
                nonlocal last_ann
                label = event.artist
                if last_ann is not None:
                    last_ann.remove()
                    last_ann = None
                u, v, k = next(key for key, val in label_list.items() if val is label)
                attrs = G.edges[u, v, k]
                columns_parsed = attrs.get("columns", None)
                info = ""
                if columns_parsed is not None:
                    if columns_parsed[0] is not None and len(columns_parsed[0]) > 0:
                        info = "Columns "
                        if ":" in columns_parsed[0][0]:
                            info += "to:from\n  "
                        else:
                            info += "to\n  "
                        info += "\n  ".join(columns_parsed[0])
                    if columns_parsed[1] is not None and len(columns_parsed[1]) > 0:
                        info += "\nWhere columns\n  "
                        info += "\n  ".join(columns_parsed[1])
                x, y = label.get_position()
                last_ann = ax.annotate(
                    info,
                    xy=(x, y),
                    xycoords="data",
                    xytext=(20, 20),
                    textcoords="offset points",
                    bbox=dict(boxstyle="round,pad=0.3", alpha=0.8),
                    arrowprops=dict(arrowstyle="->"),
                )
                fig.canvas.draw_idle()

            fig.canvas.mpl_connect("pick_event", on_pick)

            if save_path:
                plt.savefig(save_path, format="png", dpi=300, bbox_inches="tight")
                logger.info(f"Graph saved to {save_path}")
            else:
                plt.tight_layout()
                plt.show()

            plt.close()
            logger.debug("Graph rendering completed")
        except Exception as e:
            logger.error(
                f"Error visualizing graph: {e}\nYou may need to run this in an environment that supports matplotlib display."
            )
