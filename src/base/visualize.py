from collections import defaultdict
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from typing import Optional
from base.storage import GraphStorage
from logger_config import logger
from matplotlib.patches import FancyArrowPatch


class GraphVisualizer:
    """Визуализирует графы зависимостей на основе данных из GraphStorage.

    Attributes:
        Нет публичных атрибутов. Все параметры передаются в метод render.

    Example:
        >>> storage = GraphStorage()
        >>> visualizer = GraphVisualizer()
        >>> visualizer.render(storage, title="Пример графа", save_path="graph.png")
    """

    ALPHA_HIDDEN = 0.1  # alpha for hidden elements
    MULTIEDGE_LIM = 10  # max arrows displayed between graphs
    ARROWS_DIST = 0.1  # distance between arrows of the same nodes
    LIMIT_SELFLOOPS = True
    LIMIT_MULTIEDGES = True

    def __init__(self):
        self.G = None
        self.pos = None

        self.node_connections = {}
        self.node_coll = None
        self.edge_artists = []
        self.edge_artist_map = {}
        self.node_labels = {}
        self.edge_label_texts = {}
        self.nodes_list = []
        self.pressed = None

        # вывод нескольких стрелок между двумя нодами, их расположение
        self.connectionstyle = [
            f"arc3,rad={(-1)**(i+1)*((i+1)//2*self.ARROWS_DIST)}"
            for i in range(self.MULTIEDGE_LIM)
        ]
        # для edge label выделяющая рамка
        self.thin_box = dict(boxstyle="round", ec="white", fc="white", linewidth=0.5)
        self.empty_bbox = dict(ec="none", fc="none")

        self.fig = None
        self.ax = None
        # self.fig, self.ax = plt.subplots(figsize=(14, 10))
        # self.fig.canvas.mpl_connect("pick_event", self._on_pick)
        logger.debug("GraphVisualizer initialized")

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
        """Визуализирует граф зависимостей и отображает/сохраняет результат.

        Args:
            storage (GraphStorage): Хранилище с данными графа.
            title (str, optional): Заголовок графа. По умолчанию None.
            save_path (str, optional): Путь для сохранения изображения. Пример: "output/graph.png".
            figsize (tuple): Размер холста в дюймах. По умолчанию (20, 16).
            seed (int, optional): Seed для воспроизводимости расположения узлов.
            central_spread (float): Коэффициент расстояния между центральными узлами.
            peripheral_spread (float): Коэффициент расстояния для периферийных узлов.

        Returns:
            None

        Raises:
            ValueError: Если передан пустой storage.

        Example:
            >>> # Базовая визуализация
            >>> visualizer.render(storage)

            >>> # Кастомизация параметров
            >>> visualizer.render(storage, title="Data Pipeline", save_path="pipeline.png", figsize=(15, 10), seed=123, central_spread=3.0)
        """
        self.pressed = None
        self.fig, self.ax = plt.subplots(figsize=figsize)
        self.fig.canvas.mpl_connect("pick_event", self._on_pick)
        nodes, edges = storage.get_filtered_nodes_edges()

        if not storage.nodes:
            logger.warning("Graph is empty, no dependencies to display")
            return

        if self.LIMIT_SELFLOOPS:
            edges = self._limit_self_loops(edges)
        if self.LIMIT_MULTIEDGES:
            edges = self._limit_connections(edges)
        self.G = nx.MultiDiGraph()
        self.G.add_nodes_from(nodes)
        self.G.add_edges_from(edges)
        logger.debug(
            f"Created graph with {self.G.number_of_nodes()} nodes and {self.G.number_of_edges()} edges"
        )

        # Классификация узлов
        central_nodes = [
            n
            for n in self.G.nodes()
            if self.G.in_degree(n) > 0 and self.G.out_degree(n) > 0
        ]
        peripheral_nodes = [n for n in self.G.nodes() if n not in central_nodes]

        logger.debug(
            f"Central nodes: {len(central_nodes)}, Peripheral nodes: {len(peripheral_nodes)}"
        )

        # Обработка крайних случаев
        if not central_nodes:
            logger.warning("No central nodes found, using all nodes as central")
            central_nodes = list(self.G.nodes())
            peripheral_nodes = []
            # added pos handling for no central nodes
            self.pos = nx.spring_layout(self.G, k=0.2, iterations=50, seed=seed)
        elif not peripheral_nodes:
            logger.warning("No peripheral nodes found, using spring layout")
            if seed is not None:
                np.random.seed(seed)
            self.pos = nx.spring_layout(self.G, k=0.2, iterations=150, seed=seed)
        else:
            # Начальное радиальное расположение
            if seed is not None:
                np.random.seed(seed)
            self.pos = nx.shell_layout(self.G, nlist=[central_nodes, peripheral_nodes])

            # Увеличение расстояния между центральными узлами
            if len(central_nodes) > 1:
                central_subgraph = self.G.subgraph(central_nodes)
                central_pos = nx.spring_layout(
                    central_subgraph,
                    k=central_spread / np.sqrt(len(central_nodes)),
                    iterations=50,
                    seed=seed,
                )
                for node in central_nodes:
                    self.pos[node] = central_pos[node]

            # Увеличение расстояния между периферийными узлами
            for node in peripheral_nodes:
                x, y = self.pos[node]
                norm = np.sqrt(x**2 + y**2)
                if norm > 0:
                    self.pos[node] = (x * peripheral_spread, y * peripheral_spread)

        # настройка визуальных параметров
        edge_colors = [
            data["color"] for u, v, k, data in self.G.edges(keys=True, data=True)
        ]
        # * Изначальные параметры Edge(is_internal_update, is_recursive) перестали
        # * где-либо задаваться, поэтому комментарию. Когда-то is_internal_update
        # * задавался при парсинге внутрренних Update, а is_recursive=False
        # edge_style = [
        #     data.get("style", "solid")
        #     for u, v, k, data in self.G.edges(keys=True, data=True)
        # ]
        node_sizes = [1200 if n in central_nodes else 800 for n in self.G.nodes()]
        # отрисовка операций(подписей рёбер)
        edge_labels = {
            (u, v, k): d["operation"]
            for u, v, k, d in self.G.edges(keys=True, data=True)
        }

        # отрисовка графа
        nx.draw(
            self.G,
            self.pos,
            ax=self.ax,
            with_labels=False,
            node_color="lightblue",
            edge_color=edge_colors,
            node_size=node_sizes,
            arrows=True,
            arrowstyle="->",
            arrowsize=15,
            connectionstyle=self.connectionstyle,
            # style=edge_style,
        )

        self.edge_label_texts = nx.draw_networkx_edge_labels(
            self.G,
            self.pos,
            edge_labels=edge_labels,
            font_size=9,
            connectionstyle=self.connectionstyle,
            bbox=self.thin_box,
            ax=self.ax,
        )

        self.node_coll = self.ax.collections[0]
        self.edge_artists = [
            p for p in self.ax.patches if isinstance(p, FancyArrowPatch)
        ]
        edge_keys = list(self.G.edges(keys=True))
        self.edge_artist_map = dict(zip(self.edge_artists, edge_keys))

        self.node_labels = nx.draw_networkx_labels(
            self.G, self.pos, ax=self.ax, font_size=10
        )
        self.nodes_list = list(self.G.nodes())
        self.node_connections = {
            n: set(self.G.successors(n))  # исходящие
            | set(self.G.predecessors(n))  # входящие
            | {n}  # сама вершина
            for n in self.G.nodes()
        }
        for txt in self.node_labels.values():
            txt.set_picker(5)

        # Set title
        plt.title(title or "SQL Dependency Graph")
        plt.axis("off")

        # Save or show
        if save_path:
            plt.savefig(save_path, format="png", dpi=300, bbox_inches="tight")
            logger.info(f"Graph saved to {save_path}")
        else:
            plt.tight_layout()
            plt.show()

        plt.close()
        logger.debug("Graph rendering completed")

    def _on_pick(self, event):
        art = event.artist
        # реагируем только на полностью непрозрачные текст-лейблы нод
        if art not in self.node_labels.values() or (
            art.get_alpha() is not None and art.get_alpha() != 1.0
        ):
            return

        node = art.get_text()

        # сброс если та же нода
        if self.pressed == node:
            self._reset_alpha()
            self.pressed = None
        else:
            self.pressed = node
            self._highlight(node)

        event.canvas.draw_idle()

    def _reset_alpha(self):
        alphas = [1.0] * self.G.number_of_nodes()
        self.node_coll.set_alpha(alphas)
        for p in self.edge_artists:
            p.set_alpha(1.0)
        for txt in self.node_labels.values():
            txt.set_alpha(1.0)
        for txt in self.edge_label_texts.values():
            txt.set_alpha(1.0)
            txt.set_bbox(self.thin_box)

    def _highlight(self, node):
        active = self.node_connections[node]

        # узлы
        alphas = [1.0 if n in active else self.ALPHA_HIDDEN for n in self.nodes_list]
        self.node_coll.set_alpha(alphas)

        # рёбра
        for patch in self.edge_artists:
            u, v, k = self.edge_artist_map[patch]
            patch.set_alpha(1.0 if (u in active and v in active) else self.ALPHA_HIDDEN)

        # подписи нод
        for n, txt in self.node_labels.items():
            txt.set_alpha(1.0 if n in active else self.ALPHA_HIDDEN)

        # подписи рёбер
        for (u, v, k), txt in self.edge_label_texts.items():
            txt.set_alpha(1.0 if (u in active and v in active) else self.ALPHA_HIDDEN)
            txt.set_bbox(
                self.thin_box if (u in active and v in active) else self.empty_bbox
            )

    def _limit_self_loops(self, edges, max_loops=4, only_uniq_op=False):
        """
        почему max_loops == 4:
        Для каждого узла (u == v) оставляем не более четырёх петель
        (больше nx и matplotlib не отображает, если не переопределять библиотечные настройки)
        https://stackoverflow.com/q/74350464

        only_uniq_op:
        * True - первые четыре операции
        * False - четыре разные операции
        """
        loops = defaultdict(set) if only_uniq_op else defaultdict(int)
        new_edges = []
        for u, v, data in edges:
            if u == v:
                if only_uniq_op:
                    op = data.get("operation")
                    if op not in loops[u] and len(loops[u]) < max_loops:
                        new_edges.append((u, v, data))
                        loops[u].add(op)
                else:
                    if loops[u] < max_loops:
                        new_edges.append((u, v, data))
                        loops[u] += 1
            else:
                new_edges.append((u, v, data))
        return new_edges

    def _limit_connections(self, edges):
        """
        edges: iterable кортежей (u, v, data_dict)
        max_per_pair: максимально оставить рёбер для каждой упорядоченной пары (u,v)
        возвращает отфильтрованный список рёбер
        """
        counts = defaultdict(int)
        filtered = []
        for u, v, data in edges:
            key = (u, v)
            if counts[key] < self.MULTIEDGE_LIM:
                filtered.append((u, v, data))
                counts[key] += 1
        return filtered
