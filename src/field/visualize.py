import networkx as nx
from typing import Optional
from matplotlib import pyplot as plt
from base.storage import GraphStorage


class ColumnVisualizer:
    """Class for visualizing dependency graphs."""

    def render(self, storage: GraphStorage, title: Optional[str] = None):
        if not storage.nodes:
            print("Graph is empty, no dependencies to display.")
            return
        G = nx.MultiDiGraph()
        # temp_nodes = set()
        # temp_edges = []
        # for edge in storage.edges: # Display only Insert COL pairs
        #     if edge[2].get("operation") == "Insert":
        #         columns = edge[2].get("columns", None)
        #         if columns is None: continue
        #         # for col in columns[0]:
        #         #     temp_edges.append((edge[0],edge[1],{"columns":col, "color":"red"}))
        #         temp_edges.append((edge[0],edge[1],{"operation":"Insert", "columns":"\n".join(columns[0]), "color":"red"}))
        #         temp_nodes.add(edge[0])
        #         temp_nodes.add(edge[1])
        # G.add_nodes_from(temp_nodes)
        # G.add_edges_from(temp_edges)
        G.add_nodes_from(storage.nodes)
        G.add_edges_from(storage.edges)
        plt.figure(figsize=(12, 8))
        fig = plt.gcf()
        ax = plt.gca()
        try:
            pos = nx.spring_layout(G, k=0.5, iterations=50)  # Улучшаем layout

            # Получаем цвета рёбер
            edge_colors = [data["color"] for u, v, data in G.edges(data=True)]

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
            label_list = nx.draw_networkx_edge_labels(
                G,
                pos,
                edge_labels=edge_labels,
                font_size=9,
                connectionstyle=connectionstyle,
            )
            for txt in label_list.values():
                txt.set_picker(5)

            last_ann = None

            def on_pick(event):
                nonlocal last_ann
                label = event.artist  # Text-лейбл, на который кликнули

                # удаляем предыдущую аннотацию
                if last_ann is not None:
                    last_ann.remove()
                    last_ann = None

                # находим ключ ребра и атрибуты
                u, v, k = next(key for key, val in label_list.items() if val is label)
                attrs = G.edges[u, v, k]
                columns_parsed = attrs.get("columns", None)
                info = ""
                if columns_parsed is not None:
                    if columns_parsed[0] is not None and len(columns_parsed[0]) > 1:
                        info = "Columns "
                        if ":" in columns_parsed[0][0]:
                            info += "to:from\n"
                        else:
                            info += "to\n"
                        info += "\n".join(columns_parsed[0])
                    if columns_parsed[1] is not None and len(columns_parsed[1]) > 1:
                        info += "Where columns\n"
                        info += "\n".join(columns_parsed[1])

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

            if title:
                plt.title(title)
            # plt.tight_layout()
            plt.show()
        except Exception as e:
            print(f"Error visualizing graph: {e}")
            print(
                "You may need to run this in an environment that supports matplotlib display."
            )
