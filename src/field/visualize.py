import networkx as nx
from typing import Optional
from matplotlib import pyplot as plt
from base.storage import GraphStorage
from base.visualize import GraphVisualizer
from logger_config import logger
from matplotlib.patches import FancyArrowPatch


class ColumnVisualizer(GraphVisualizer):
    """Class for visualizing dependency graphs."""

    def __init__(self):
        self.pressed_edge = None
        self.last_uv = ()
        self.last_ann = None
        super().__init__()

    def render(
        self,
        storage: GraphStorage,
        title: Optional[str] = None,
        output_path=None,
        sep: bool = False,
    ):
        if not storage.nodes:
            logger.warning("Graph is empty, no dependencies to display")
            return

        edges = storage.edges
        if self.LIMIT_SELFLOOPS:
            edges = self._limit_self_loops(edges)
        if self.LIMIT_MULTIEDGES:
            edges = self._limit_connections(edges)
        self.G = nx.MultiDiGraph()
        self.G.add_nodes_from(storage.nodes)
        self.G.add_edges_from(edges)
        self.pos = nx.spring_layout(self.G, k=0.95, iterations=50)

        if sep:
            plt.close()
            self.pressed = None
            self.last_uv = ()
            self.last_ann = None
            self.pressed_edge = None
            self.fig, self.ax = plt.subplots(figsize=(14, 10))
            self.fig.canvas.mpl_connect("pick_event", self._on_pick)

        # стиль рёбер
        self.edge_colors = [
            data["color"] for u, v, k, data in self.G.edges(keys=True, data=True)
        ]
        self.edge_style = [
            data.get("style", "solid")
            for u, v, k, data in self.G.edges(keys=True, data=True)
        ]
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
            edge_color=self.edge_colors,
            node_size=2000,
            arrows=True,
            arrowsize=15,
            connectionstyle=self.connectionstyle,
            style=self.edge_style,
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
        if output_path:
            plt.savefig(output_path, format="png", dpi=300, bbox_inches="tight")
            logger.info(f"Graph saved to {output_path}")
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
