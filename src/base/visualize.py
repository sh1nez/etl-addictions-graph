import networkx as nx
from typing import Optional
from matplotlib import pyplot as plt
from base.storage import GraphStorage


class GraphVisualizer:
    """Class for visualizing dependency graphs."""

    def render(self, storage: GraphStorage, title: Optional[str] = None):
        if not storage.nodes:
            print("Graph is empty, no dependencies to display.")
            return
        G = nx.MultiDiGraph()
        G.add_nodes_from(storage.nodes)
        G.add_edges_from(storage.edges)
        plt.figure(figsize=(12, 8))
        try:
            pos = nx.spring_layout(G, k=0.5, iterations=50)  # Улучшаем layout

            # Получаем цвета рёбер
            edge_colors = [data["color"] for u, v, data in G.edges(data=True)]

            # Подготовка меток для рёбер
            edge_labels = {
                (u, v, k): d["operation"]
                for u, v, k, d in G.edges(keys=True, data=True)
            }

            # насколько одна связь отдаляется от другой
            step = 0.1
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
                arrowsize=15,
                connectionstyle=connectionstyle,
            )
            nx.draw_networkx_edge_labels(
                G,
                pos,
                edge_labels=edge_labels,
                font_size=9,
                connectionstyle=connectionstyle,
            )

            if title:
                plt.title(title)
            plt.tight_layout()
            plt.show()
        except Exception as e:
            print(f"Error visualizing graph: {e}")
            print(
                "You may need to run this in an environment that supports matplotlib display."
            )
