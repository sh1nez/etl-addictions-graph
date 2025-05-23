import networkx as nx
from typing import Optional
from matplotlib import pyplot as plt
import numpy as np
from base.storage import GraphStorage
from base.visualize import GraphVisualizer
from logger_config import logger
from matplotlib.patches import FancyArrowPatch


class ColumnVisualizer(GraphVisualizer):
    """Визуализатор графов зависимостей между колонками таблиц.

    Наследует функциональность GraphVisualizer и добавляет:
        - Интерактивное отображение информации о колонках при клике
        - Расширенную стилизацию для операций с колонками
        - Автоматическое определение стилей соединений для мультиграфов

    Attributes:
        Наследует все атрибуты GraphVisualizer
    """

    def __init__(self):
        self.pressed_edge = None
        self.last_uv = ()
        self.last_ann = None
        super().__init__()

    def render(
        self,
        storage: GraphStorage,
        title: Optional[str] = None,
        save_path=None,
        figsize: tuple = (20, 16),
        seed: Optional[int] = 42,
        central_spread: float = 2.0,
        peripheral_spread: float = 1.5,
    ):
        """Визуализирует граф зависимостей с возможностью интерактивного взаимодействия.

        Args:
            storage (GraphStorage): Хранилище с данными графа
            title (str, optional): Заголовок графа. По умолчанию None
            save_path (str, optional): Путь для сохранения изображения. Пример: "output/graph.png"
            figsize (tuple): Размер холста в дюймах. По умолчанию (20, 16).
            seed (int, optional): Seed для воспроизводимости расположения узлов.
            central_spread (float): Коэффициент расстояния между центральными узлами.
            peripheral_spread (float): Коэффициент расстояния для периферийных узлов.

        Raises:
            RuntimeError: Если визуализация невозможна в текущем окружении
            ValueError: При передаче некорректных данных

        Example:
            >>> storage = ColumnStorage()
            >>> visualizer = ColumnVisualizer()
            >>> visualizer.render(storage, title="User Columns", output_path="graph.png")

        Особенности реализации:
            - Использует spring_layout с параметрами k=0.5 и iterations=50
            - Поддерживает до 10 соединений между узлами с автоматическим смещением
            - Реализует интерактивные подсказки с информацией о колонках:
              * ЛКМ по ребру -> отображение связанных колонок
              * Повторный клик -> скрытие подсказки
        """
        self.pressed = None
        self.last_uv = ()
        self.last_ann = None
        self.pressed_edge = None
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

        # стиль рёбер
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

        # Отрисовка графа
        nx.draw(
            self.G,
            self.pos,
            ax=self.ax,
            with_labels=False,
            node_color="lightblue",
            edge_color=edge_colors,
            node_size=node_sizes,
            arrows=True,
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
        for txt in self.edge_label_texts.values():
            txt.set_picker(5)

        plt.title(title or "SQL Dependency Graph with columns")
        plt.axis("off")

        # Save or show
        if save_path:
            plt.savefig(save_path, format="png", dpi=300, bbox_inches="tight")
            logger.info(f"Graph saved to {save_path}")
        else:
            plt.tight_layout()
            plt.show()

        plt.close()

    def _on_pick(self, event):
        if event.artist in self.edge_label_texts.values():
            self._columns_display(event)
        else:
            art = event.artist
            if (
                art in self.node_labels.values()
                and art.get_alpha() == 1.0
                and self.last_ann is not None
            ):
                conn = self.node_connections[art.get_text()]
                if not all(uv in conn for uv in self.last_uv):
                    self.last_ann.remove()
                    self.last_ann = None
                    self.last_uv = ()
                    self.pressed_edge = None
            super()._on_pick(event)

    def _columns_display(self, event):
        label = event.artist
        if label.get_alpha() is not None and label.get_alpha() != 1.0:
            return  # не работаем с (полу)прознычными

        same = self.pressed_edge == label
        # удаляем предыдущую аннотацию
        if self.last_ann is not None:
            self.last_ann.remove()
            self.last_ann = None
            self.last_uv = ()
            self.pressed_edge = None

        if same:
            event.canvas.draw_idle()
            return

        # находим ключ ребра и атрибуты
        u, v, k = next(
            key for key, val in self.edge_label_texts.items() if val is label
        )
        attrs = self.G.edges[u, v, k]
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
        self.last_ann = self.ax.annotate(
            info,
            xy=(x, y),
            xycoords="data",
            xytext=(20, 20),
            textcoords="offset points",
            bbox=dict(boxstyle="round,pad=0.3", alpha=0.8),
            arrowprops=dict(arrowstyle="->"),
        )
        self.last_uv = (u, v)
        self.pressed_edge = label
        event.canvas.draw_idle()
