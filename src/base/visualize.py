import networkx as nx
from typing import Optional
from matplotlib import pyplot as plt
from parse import GraphStorage


class GraphVisualizer:
    """Class for visualizing dependency graphs."""

    def render(self, storage: GraphStorage, title: Optional[str] = None):
        if not storage.nodes:
            print("Graph is empty, no dependencies to display.")
            return
        G = nx.DiGraph()
        G.add_nodes_from(storage.nodes)
        G.add_edges_from(storage.edges)
        plt.figure(figsize=(10, 6))
        try:
            pos = nx.spring_layout(G)
            # * Есть разные методы layout, в теории потом можно будет использовать nx.multipartite_layout(),
            # * который послойно будет отображать ноды, т.е. можно отображать что-то наподобии этапов
            # * pos = nx.multipartite_layout(G, subset_key="layer")
            # * или можно использовать тот же spring_layout, но с параметрами для большего расстояния между нодами:
            # * n = G.number_of_nodes()
            # * nx.spring_layout(G, k=1 / (n**0.0625), iterations=100, scale=2)
            colors = nx.get_edge_attributes(G, "color").values()
            labels = nx.get_edge_attributes(G, "operation")
            nx.draw(
                G,
                pos,
                with_labels=True,
                node_color="lightblue",
                edge_color=colors,
                font_size=10,
                node_size=2000,
            )
            nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
            if title:
                plt.title(title)  # ! window still being named as Figure 1
                # plt.gcf().canvas.manager.set_window_title(title) # was working (at least on Windows)
            plt.show()
        except Exception as e:
            print(f"Error visualizing graph: {e}")
            print(
                "You may need to run this in an environment that supports matplotlib display."
            )
