import networkx as nx
from typing import Optional
from matplotlib import pyplot as plt
from storage import GraphStorage


class GraphVisualizer:
    """Class for visualizing dependency graphs."""

    def render(
        self,
        storage: GraphStorage,
        title: Optional[str] = None,
        edge_widths: Optional[list] = None,
    ):  # Добавлен параметр edge_widths
        if not storage.nodes:
            print("Graph is empty, no dependencies to display.")
            return
        G = nx.DiGraph()
        G.add_nodes_from(storage.nodes)
        G.add_edges_from(storage.edges)
        plt.figure(figsize=(12, 8))
        try:
            pos = nx.spring_layout(G, k=0.5, iterations=50)  # Улучшаем layout

            # Получаем цвета рёбер
            edge_colors = [data["color"] for u, v, data in G.edges(data=True)]

            # Подготовка меток для рёбер
            edge_labels = {}
            for u, v, data in G.edges(data=True):
                # Берем только имя операции без деталей
                label = data.get("operation", "")
                edge_labels[(u, v)] = label

            # Определяем толщину линий
            if edge_widths is None:
                edge_widths = [1.0] * len(G.edges)  # По умолчанию толщина 1.0

            # Отрисовка графа
            nx.draw(
                G,
                pos,
                with_labels=True,
                node_color="lightblue",
                edge_color=edge_colors,
                width=edge_widths,  # Используем толщину линий
                font_size=10,
                node_size=2000,
                arrows=True,
                arrowsize=15,
            )
            nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=9)

            if title:
                plt.title(title)
            plt.tight_layout()
            plt.show()
        except Exception as e:
            print(f"Error visualizing graph: {e}")
            print(
                "You may need to run this in an environment that supports matplotlib display."
            )
