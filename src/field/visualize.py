import networkx as nx
from typing import Optional
from matplotlib import pyplot as plt
from base.storage import GraphStorage
from base.visualize import GraphVisualizer
from logger_config import logger


class ColumnVisualizer(GraphVisualizer):
    """Визуализатор графов зависимостей между колонками таблиц.

    Наследует функциональность GraphVisualizer и добавляет:
        - Интерактивное отображение информации о колонках при клике
        - Расширенную стилизацию для операций с колонками
        - Автоматическое определение стилей соединений для мультиграфов

    Attributes:
        Наследует все атрибуты GraphVisualizer
    """

    def render(
        self, storage: GraphStorage, title: Optional[str] = None, output_path=None
    ):
        """Визуализирует граф зависимостей с возможностью интерактивного взаимодействия.

        Args:
            storage (GraphStorage): Хранилище с данными графа
            title (str, optional): Заголовок графа. По умолчанию None
            output_path (str, optional): Путь для сохранения изображения. Пример: "output/graph.png"

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

        if not storage.nodes:
            logger.warning("Graph is empty, no dependencies to display")
            return
        G = nx.MultiDiGraph()
        G.add_nodes_from(storage.nodes)
        G.add_edges_from(storage.edges)
        plt.figure(figsize=(12, 8))
        fig = plt.gcf()
        ax = plt.gca()
        try:
            pos = nx.spring_layout(G, k=0.5, iterations=50)  # Улучшаем layout

            # Получаем цвета рёбер
            edge_colors = [
                data["color"] for u, v, k, data in G.edges(keys=True, data=True)
            ]

            # Получаем стиль рёбер, иначе solid по умолчанию
            edge_style = [
                data.get("style", "solid")
                for u, v, k, data in G.edges(keys=True, data=True)
            ]

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
                    if columns_parsed[0] is not None and len(columns_parsed[0]) > 0:
                        info = "Columns "
                        if "JOIN" in columns_parsed[0][0]:
                            info = "Joined\n  "
                            columns_parsed[0][0] = columns_parsed[0][0].replace(
                                "JOIN", ""
                            )
                        elif ":" in columns_parsed[0][0]:
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

            # Save or show
            if output_path:
                plt.savefig(output_path, format="png", dpi=300, bbox_inches="tight")
                logger.info(f"Graph saved to {output_path}")
            else:
                plt.tight_layout()
                plt.show()

            plt.close()
            logger.debug("Graph rendering completed")
        except Exception as e:
            logger.error(
                f"Error visualizing graph: {e}\nYou may need to run this in an environment that supports matplotlib display."
            )
