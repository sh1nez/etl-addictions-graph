import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from typing import Optional
from base.storage import GraphStorage
from logger_config import logger


class GraphVisualizer:
    """Class for visualizing dependency graphs."""

    def render(
        self,
        storage: GraphStorage,
        title: Optional[str] = None,
        save_path: Optional[str] = None,
        figsize: tuple = (20, 16),
        seed: Optional[int] = 42,
        central_spread: float = 2.0,
        peripheral_spread: float = 1.5,
    ):
        if not storage.nodes:
            logger.warning("Graph is empty, no dependencies to display")
            return

        # Создаем направленный мультиграф
        G = nx.MultiDiGraph()
        G.add_nodes_from(storage.nodes)
        G.add_edges_from(
            (
                u,
                v,
                {
                    "operation": data.get("operation", "UNKNOWN"),
                    "color": data.get("color", "black"),
                },
            )
            for u, v, data in storage.edges
        )
        logger.debug(
            f"Created graph with {len(G.nodes())} nodes and {len(G.edges())} edges"
        )

        # Классификация узлов
        central_nodes = [
            n for n in G.nodes() if G.in_degree(n) > 0 and G.out_degree(n) > 0
        ]
        peripheral_nodes = [n for n in G.nodes() if n not in central_nodes]

        # Логирование классификации
        logger.debug(
            f"Central nodes: {len(central_nodes)}, Peripheral nodes: {len(peripheral_nodes)}"
        )

        # Обработка крайних случаев
        if not central_nodes:
            logger.warning("No central nodes found, using all nodes as central")
            central_nodes = list(G.nodes())
            peripheral_nodes = []
        elif not peripheral_nodes:
            logger.warning("No peripheral nodes found, using spring layout")
            if seed is not None:
                np.random.seed(seed)
            pos = nx.spring_layout(G, k=0.2, iterations=150, seed=seed)
        else:
            # Начальное радиальное расположение
            if seed is not None:
                np.random.seed(seed)
            pos = nx.shell_layout(G, nlist=[central_nodes, peripheral_nodes])

            # Увеличение расстояния между центральными узлами
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

            # Увеличение расстояния между периферийными узлами
            for node in peripheral_nodes:
                x, y = pos[node]
                norm = np.sqrt(x**2 + y**2)
                if norm > 0:
                    pos[node] = (x * peripheral_spread, y * peripheral_spread)

        # Настройка визуальных параметров
        node_sizes = [1200 if n in central_nodes else 800 for n in G.nodes()]
        node_colors = ["lightblue" for n in G.nodes()]  # Восстановлен изначальный цвет
        edge_colors = [data["color"] for _, _, data in G.edges(data=True)]
        edge_labels = {(u, v): data["operation"] for u, v, data in G.edges(data=True)}

        # Настройка холста
        plt.figure(figsize=figsize)

        # Отрисовка графа
        nx.draw(
            G,
            pos,
            with_labels=True,
            node_color=node_colors,
            edge_color=edge_colors,
            node_size=node_sizes,
            font_size=8,
            arrows=True,
            arrowsize=15,
            connectionstyle="arc3,rad=0.1",
        )
        nx.draw_networkx_edge_labels(
            G, pos, edge_labels=edge_labels, font_size=7, label_pos=0.5
        )

        # Добавление заголовка
        if title:
            plt.title(title)

        # Оптимизация отступов
        plt.tight_layout()
        logger.info(f"Rendering graph: {title or 'Untitled'}")

        # Сохранение и отображение
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            logger.info(f"Graph saved to {save_path}")
        plt.show()
        logger.debug("Graph displayed successfully")
