Модули для field режима
==================================

Описание компонентов field режима

**Взаимодействие компонентов**

Анализ данных:
 columns.py → Парсит SQL → Извлекает зависимости на уровне колонок.

 run.py → Передаёт данные в ColumnStorage.

Хранение:
 ColumnStorage → Сохраняет узлы и рёбра с метаданными.

Визуализация:
 ColumnVisualizer → Принимает ColumnStorage → Строит интерактивный граф.

Запуск:
 Пользователь → Задаёт параметры через CLI → run.py → Координирует весь процесс.


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   columns
   field_run
   field_storage
   field_visualizer
